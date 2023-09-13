import dataclasses
from typing import List, Optional, get_type_hints

from vatis.asr_commons.domain.spoken_commands import SpokenCommandConfig
from vatis.asr_commons.domain.find_replace import FindReplaceConfig

from vatis.asr_commons.json import serialization, deserialization


@dataclasses.dataclass
class LiveConfig(serialization.ExcludeNullsJSONSerializer, deserialization.JSONDeserializable):
    @staticmethod
    def from_json(json_dict: dict):
        return LiveConfig(**json_dict)

    spokenCommands: Optional[bool] = None


@dataclasses.dataclass
class ModelConfig(serialization.ExcludeNullsJSONSerializer, deserialization.JSONDeserializable):
    uid: str
    default: bool
    createdDate: str
    discriminator: str
    name: str
    language: str
    description: Optional[str] = None
    disfluencies: Optional[bool] = None
    punctuationCapitalization: Optional[bool] = None
    entitiesRecognition: Optional[bool] = None
    numeralsConversion: Optional[bool] = None
    speakersDiarization: Optional[bool] = None
    multipleChannels: Optional[bool] = None
    customVocabulary: Optional[List[str]] = None
    boostParam: Optional[float] = None
    liveConfig: Optional[LiveConfig] = None
    findReplace: Optional[bool] = None

    @staticmethod
    def from_json(json_dict: dict):
        if json_dict.get('liveConfig') is not None:
            json_dict['liveConfig'] = LiveConfig.from_json(json_dict['liveConfig'])

        return ModelConfig(**json_dict)


@dataclasses.dataclass
class LanguageConfig(serialization.ExcludeNullsJSONSerializer, deserialization.JSONDeserializable):
    language: str
    default: bool
    models: List[ModelConfig] = None
    spokenCommandsList: List[SpokenCommandConfig] = None
    findReplaceList: List[FindReplaceConfig] = None

    def __post_init__(self):
        if self.models is None:
            self.models = []
        if self.spokenCommandsList is None:
            self.spokenCommandsList = []
        if self.findReplaceList is None:
            self.findReplaceList = []

    @staticmethod
    def from_json(json_dict: dict):
        if json_dict.get('models') is not None:
            json_dict['models'] = [ModelConfig.from_json(config_json) for config_json in json_dict['models']]
        if json_dict.get('spokenCommandsList') is not None:
            json_dict['spokenCommandsList'] = [SpokenCommandConfig.from_json(config_json) for config_json in json_dict['spokenCommandsList']]
        if json_dict.get('findReplaceList') is not None:
            json_dict['findReplaceList'] = [FindReplaceConfig.from_json(config_json) for config_json in json_dict['findReplaceList']]

        return LanguageConfig(**json_dict)


@dataclasses.dataclass
class TranscriptionConfig(serialization.ExcludeNullsJSONSerializer, deserialization.JSONDeserializable):
    languageConfigs: List[LanguageConfig] = None

    def __post_init__(self):
        if self.languageConfigs is None:
            self.languageConfigs = []

    @staticmethod
    def from_json(json_list: list):
        if json_list is not None:
            json_list = [LanguageConfig.from_json(config_json) for config_json in json_list]

        return TranscriptionConfig(languageConfigs=json_list)

    def to_json(self) -> list:
        if self.languageConfigs is not None:
            return [language_config.to_json() for language_config in self.languageConfigs]
        else:
            return []
