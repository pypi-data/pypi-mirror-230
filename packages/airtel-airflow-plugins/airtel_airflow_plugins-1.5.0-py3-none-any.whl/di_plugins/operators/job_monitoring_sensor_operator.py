from di_plugins.operators.operator_service import IOperatorService
from di_plugins.sensors.job_monitor_sensor import JobMonitorSSHSensor
from di_plugins.utils import util


class DIJobMonitoringSensorOperator(IOperatorService):
    """
    wrapper around plugins.sensors.job_monitor_sensor.JobMonitorSSHSensor
    """

    def __init__(self):
        self._config = {}
        self.logger = util.get_logger()

    def create_operator(self, operator_config: dict) -> JobMonitorSSHSensor:
        self.logger.debug("executing DIJobMonitoringSensorOperator.create_operator()")
        self._config = operator_config
        self.logger.debug("creating hdfs file sensor operator")

        try:
            self.logger.debug("exiting DIJobMonitoringSensorOperator.create_operator()")
            return JobMonitorSSHSensor(**operator_config)
        except Exception as ex:
            self.logger.error("error occurred while creating hdfs file sensor operator, error - %s", ex)
            raise ex
