import dataclasses
import json
from typing import List, Union, Dict, Optional

from vatis.asr_commons.domain.expression import Expressions
from vatis.asr_commons.json.deserialization import JSONDeserializable


@dataclasses.dataclass(frozen=True)
class SpokenCommandConfig(JSONDeserializable):
    command: str
    regex: List[str]
    enabled: bool = True

    def __post_init__(self):
        assert self.command is not None, 'command must not be none'
        assert self.regex is not None, 'regex must not be none'
        assert self.enabled is not None, 'enabled must not be none'

    @staticmethod
    def from_json(json_dict: dict):
        return SpokenCommandConfig(**json_dict)


class CommandsExpressions(Expressions):
    def __init__(self, expressions: Dict[str, List[str]] = None):
        super(CommandsExpressions, self).__init__(expressions)

    @staticmethod
    def from_command_config_list(expressions: List[Union[SpokenCommandConfig, dict]]) -> 'CommandsExpressions':
        parsed_expressions: Dict[str, List[str]] = {}

        for command_config in expressions:
            if isinstance(command_config, SpokenCommandConfig):
                pass
            elif isinstance(command_config, dict):
                command_config = SpokenCommandConfig.from_json(command_config)
            else:
                raise ValueError(f'Bad type: {type(command_config)}')

            if command_config.command not in parsed_expressions:
                parsed_expressions[command_config.command] = command_config.regex.copy()
            else:
                raise ValueError(f'Duplicate command: {command_config.command}')

        return CommandsExpressions(parsed_expressions)
