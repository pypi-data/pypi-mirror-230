import os
import sys
script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_directory, '..'))
import pytest
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.Logger import Logger
from variable_local.src.template import *
from variable_local.src.variable import *
from unittest.mock import Mock, patch
from dotenv import load_dotenv
load_dotenv()

object_to_insert = {
    'component_id': VARIABLE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': VARIABLE_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'guy.n@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)

TEST_VARIABLE_NAME1 = 'variable1'
TEST_VARIABLE_ID1 = 1
TEST_VARIABLE_VALUE1 = 'variable1 value'


class MockCursor:
    def execute(self, query, params):
        pass


class MockConnection:
    def commit(self):
        pass


@pytest.fixture
def mocker_get_variable_value_by_variable_id(mocker):
    return mocker.patch("variable_local.src.variable.VariablesLocal.get_variable_value_by_variable_id", return_value="mocked_value")


class TestVariablesLocal:
    @pytest.fixture
    def variable_instance(self):
        return VariablesLocal()

    def test_initialization(self, variable_instance):
        message = 'test_initialization succeed'
        logger.start(object={'variable_instance': str(variable_instance)})
        assert len(variable_instance.name2id_dict) == 34
        assert len(variable_instance.id2name_dict) == 34
        assert variable_instance.next_variable_id == 1
        logger.end(message)

    def test_variable_add_method(self, variable_instance):
        message = 'test_add_method succeed'
        logger.start(object={'variable_instance': str(variable_instance)})
        variable_instance.variable_add(variable_id=TEST_VARIABLE_ID1, variable_name=TEST_VARIABLE_NAME1)
        assert variable_instance.name2id_dict[TEST_VARIABLE_NAME1] == TEST_VARIABLE_ID1
        assert variable_instance.id2name_dict[TEST_VARIABLE_ID1] == TEST_VARIABLE_NAME1
        logger.end(message)

    def test_get_variable_id(self, variable_instance):
        message = 'test_get_variable_id succeed'
        logger.start(object={'variable_instance': str(variable_instance)})
        variable_instance.name2id_dict[TEST_VARIABLE_NAME1] = TEST_VARIABLE_ID1
        assert variable_instance.get_variable_id(
            variable_name=TEST_VARIABLE_NAME1) == TEST_VARIABLE_ID1
        logger.end(message)

    def test_get_variable_name(self, variable_instance):
        message = 'test_get_variable_name succeed'
        logger.start(object={'variable_instance': str(variable_instance)})
        variable_instance.id2name_dict[TEST_VARIABLE_ID1] = TEST_VARIABLE_NAME1
        assert variable_instance.get_variable_name(
            variable_id=TEST_VARIABLE_ID1) == TEST_VARIABLE_NAME1
        logger.end(message)

    def test_get_variable_value_by_variable_name(self, variable_instance, mocker_get_variable_value_by_variable_id):
        message = 'test_get_variable_value_by_variable_name succeed'
        logger.start(object={'variable_instance': str(
            variable_instance), 'mocker_get_variable_value_by_variable_id': str(mocker_get_variable_value_by_variable_id)})
        variable_instance.name2id_dict[TEST_VARIABLE_NAME1] = TEST_VARIABLE_ID1
        result = variable_instance.get_variable_value_by_variable_name(
            variable_name=TEST_VARIABLE_NAME1, lang_code="en")
        assert result == "mocked_value"
        logger.end(message)

    @patch.object(VariablesLocal, 'get_variable_value_by_variable_id')
    def test_get_variable_value_by_variable_id(self, mock_get_variable_value_by_variable_id, variable_instance):
        message = ' test_get_variable_value_by_variable_id succeed'
        logger.start(object={'mock_get_variable_value_by_variable_id': str(
            mock_get_variable_value_by_variable_id), 'variable_instance': str(variable_instance)})
        mock_get_variable_value_by_variable_id.return_value = "mocked_value"
        variable_instance.name2id_dict[TEST_VARIABLE_NAME1] = TEST_VARIABLE_ID1
        result = variable_instance.get_variable_value_by_variable_id(
            variable_id= TEST_VARIABLE_ID1, language='en')
        assert result == "mocked_value"
        mock_get_variable_value_by_variable_id.assert_called_once_with(
            variable_id=TEST_VARIABLE_ID1, language='en')
        logger.end(message)

    def test_load_data_from_table(self, variable_instance):
        message = 'test_load_data_from_table succeed'
        logger.start(object={'variable_instance': str(variable_instance)})
        obj = variable_instance.load_data_from_variable_table()
        assert obj[1] == "Person Id"
        assert obj[2] == "User Id"
        assert obj[3] == "Profile Id"
        assert obj[4] == "Lang Code"
        assert obj[5] == "Name Prefix"
        assert obj[6] == "First Name"
        assert obj[7] == "Middle Name"
        assert obj[8] == "Last Name"
        assert obj[9] == "Name Suffix"
        assert obj[10] == "Full Name"
        logger.end(message)


def mock_get_variable_id(variable_name):
    return TEST_VARIABLE_ID1  # Mock variable ID for testing


def mock_get_variable_value_by_variable_id(language, variable_id):
    return "Mocked Value"  # Mock variable value for testing


class TestReplaceFieldsWithValues:
    @pytest.fixture
    def replace_instance(self):
        variable_instance = VariablesLocal()
        return ReplaceFieldsWithValues("Hello {Name}, how are you {feeling|doing}?", "language", variable_instance)

    def test_choose_option(self):
        logger_message = 'test_choose_option succeed'
        logger.start()
        result_index = 35
        test_first_param = "feeling"
        message = "Hello {Name}, how are you {feeling|doing}?"
        replace_instance = ReplaceFieldsWithValues(message, "en", None)

        result, index = replace_instance.choose_option(
            message_index=result_index, first_param=test_first_param)

        # Check if the selected result is one of the options
        assert result in ["feeling", "doing"]
        logger.end(logger_message)

    def test_get_variable_names_and_chosen_option(self, replace_instance):
        message = 'test_get_variable_names_and_chosen_option succeed'
        logger.start(object={'replace_instance': str(replace_instance)})
        variable_names_list, message_without_variable_names = replace_instance.get_variable_names_and_chosen_option()
        assert variable_names_list == ["Name"]
        assert message_without_variable_names == "Hello {}, how are you doing?" or message_without_variable_names == "Hello {}, how are you feeling?"
        logger.end(message)

    def test_get_variable_values_and_chosen_option(self, replace_instance, mocker, mocker_get_variable_value_by_variable_id):
        #test input -> replace_instance = ReplaceFieldsWithValues(message = "Hello {Name}, how are you {feeling|doing}?",code_lang = "language",variable =  variable_instance)
        logger_message = 'test_get_variable_values_and_chosen_option succeed'
        logger.start(object={'replace_instance': str(
            replace_instance), 'mocker': str(mocker)})
        mocker.patch.object(replace_instance.variable,
                            "get_variable_id", return_value=TEST_VARIABLE_ID1)
        result = replace_instance.get_variable_values_and_chosen_option()
        assert result == "Hello mocked_value, how are you doing?" or result == "Hello mocked_value, how are you feeling?"
        logger.end(logger_message)


if __name__ == '__main__':
    pytest.main()
