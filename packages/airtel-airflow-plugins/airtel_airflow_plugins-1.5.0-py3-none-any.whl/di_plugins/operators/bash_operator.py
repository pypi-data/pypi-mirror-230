from di_plugins.operators.operator_service import IOperatorService
from airflow.operators.bash import BashOperator
from di_plugins.utils import util


class DIBashOperator(IOperatorService):

    def __init__(self):
        self._config = {}
        self.logger = util.get_logger()

    def create_operator(self, operator_config: dict) -> BashOperator:
        self.logger.debug("executing DIBashOperator.create_operator()")
        self._config = operator_config
        self.logger.debug("creating bash operator")

        try:

            self.logger.debug("exiting DIBashOperator.create_operator()")
            return BashOperator(**operator_config)
        except Exception as ex:
            self.logger.error("error occurred while creating bash operator, error - %s",ex)
            raise ex


