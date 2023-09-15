from datetime import datetime, timedelta
from pendulum.tz.timezone import Timezone
from airflow import models
from pendulum import DateTime
from airflow.sensors.bash import BaseSensorOperator
import json
import requests
import logging
from airflow.models import Variable
from airflow.exceptions import AirflowException
from airflow.exceptions import AirflowSkipException
from airflow.providers.hashicorp.hooks.vault import VaultHook
from dateutil import parser
import ast
from di_plugins.sensors.sensor_util import check_skipped


class DIExternalTaskSensor(BaseSensorOperator):
    """
    DIExternalTaskSensor is a custom sensor that checks execution of target dags for a given date. It uses airflow's
    rest APIs to track dag run status.
    
    op_kwargs for this sensor ars as follows:
    source_dag_ids: ids of source dags to be monitored
    execution_summary_date: execution date of source dags
    system: system name
    env: environment
    success_statuses: dag run status that will be considered as success
    failure_statuses: dag run status that will be considered as failed
    airflow_base_url: airflow base url
    vault_conn_id: vault connection id
    vault_url: vault url
    vault_secret_path: vault secret path
    vault_mount_point: vault mount point
    vault_certificate_file: certificate file path

    This sensor first checks if a source dag will be executed for given execution_summary_date date (between 00 hours of
    execution_summary_date to 23:59:59 hours) and it stores dag run details in airflow variable whose name is
    constructed as execution_summary_{system}_{env}_{dag_run_id}.

    it stores following information of dag run in airflow variable:
    - source_dag_id: source dag id
    - source_dag_run_id: source dag run id
    - is_skipped: true if dag didn't run on execution_summary_date
    - start_date: start date of dag run
    - end_date: end date of dag run
    - dag_run_state: status of dag run

    this sensor can terminate its execution if parameter skip_enable (default is true) is set in op_kwargs and it will
    terminate its execution if it is executing after skip_after_minutes from start_date
    """
    template_fields = ['op_kwargs']
    ui_color = '#5499C7'  # type: str
    ui_fgcolor = '#000'  # type: str

    def __init__(self, *, op_kwargs, **kwargs):
        super().__init__(**kwargs)
        self.op_kwargs = op_kwargs
        
        self.logger = logging.getLogger("airflow.task")

    def get_lookup_key(self, dag_run_id):
        """
        this method creates airflow variable name in which dag run details are stored.
        variable name prefix can be set using parameter dag_status_variable_prefix (default prefix is execution_summary)

        variable name - {prefix}_{system}_{env}_{dag_run_id}
        :param dag_run_id: dag_run_id
        :return: variable name
        """
        dag_status_variable = self.op_kwargs.get('dag_status_variable_prefix','execution_summary')
        return f"{dag_status_variable}_{self.op_kwargs['system']}_{self.op_kwargs['env']}_{dag_run_id}"

    def get_dag_execution_details(self, lookup_key):
        """
        this method fetches value for airflow variable - lookup_key
        :param lookup_key: airflow variable name
        :return: value for given airflow variable
        """
        return Variable.get(key=lookup_key, deserialize_json=True, default_var=None)

    def set_dag_execution_details(self, lookup_key, data):
        """
        this method update airflow variable - lookup_key by value - data
        :param lookup_key: airflow variable
        :param data: data for airflow variable
        """
        Variable.set(key=lookup_key, value=data, serialize_json=True)

    def get_message(self, source_dag_id, source_dag_run_id=None, is_skipped=True, start_date=None, end_date=None,
                    dag_run_state=None):
        return {'source_dag_id': source_dag_id,
                'source_dag_run_id': source_dag_run_id,
                'is_skipped': is_skipped,
                'start_date': start_date,
                'end_date': end_date,
                'dag_run_state': dag_run_state
                }

    def check_execution_bw_dates(self, dag_id, dag_bag, start_date, end_date):
        """
        this method check if dag will run between given date ranges
        :param dag_id: dag id
        :param dag_bag: dag bag
        :param start_date: start date
        :param end_date: end date
        :return: true if dag runs between start_date and end_date, false otherwise
        """
        dag_object = dag_bag.get_dag(dag_id)

        if dag_object is None:
            raise AirflowException(f"dag not found for dag id - {dag_id}")

        run_dates = list(dag_object.iter_dagrun_infos_between(earliest=start_date, latest=end_date))
        self.logger.info(f"run_dates for dag - {dag_id} are - {run_dates}")
        if len(run_dates) > 0:
            return True
        else:
            return False

    def get_dag_run_range(self):
        execution_summary_date = parser.parse(self.op_kwargs['execution_summary_date'])
        start_date = DateTime(execution_summary_date.year, execution_summary_date.month, execution_summary_date.day,
                              0, 0, 0, tzinfo=Timezone('UTC'))

        end_date = DateTime(execution_summary_date.year, execution_summary_date.month, execution_summary_date.day,
                            23, 59, 59, tzinfo=Timezone('UTC'))

        return start_date, end_date

    def get_pending_source_dags(self, lookup_key):
        """
        this method gets pending dag run details.
        it work as follows:
        - get dag execution details for airflow variable
        - if execution details is None then it identifies dags that will run for given execution_summary date and is
        mark dag runs as skipped for those dags which don't run for given execution_summary date and stores the result
        in airfow variable
        - if execution details is not None then it identifies pending source dag runs

        :param lookup_key: airflow variable in which execution details are stores
        :return: dags that haven't run
        """
        self.logger.info("executing - DIExternalTaskSensor.get_pending_source_dags()")
        dag_exe_values = self.get_dag_execution_details(lookup_key)
        source_dag_ids = self.get_source_dag_ids()
        if dag_exe_values is None:
            self.logger.info(f"source_dag_ids - {source_dag_ids}")
            dag_bag = models.DagBag(read_dags_from_db=True)
            dag_bag.collect_dags_from_db()
            start_date, end_date = self.get_dag_run_range()

            current_day_dag_runs = list(filter(
                lambda source_dag_id: self.check_execution_bw_dates(source_dag_id, dag_bag, start_date, end_date),
                source_dag_ids))

            skipped_dag_ids = list(
                filter(lambda source_dag_id: source_dag_id not in current_day_dag_runs, source_dag_ids))

            dag_exe_values = {}
            for skipped_dag_id in skipped_dag_ids:
                dag_exe_values[skipped_dag_id] = self.get_message(skipped_dag_id)

            self.set_dag_execution_details(lookup_key, dag_exe_values)

            return current_day_dag_runs
        else:
            return list(filter(lambda source_dag_id: source_dag_id not in dag_exe_values.keys(), source_dag_ids))

    def get_secret_from_vault(self) -> dict:
        try:
            conn_id = self.op_kwargs['vault_conn_id']
            certificate_file = self.op_kwargs['vault_certificate_file']
            vault_url = self.op_kwargs['vault_url']
            vault_secret_path = self.op_kwargs['vault_secret_path']
            vault_mount_point = self.op_kwargs['vault_mount_point']

            vault_obj = VaultHook(conn_id)
            vault_obj.vault_client.kwargs = {'verify': certificate_file}
            vault_obj.vault_client.url = vault_url
            connection = vault_obj.get_conn()
            secret = connection.secrets.kv.v2.read_secret_version(path=vault_secret_path,
                                                                  mount_point=vault_mount_point)
            return secret

        except Exception as ex:
            self.logger.error("error occurred while getting vault secrets", ex)
            raise ex

    def get_secrets(self):
        vault_response = self.get_secret_from_vault()
        secrets = vault_response['data']['data']
        return secrets['user_name'], secrets['user_password']

    def get_dag_status(self, dag_ids):
        """
        this method gets dag run details for given dag ids
        :param dag_ids: dag ids
        :return:  dag run details
        """
        self.logger.info("executing - DIExternalTaskSensor.get_dag_status()")
        execution_date_gte, execution_date_lte = self.get_dag_run_range()
        payload = json.dumps({
            'dag_ids': dag_ids,
            'execution_date_gte': execution_date_gte.isoformat(),
            'execution_date_lte': execution_date_lte.isoformat(),
            "order_by": "-execution_date"
        })

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        api_url = f"{self.op_kwargs['airflow_base_url']}/api/v1/dags/~/dagRuns/list"
        self.logger.info(f"dag run status api - {api_url}, payload - {payload}")

        secrets = self.get_secrets()
        auth = (secrets[0], secrets[1])
        response = requests.request("POST", url=api_url, auth=auth, headers=headers, data=payload, verify=False)

        if response.status_code != 200:
            raise Exception(f"get dags run request failed with status code - {response.status_code}")

        dag_runs = response.json()['dag_runs']
        dag_state_data = []
        for dag_id in dag_ids:
            dag_states = list(filter(lambda dag_run_data: dag_run_data['dag_id'] == dag_id, dag_runs))

            if len(dag_states) == 0:
                dag_state_data.append({'dag_id': dag_id,
                                       'state': 'pending'})
            else:
                dag_state = dag_states[0]
                dag_state_data.append({'dag_id': dag_state['dag_id'],
                                       'dag_run_id': dag_state['dag_run_id'],
                                       'state': dag_state['state'],
                                       'start_date': dag_state['start_date'],
                                       'end_date': dag_state['end_date']
                                       })

        return dag_state_data

    def get_dag_data(self, dag_id, auth, base_url, headers):
        """
        this method calls airflow rest api to get details of given dag id
        :param dag_id: source dag id
        :param auth: authentication
        :param base_url: airflow base url
        :param headers: request headers
        :return: dag details
        """
        api_url = f"{base_url}/api/v1/dags/{dag_id}"
        self.logger.info(f"dag data api - {api_url}")

        response = requests.request("GET", url=api_url, auth=auth, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_source_dag_ids(self):
        """
        this method return source dag ids
        :return: source dag ids
        """
        if isinstance(self.op_kwargs['source_dag_ids'], str):
            return ast.literal_eval(self.op_kwargs['source_dag_ids'])
        else:
            return self.op_kwargs['source_dag_ids']

    def check_dag_existence(self):
        """
        this method checks if source dags exists in airflow using rest api call. This check can be enable by setting
        check_existence to true in op_kwargs. default is false
        :return:
        """
        check_existence = self.op_kwargs.get("check_existence", False)
        if check_existence:
            self.logger.info("checking dags existence")
            source_dag_ids = self.get_source_dag_ids()
            base_url = self.op_kwargs['airflow_base_url']
            headers = {
                'accept': 'application/json'
            }
            auth = self.get_secrets()
            for source_dag_id in source_dag_ids:
                dag_details = self.get_dag_data(source_dag_id, auth, base_url, headers)
                if dag_details is None:
                    raise AirflowException(f"dag not found - {source_dag_id}")

    def check_failed_dags(self, dag_run_data_list):
        """
        this method checks if it needs to throw exception of failure of source dags. this can be enabled using
        error_on_failed_dags parameter which is false by default
        :param dag_run_data_list: dag run details
        """
        error_on_failed_dags = self.op_kwargs.get("error_on_failed_dags", False)
        if error_on_failed_dags:
            failure_statuses = self.op_kwargs['failure_statuses']
            failed_dags_data = list(
                filter(lambda dag_run_data: dag_run_data['state'] in failure_statuses, dag_run_data_list))

            if len(failed_dags_data) > 0:
                failed_dag_ids = list(
                    map(lambda dag_run_data: dag_run_data['dag_id'], failed_dags_data))
                raise AirflowException(f"dags - {','.join(failed_dag_ids)} are in failed state - {failure_statuses}")

    def dag_statuses_to_compare(self):
        if isinstance(self.op_kwargs['success_statuses'], list):
            success_statuses = self.op_kwargs['success_statuses']
        else:
            success_statuses = ast.literal_eval(self.op_kwargs['success_statuses'])

        if isinstance(self.op_kwargs['failure_statuses'], list):
            failure_statuses = self.op_kwargs['failure_statuses']
        else:
            failure_statuses = ast.literal_eval(self.op_kwargs['failure_statuses'])

        return success_statuses, failure_statuses

    def update_source_dag_statuses(self, dag_run_data_list, lookup_key):
        self.logger.info("executing - DIExternalTaskSensor.update_source_dag_statuses()")
        success_statuses, failure_statuses = self.dag_statuses_to_compare()

        self.logger.info(f"success_statuses - {success_statuses}, failure_statuses - {failure_statuses}")

        processed_dags_data = list(
            filter(lambda dag_run_data: dag_run_data['state'] in success_statuses or dag_run_data[
                'state'] in failure_statuses, dag_run_data_list))

        if len(processed_dags_data) > 0:
            dag_exe_existing_values = self.get_dag_execution_details(lookup_key)
            for dag_data in processed_dags_data:
                dag_exe_existing_values[dag_data['dag_id']] = self.get_message(source_dag_id=dag_data['dag_id'],
                                                                               source_dag_run_id=dag_data['dag_run_id'],
                                                                               is_skipped=False,
                                                                               start_date=dag_data['start_date'],
                                                                               end_date=dag_data['end_date'],
                                                                               dag_run_state=dag_data['state']
                                                                               )

            self.set_dag_execution_details(lookup_key, dag_exe_existing_values)

        pending_dags_data = list(
            filter(lambda dag_run_data: dag_run_data['state'] not in success_statuses and dag_run_data[
                'state'] not in failure_statuses, dag_run_data_list))

        return pending_dags_data

    def poke(self, context):
        """
        this method is called by airflow framework after every poke_interval

        it does following:
        -check if sensor execution is to be terminated
        -check if it has to validate existence of source dags

        - gets all source dags which are not executed
        - gets dag run status for these pending dags using airflow rest apis
        - update dag run status in airflow variable

        if there are no pending source dag run then it returns true otherwise it returns false
        :param context:
        :return:
        """
        self.logger.info("executing - DIExternalTaskSensor.poke()")
        lookup_key = self.get_lookup_key(context['run_id'])
        
        is_skip_enable = self.op_kwargs.get('skip_enable', False)
        skip_enable = (isinstance(is_skip_enable, bool) and is_skip_enable is True) or (
                isinstance(is_skip_enable, str) and eval(is_skip_enable) is True)

        if skip_enable:
            check_skipped(parser.parse(self.op_kwargs.get('start_date')),
                          self.op_kwargs.get('skip_after_minutes', 2880), skip_enable)
        
        self.check_dag_existence()

        self.logger.info(f"lookup key - {lookup_key}")

        pending_dag_ids = self.get_pending_source_dags(lookup_key)
        if len(pending_dag_ids) > 0:
            dag_run_data = self.get_dag_status(pending_dag_ids)

            self.check_failed_dags(dag_run_data)
            pending_dags = self.update_source_dag_statuses(dag_run_data, lookup_key)

            self.logger.info(f"pending dags count- {len(pending_dags)}")
            for pending_dag in pending_dags:
                self.logger.info(f"dag id - {pending_dag['dag_id']} has current state - {pending_dag['state']}")

            is_done = len(pending_dags) == 0
        else:
            self.logger.info("no pending dags ...")
            is_done = len(pending_dag_ids) == 0
        self.logger.info("exiting - DIExternalTaskSensor.poke()")
        return is_done
