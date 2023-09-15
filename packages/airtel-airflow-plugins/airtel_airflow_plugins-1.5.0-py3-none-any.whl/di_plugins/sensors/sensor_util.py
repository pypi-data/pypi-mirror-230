import paramiko

from airflow.models.connection import Connection
from airflow.exceptions import AirflowSkipException
from datetime import datetime, timedelta
from pendulum.tz.timezone import Timezone
from airflow.models import Variable


def get_directory_status(params, cmd, pending_files):
    """
    this method executes shell command to get file/directory status.
    it parses shell command console output to  determine pending and done files

    it returns done and pending files
    """
    try:
        conn = Connection.get_connection_from_secrets(params["ssh_conn_id"])

        detailed_log = params.get("detailed_log", "no")
        if detailed_log == "yes":
            print(f"executing command over ssh - {cmd}")

        with paramiko.SSHClient() as ssh_client:
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh_client.connect(hostname=conn.host,
                               port=conn.port,
                               username=conn.login,
                               password=conn.password,
                               timeout=params.get("timeout", None),
                               banner_timeout=params.get("banner_timeout", None),
                               auth_timeout=params.get("auth_timeout", None),
                               )
            stdin, stdout, stderr = ssh_client.exec_command(command=cmd,
                                                            timeout=params.get("timeout", None))

            out = stdout.read().decode().strip()

            if detailed_log == "yes":
                print(f"command log - {out}")

            pending_files = filter(lambda element: element.startswith("PENDING >>"), out.split("\n"))
            done_files = filter(lambda element: element.startswith("DONE >>"), out.split("\n"))

            recv_exit_status = stdout.channel.recv_exit_status()

            ssh_client.close()
            # print(recv_exit_status)
            if recv_exit_status == 0:
                return (list(map(lambda d: d[len("DONE >> "):].strip(), done_files)),
                        list(map(lambda d: d[len("PENDING >> "):].strip(), pending_files)))
            else:
                error = stderr.read().decode().strip()
                print(f"script output - {out}")
                print(f"script exit status code - {recv_exit_status}, error output - {error}")
                raise Exception(f"command {cmd} exit with code {recv_exit_status}")

    except Exception as ex:
        if "error reading ssh protocol banner" in (str(ex)).lower():
            print(f"Catching Exception: {str(ex)}")
            done_files = []
            return done_files, pending_files

        else:
            print(f"Exception occurred: {str(ex)}")
            raise ex


def sense_objects(fs_type: str, param: dict, pending_files: list):
    """
    this method validates directory status as per the file system
    :param fs_type: file system type
    :param param: parameters
    :param pending_files: initial pending files
    :return: directory status
    """
    if pending_files is None:
        """initialize pending_files"""
        print("***** init pending files *****")
        pending_files = list(map(lambda path: path.strip(), param["objects"]))
        print(pending_files)

    cmd_file_str = ','.join(pending_files)
    """shell command to execute"""
    cmd = f'sh {param["script"]} -ol "{cmd_file_str}" -fs {fs_type} -ot {param.get("object_type", "file")}'

    return get_directory_status(param, cmd, pending_files)


def check_skipped(start_date, skip_after_minutes=1440, skip_enable=True, variable_to_delete=None):
    """
    this method check if difference between start_date and current time is more than skip_after_minutes and throws
    AirflowSkipException if skip_enable is true
    :param variable_to_delete:
    :param start_date: start date
    :param skip_after_minutes: duration in minutes
    :param skip_enable: flag to enable/disable
    """
    total_minutes = int((datetime.now(Timezone('UTC')) - start_date).total_seconds() / 60)
    if total_minutes > skip_after_minutes and skip_enable:
        if variable_to_delete is not None:
            Variable.delete(variable_to_delete)

        raise AirflowSkipException(
            f"task is running from {total_minutes} minutes which is > {skip_after_minutes} minutes")
