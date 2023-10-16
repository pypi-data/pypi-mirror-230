import os
from dotenv import load_dotenv
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.Logger import Logger
from circles_local_database_python.connector import Connector
from circles_local_database_python.generic_crud import GenericCRUD
from language_local import lang_code
# from src.template import ReplaceFieldsWithValues
load_dotenv()

VARIABLE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 175
VARIABLE_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = "variable-local-python-package"

object_to_insert = {
    'component_id': VARIABLE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': VARIABLE_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'guy.n@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)


class VariablesLocal(GenericCRUD):
    def __init__(self):
        self.name2id_dict = {}
        self.id2name_dict = {}
        self.next_variable_id = 1
        self.connector = Connector.connect('field')
        self.cursor = self.connector.cursor(dictionary=True, buffered=True)
        VARIABLE_NAMES_DICT = self.load_data_from_variable_table()
        for variable_id in VARIABLE_NAMES_DICT:
            self.add(variable_id=variable_id,
                     variable_name=VARIABLE_NAMES_DICT[variable_id])

    def add(self, variable_id: int, variable_name: str) -> None:
        logger.start(object={'variable_id': variable_id,
                     'variable_name': variable_name})
        try:
            self.name2id_dict[variable_name] = variable_id
            self.id2name_dict[variable_id] = variable_name
            self.cursor.execute("""INSERT INTO variable_table(variable_id, name) VALUES (%s, %s)""", [
                                variable_id, variable_name])
            self.connector.commit()

        except Exception as ex:
            message = 'error: Failed to add variable'
            logger.exception(message, object=ex)
            logger.end()
            """TODO: add error to logger"""
        logger.end()

    def get_variable_id_by_variable_name(self, variable_name: str) -> int:
        logger.start(object={'variable_name': variable_name})
        variable_id = self.name2id_dict[variable_name]
        logger.end(object={'variable_id': variable_id})
        return variable_id

    def get_variable_name_by_variable_id(self, variable_id: int) -> str:
        logger.start(object={'variable_id': variable_id})
        variable_name = self.id2name_dict[variable_id]
        logger.end(object={'variable_name': variable_name})
        return variable_name

    def get_variable_value_by_variable_name_and_lang_code(self, variable_name: str, lang_code: lang_code) -> str:
        logger.start(object={'lang_code': lang_code,
                     'variable_name': variable_name})
        variable_id = self.get_variable_id_by_variable_name(
            variable_name=variable_name)
        variable_value = VariablesLocal.get_variable_value_by_variable_id(
            lang_code=lang_code, variable_id=variable_id)
        logger.end(object={'variable_value': variable_value})
        return variable_value

    @staticmethod
    def get_variable_value_by_variable_id(variable_id: int, lang_code: lang_code) -> str:
        connection = Connector.connect('dialog_workflow')
        cursor = connection.cursor(dictionary=True, buffered=True)
        logger.start(object={'lang_code': lang_code,
                     'variable_id': variable_id})
        # TODO: Change to our database package
        cursor.execute(
            """SELECT variable_value_new FROM dialog_workflow_state_history_view WHERE variable_id= %s ORDER BY timestamp DESC""", [variable_id])
        variable_value = (cursor.fetchone())["variable_value_new"]
        logger.end(object={'variable_value': variable_value})
        return variable_value

    def load_data_from_variable_table(self) -> dict:
        logger.start()
        connection = Connector.connect('field')
        cursor = connection.cursor(dictionary=True, buffered=True)
        cursor.execute("""SELECT variable_id, name FROM variable_table""")
        rows = cursor.fetchall()
        data = {}
        # backward_data = {}
        for row in rows:
            variable_id, variable_name = row['variable_id'], row['name']
            # backward_data[variable_name] = variable_id
            data[variable_id] = variable_name
        logger.end(object={'data': data})
        return data
