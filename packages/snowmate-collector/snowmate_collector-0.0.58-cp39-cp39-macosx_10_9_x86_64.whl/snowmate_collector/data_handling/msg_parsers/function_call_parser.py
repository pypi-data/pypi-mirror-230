import os
from typing import List

from snowmate_common.messages_data.messages import ExternalFunction, Inputs, TestCase

from snowmate_collector.configs.collector_settings import CollectorSettings
from snowmate_collector.data_collection.function_call_data import UserFunctionCall
from snowmate_collector.data_handling.msg_parsers.utils import serialize_data
from snowmate_collector.data_serialization.ipc_serializer import IpcPickleSerializer
from snowmate_collector.data_serialization.utils import (
    MAIN_STR,
    replace__main__with_real_name,
)


class FunctionCallParser:
    """
    This class is responsible for parsing UserFunctionCall messages in the worker process.
    The serializer method can be configured and is default to IpcPickleSerializer.
    """

    def __init__(self, serializer=IpcPickleSerializer()) -> None:
        """
        Constructor for FunctionCallParser.
        :param serializer: serializer to use. Default is IpcPickleSerializer.
        :type serializer: Any
        """
        self.serializer = serializer

    def parse(self, msg: UserFunctionCall) -> TestCase:
        """
        This function parses a UserFunctionCall message to TestCaseMessage.
        :param msg: msg to parse
        :type msg: UserFunctionCall.
        :return: parsed message.
        :rtype: TestCaseMessage
        """

        file_path = os.path.relpath(
            msg.function_metadata.full_path, CollectorSettings.project_path
        )
        if msg.function_metadata.module_name == MAIN_STR:
            msg.function_metadata.full_name = replace__main__with_real_name(
                msg.function_metadata.full_name, file_path
            )
        # Start the parsing and protobuff build.
        should_obfuscate_data = CollectorSettings.should_obfuscate_data
        pre_run_args = serialize_data(msg.pre_run_args, should_obfuscate_data)
        pre_run_kwargs = serialize_data(msg.pre_run_kwargs, should_obfuscate_data)
        return_value = serialize_data(msg.return_value, should_obfuscate_data)
        post_run_args = serialize_data(msg.post_run_args, should_obfuscate_data)
        post_run_kwargs = serialize_data(msg.post_run_kwargs, should_obfuscate_data)

        project_id = CollectorSettings.project_id
        full_name = msg.function_metadata.full_name
        code_hash = str(msg.function_metadata.code_hash)
        raised_exception = serialize_data(msg.execption, should_obfuscate_data)
        pre_run_inputs = Inputs(args=pre_run_args, kwargs=pre_run_kwargs)
        post_run_inputs = Inputs(args=post_run_args, kwargs=post_run_kwargs)
        formatted_external_function = self._get_parsed_external_calls(msg)
        msg_globals = serialize_data(msg.globals, should_obfuscate_data)
        signature = serialize_data(
            (msg.function_metadata.function_signature), should_obfuscate_data
        )
        python_version = CollectorSettings.python_version
        collector_version = CollectorSettings.lib_version

        is_async_function = msg.function_metadata.is_async

        # Finally, build the test case protobuff message.
        data = TestCase(
            external_functions=formatted_external_function,
            pre_run_inputs=pre_run_inputs,
            post_run_inputs=post_run_inputs,
            return_value=return_value,
            project_id=project_id,
            file_path=file_path,
            full_name=full_name,
            code_hash=code_hash,
            raised_exception=raised_exception,
            globals=msg_globals,
            function_signature=signature,
            python_version=python_version,
            collector_version=collector_version,
            is_async_function=is_async_function,
        )
        return data

    def _get_parsed_external_calls(
        self, msg: UserFunctionCall
    ) -> List[ExternalFunction]:
        """
        This function parses UserFunctionCall.external_calls to the message ExternalFunction format.
        :param msg: message to parse.
        :type msg: UserFunctionCall
        :return: list of external functions.
        :rtype: List[ExternalFunction]
        """
        should_obfuscate_data = CollectorSettings.should_obfuscate_data
        external_function_formatted = []
        for external_function in msg.external_calls:
            external_function_formatted.append(
                ExternalFunction(
                    full_name=external_function.function_metadata.full_name,
                    raised_exception=serialize_data(
                        external_function.execption, should_obfuscate_data
                    ),
                    module_name=external_function.function_metadata.module_name,
                    return_value=serialize_data(
                        external_function.return_value, should_obfuscate_data
                    ),
                )
            )

        return external_function_formatted
