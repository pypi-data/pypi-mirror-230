from di_plugins.operators.operator_service import IOperatorService
from di_plugins.sensors.di_external_task_sensor import DIExternalTaskSensor
from di_plugins.utils import util


class DIExternalTaskSensorOperator(IOperatorService):
    
    def __init__(self):
        self._config = {}
        self.logger = util.get_logger()

    def create_operator(self, operator_config: dict) -> DIExternalTaskSensor:
        self.logger.debug("executing DIExternalTaskSensorOperator.create_operator()")
        self._config = operator_config
        self.logger.debug("creating acquire lock sensor operator")

        try:
            self.logger.debug("exiting DIExternalTaskSensorOperator.create_operator()")
            return DIExternalTaskSensor(**operator_config)
        except Exception as ex:
            self.logger.error("error occurred while creating DIExternalTaskSensor operator, error - %s", ex)
            raise ex
