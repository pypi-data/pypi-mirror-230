from typing import Any
from airflow.exceptions import AirflowException
from airflow.models.connection import Connection

from di_plugins.sensors.ssh_sensor import SSHSensor

class JobMonitorSSHSensor(SSHSensor):

    template_fields = ['op_kwargs', 'operator_command']

    def __init__(
            self,
            venv,
            op_kwargs,
            app_type,
            app_name,
            db_conn_id,
            cluster_url,
            operator_command,
            operator_kill_command,
            keytab_file,
            principal,
            **kwargs
        ):
        super().__init__(environment={"TERM": "xterm"}, **kwargs)
        self.op_kwargs = op_kwargs
        self.app_type = app_type
        self.app_name = app_name
        self.venv = venv
        self.cluster_url = cluster_url
        self.keytab_file = keytab_file
        self.principal = principal
        self.db_conn_id = db_conn_id
        self.operator_command = operator_command
        self.operator_kill_command = operator_kill_command


    def _get_db_url(self, db_conn_id):
        conn = Connection.get_connection_from_secrets(conn_id=db_conn_id, )
        extra = conn.extra_dejson
        conn_str = f"{extra.get('client')}://{conn.login}:{conn.password}@{conn.host}:{conn.port}/?service_name={extra.get('service_name')}"
        return conn_str

    def _validate_command(self, cmd:str):
        if cmd.find("$") >= 0:
            raise AirflowException(f"commands cannot contain variable substitution from shell. command: {cmd}")


    def _escape_quotes(self, command:str) -> str:
        cmd = (
            command
            .replace('"', '\\"')
            # .replace(";", "\\;")
        )
        self.log.info("esacped command: %s", cmd)
        return cmd
    
    def execute(self, context: Any):
        db_url = self._get_db_url(self.db_conn_id)
        self._validate_command(self.operator_command)
        self._validate_command(self.operator_kill_command)
        operator_command = self._escape_quotes(self.operator_command)
        operator_kill_command = self._escape_quotes(self.operator_kill_command)
        self.command = f'export TERM=xterm && conda activate {self.venv} && job_automator --app-type {self.app_type} --app-name {self.app_name} --db-url {db_url} --cluster-url {self.cluster_url} --keytab {self.keytab_file} --principal {self.principal} --operator-command "{operator_command}" --operator-kill-command "{operator_kill_command}" '

        return super().execute(context)