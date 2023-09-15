from di_plugins.operators.operator_service import IOperatorService
from di_plugins.sensors.local_file_sensor import LocalFileSensor
from di_plugins.utils import util


class DILocalFileSensorOperator(IOperatorService):
    """
    wrapper around plugins.sensors.local_file_sensor.LocalFileSensor
    """

    def __init__(self):
        self._config = {}
        self.logger = util.get_logger()

    def create_operator(self, operator_config: dict) -> LocalFileSensor:
        self.logger.debug("executing DILocalFileSensorOperator.create_operator()")
        self._config = operator_config
        self.logger.debug("creating local file sensor operator")

        try:
            self.logger.debug("exiting DILocalFileSensorOperator.create_operator()")
            return LocalFileSensor(**operator_config)
        except Exception as ex:
            self.logger.error("error occurred while creating local file sensor operator, error - %s", ex)
            raise ex
