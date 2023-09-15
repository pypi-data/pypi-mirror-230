from di_plugins.operators.operator_service import IOperatorService
from airflow.providers.oracle.operators.oracle import OracleOperator
from di_plugins.utils import util


class DIOracleOperator(IOperatorService):
    """
    wrapper around airflow.providers.oracle.operators.oracle.OracleOperator
    """

    def __init__(self):
        self._config = {}
        self.logger = util.get_logger()

    def create_operator(self, operator_config: dict) -> OracleOperator:
        self.logger.debug("executing DIOracleOperator.create_operator()")
        self._config = operator_config
        self.logger.debug("creating oracle operator")

        try:

            self.logger.debug("exiting DIOracleOperator.create_operator()")
            return OracleOperator(**operator_config)
        except Exception as ex:
            self.logger.error("error occurred while creating oracle operator, error - %s",ex)
            raise ex


