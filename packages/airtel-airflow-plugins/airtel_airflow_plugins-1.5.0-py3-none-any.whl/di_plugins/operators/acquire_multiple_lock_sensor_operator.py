from di_plugins.operators.operator_service import IOperatorService
from di_plugins.sensors.acquire_multiple_lock_sensor import AcquireMultipleLockSensor
from di_plugins.utils import util


class DIAcquireMultipleLockSensorOperator(IOperatorService):
    """
    wrapper di_plugins.sensors.acquire_lock_sensor.AcquireLockSensor
    """

    def __init__(self):
        self._config = {}
        self.logger = util.get_logger()

    def create_operator(self, operator_config: dict) -> AcquireMultipleLockSensor:
        self.logger.debug("executing DIAcquireMultipleLockSensorOperator.create_operator()")
        self._config = operator_config
        self.logger.debug("creating acquire multiple lock sensor operator")

        try:
            self.logger.debug("exiting DIAcquireMultipleLockSensorOperator.create_operator()")
            return AcquireMultipleLockSensor(**operator_config)
        except Exception as ex:
            self.logger.error("error occurred while creating acquire multiple lock sensor operator, error - %s", ex)
            raise ex
