from di_plugins.operators.operator_service import IOperatorService
from di_plugins.utils import util
from airflow.operators.python import BranchPythonOperator


class DIBranchPythonOperator(IOperatorService):
    """
    wrapper from airflow.operators.python.BranchPythonOperator
    """

    def __init__(self):
        self._config = {}
        self.logger = util.get_logger()

    def create_operator(self, operator_config: dict) -> BranchPythonOperator:
        """
        this method creates BranchPythonOperator as per given operator_config

        operator_config config must following have mandatory attributes:
        class_name: fully qualified name of python class from which callable is to be used
        method_name: python callable method name

        :param operator_config:
        :return:
        """
        self.logger.debug("executing DIBranchPythonOperator.create_operator()")
        self._config = operator_config
        self.logger.debug("creating  BranchPython operator")

        try:
            python_callable = self.get_callable(operator_config)
            operator_config.pop('class_name')
            operator_config.pop('method_name')
            operator_config['python_callable'] = python_callable

            self.logger.debug("exiting DIBranchPythonOperator.create_operator()")
            return BranchPythonOperator(**operator_config)
        except Exception as ex:
            self.logger.error("error occurred while creating  BranchPython operator, error - %s", ex)
            raise ex

    def get_callable(self, operator_config: dict):
        if 'class_name' not in operator_config.keys():
            raise Exception('callable class name not provided in operator config. please provide class_name')

        if 'method_name' not in operator_config.keys():
            raise Exception('callable class name not provided in operator config. please provide method_name')

        class_name = operator_config['class_name']
        packages = class_name.split('.')
        module_name = ".".join(packages[:-1])
        obj = __import__(module_name)

        for sub_package in packages[1:]:
            obj = getattr(obj, sub_package)

        return getattr(obj, operator_config['method_name'])
