from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.sensors.base import BaseSensorOperator
from airflow.exceptions import AirflowException
from di_plugins.sensors.sensor_util import check_skipped
from dateutil import parser

class SSHSensor(BaseSensorOperator, SSHOperator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def raise_for_status(self, exit_status: int, stderr: bytes, context=None) -> None:
        if context and self.do_xcom_push:
            ti = context.get("task_instance")
            ti.xcom_push(key="ssh_exit", value=exit_status)
        if exit_status != 0 and exit_status != 99:
            # exclude 99 code as well, as this is custom return code we're using for reschedule
            raise AirflowException(f"SSH test operator error: exit status = {exit_status}")
        self.exit_status = exit_status

    def poke(self, context):

        #Skip current instance before reschedule
        is_skip_enable = self.op_kwargs.get('skip_enable', False)
        skip_enable = (isinstance(is_skip_enable, bool) and is_skip_enable is True) or (isinstance(is_skip_enable, str) and eval(is_skip_enable) is True)
        check_skipped(parser.parse(self.op_kwargs.get('start_date')),self.op_kwargs.get('skip_after_minutes', 1440), skip_enable)

        SSHOperator.execute(self, context)
        # as a usual poking service runs on airflow, applicaiton errors are raised if any error occurs.
        # to not mistake bash script errors (return code 1) as rescheulable event we implement a custom
        # return code 99. 
        # if we get return code of 99 we reschedule the job
        if self.exit_status == 99:
            return False
        elif self.exit_status == 0:
            return True