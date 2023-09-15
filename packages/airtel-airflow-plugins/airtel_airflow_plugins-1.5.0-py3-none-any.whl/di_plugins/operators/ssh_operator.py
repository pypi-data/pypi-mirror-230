from di_plugins.operators.operator_service import IOperatorService
from airflow.providers.ssh.operators.ssh import SSHOperator
from di_plugins.utils import util


class DISSHOperator(IOperatorService):

    def __init__(self):
        self._config = {}
        self.logger = util.get_logger()

    def create_operator(self, operator_config: dict) -> SSHOperator:
        self.logger.debug("executing DISSHOperator.create_operator()")
        self._config = operator_config
        self.logger.debug("creating SSH operator")

        try:

            self.logger.debug("exiting DISSHOperator.create_operator()")
            return SSHOperator(**operator_config)
        except Exception as ex:
            self.logger.error("error occurred while creating SSH operator, error - %s",ex)
            raise ex


