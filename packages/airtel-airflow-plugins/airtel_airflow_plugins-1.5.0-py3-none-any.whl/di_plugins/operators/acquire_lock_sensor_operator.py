from di_plugins.operators.operator_service import IOperatorService
from di_plugins.sensors.acquire_lock_sensor import AcquireLockSensor
from di_plugins.utils import util


class DIAcquireLockSensorOperator(IOperatorService):
    """
    wrapper di_plugins.sensors.acquire_lock_sensor.AcquireLockSensor
    """

    def __init__(self):
        self._config = {}
        self.logger = util.get_logger()

    def create_operator(self, operator_config: dict) -> AcquireLockSensor:
        self.logger.debug("executing DIAcquireLockSensorOperator.create_operator()")
        self._config = operator_config
        self.logger.debug("creating acquire lock sensor operator")

        try:
            self.logger.debug("exiting DIAcquireLockSensorOperator.create_operator()")
            return AcquireLockSensor(**operator_config)
        except Exception as ex:
            self.logger.error("error occurred while creating acquire lock sensor operator, error - %s", ex)
            raise ex
