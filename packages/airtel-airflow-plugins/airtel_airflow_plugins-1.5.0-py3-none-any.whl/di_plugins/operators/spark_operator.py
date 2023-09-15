from di_plugins.operators.operator_service import IOperatorService
from di_plugins.utils import util


class DISparkOperator(IOperatorService):

    def __init__(self):
        self._config = {}
        self.logger = util.get_logger()

    def create_operator(self, config: dict):
        self.logger.debug("executing DISparkOperator.create_operator()")
        self._config = config
        self.logger.debug("creating spark operator")

        """code for spark operator"""
        self.logger.debug("exiting DISparkOperator.create_operator()")
