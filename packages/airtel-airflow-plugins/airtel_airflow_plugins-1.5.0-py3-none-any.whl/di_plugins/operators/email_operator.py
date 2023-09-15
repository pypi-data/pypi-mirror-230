from airflow.operators.email import EmailOperator
from di_plugins.operators.operator_service import IOperatorService
from di_plugins.utils import util


class DIEmailOperator(IOperatorService):

    """
    wrapper around airflow.operators.email.EmailOperator
    """
    def __init__(self):
        self._config = {}
        self.logger = util.get_logger()

    def create_operator(self, operator_config: dict) -> EmailOperator:
        self.logger.debug("executing DIEmailOperator.create_operator()")
        self._config = operator_config
        self.logger.debug("creating emil operator")

        try:
            self.logger.debug("exiting DIEmailOperator.create_operator()")
            return EmailOperator(**operator_config)
        except Exception as ex:
            self.logger.error("error occurred while creating email operator, error - %s", ex)
            raise ex
