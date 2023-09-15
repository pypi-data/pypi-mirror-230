from di_plugins.operators.operator_service import IOperatorService
from di_plugins.sensors.hdfs_sensor import HdfsSensor
from di_plugins.utils import util


class DIHdfsFileSensorOperator(IOperatorService):
    """
    wrapper around plugins.sensors.hdfs_sensor.HdfsSensor
    """

    def __init__(self):
        self._config = {}
        self.logger = util.get_logger()

    def create_operator(self, operator_config: dict) -> HdfsSensor:
        self.logger.debug("executing DIHdfsFileSensorOperator.create_operator()")
        self._config = operator_config
        self.logger.debug("creating hdfs file sensor operator")

        try:
            self.logger.debug("exiting DIHdfsFileSensorOperator.create_operator()")
            return HdfsSensor(**operator_config)
        except Exception as ex:
            self.logger.error("error occurred while creating hdfs file sensor operator, error - %s", ex)
            raise ex
