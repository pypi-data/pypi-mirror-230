from di_plugins.operators.operator_service import IOperatorService
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from di_plugins.utils import util


class DITriggerDagRunOperator(IOperatorService):
    """
    wrapper around airflow.operators.trigger_dagrun.TriggerDagRunOperator
    """
    def __init__(self):
        self._config = {}
        self.logger = util.get_logger()

    def create_operator(self, operator_config: dict) -> TriggerDagRunOperator:
        self.logger.debug("executing DITriggerDagRunOperator.create_operator()")
        self._config = operator_config
        self.logger.debug("creating TriggerDagRun operator")

        try:

            self.logger.debug("exiting DITriggerDagRunOperator.create_operator()")
            return TriggerDagRunOperator(**operator_config)
        except Exception as ex:
            self.logger.error("error occurred while creating TriggerDagRun operator, error - %s",ex)
            raise ex


