import json
from typing import ClassVar, Union
from typing import Any, Dict, List, Optional

from vatis.asr_commons.config.headers import *

from vatis.asr_commons.config.logging import get_logger
from vatis.asr_commons.domain.transcriber import ConfigPacket, Base64InputPacket, PacketType
from vatis.asr_commons.live.headers import *

logger = get_logger(__name__)


class TranscriptionOptions:
    DISABLE_DISFLUENCIES: ClassVar[str] = 'disable_disfluencies'
    ENABLE_PUNCTUATION_CAPITALIZATION: ClassVar[str] = 'enable_punctuation_capitalization'
    ENABLE_ENTITIES_RECOGNITION: ClassVar[str] = 'enable_entities_recognition'
    ENABLE_NUMERALS_CONVERSION: ClassVar[str] = 'enable_numerals_conversion'

    SPEAKERS_DIARIZATION: ClassVar[str] = 'speakers_diarization'
    SPEAKERS_NUMBER: ClassVar[str] = 'speakers_number'
    MULTI_CHANNELS: ClassVar[str] = 'multi_channels'

    SAMPLE_RATE: ClassVar[str] = 'sample_rate'
    BIT_RATE: ClassVar[str] = 'bit_rate'
    BIT_DEPTH: ClassVar[str] = 'bit_depth'
    AUDIO_FORMAT: ClassVar[str] = 'audio_format'
    SENDING_HEADERS: ClassVar[str] = 'sending_headers'
    CHANNELS: ClassVar[str] = 'channels'

    FRAME_LEN: ClassVar[str] = 'frame_len'
    FRAME_OVERLAP: ClassVar[str] = 'frame_overlap'
    BUFFER_OFFSET: ClassVar[str] = 'buffer_offset'

    HOTWORDS: ClassVar[str] = 'hotwords'
    HOTWORDS_WEIGHT: ClassVar[str] = 'hotwords_weight'

    COMMANDS_EXPRESSIONS: ClassVar[str] = 'commands_expression'
    ENABLE_ON_COMMAND_FINAL_FRAME: ClassVar[str] = 'enable_on_command_final_frame'
    FIND_REPLACE_EXPRESSIONS: ClassVar[str] = 'find_replace_expressions'


def parse_post_processing_options(headers) -> Dict[str, Any]:
    post_processing_config: Dict[str, Any] = {}

    if DISABLE_DISFLUENCIES_HEADER in headers:
        post_processing_config[TranscriptionOptions.DISABLE_DISFLUENCIES] = str(headers.get(DISABLE_DISFLUENCIES_HEADER)).lower() == 'true'

    if ENABLE_PUNCTUATION_AND_CAPITALIZATION_HEADER in headers:
        post_processing_config[TranscriptionOptions.ENABLE_PUNCTUATION_CAPITALIZATION] = str(headers.get(ENABLE_PUNCTUATION_AND_CAPITALIZATION_HEADER)).lower() == 'true'

    if ENABLE_ENTITIES_RECOGNITION_HEADER in headers:
        post_processing_config[TranscriptionOptions.ENABLE_ENTITIES_RECOGNITION] = str(headers.get(ENABLE_ENTITIES_RECOGNITION_HEADER)).lower() == 'true'

    if ENABLE_NUMERALS_CONVERSION_HEADER in headers:
        post_processing_config[TranscriptionOptions.ENABLE_NUMERALS_CONVERSION] = str(headers.get(ENABLE_NUMERALS_CONVERSION_HEADER)).lower() == 'true'

    return post_processing_config


def parse_speakers_diarization_and_channels_transcription_options(headers) -> Dict[str, Any]:
    options: Dict[str, Any] = {}

    if SPEAKERS_DIARIZATION_HEADER in headers:
        options[TranscriptionOptions.SPEAKERS_DIARIZATION] = str(headers.get(SPEAKERS_DIARIZATION_HEADER)).lower() == 'true'

    if SPEAKERS_NUMBER_HEADER in headers:
        options[TranscriptionOptions.SPEAKERS_NUMBER] = int(headers.get(SPEAKERS_NUMBER_HEADER))

    if ENABLE_MULTI_CHANNELS in headers:
        options[TranscriptionOptions.MULTI_CHANNELS] = str(headers.get(ENABLE_MULTI_CHANNELS)).lower() == 'true'

    return options


def parse_audio_attributes(headers) -> Dict[str, Any]:
    audio_attributes: Dict[str, Any] = {}

    if SAMPLE_RATE_HEADER in headers:
        audio_attributes[TranscriptionOptions.SAMPLE_RATE] = int(headers.get(SAMPLE_RATE_HEADER))

    if BIT_RATE_HEADER in headers:
        audio_attributes[TranscriptionOptions.BIT_RATE] = int(headers.get(BIT_RATE_HEADER))

    if BIT_DEPTH_HEADER in headers:
        audio_attributes[TranscriptionOptions.BIT_DEPTH] = int(headers.get(BIT_DEPTH_HEADER))

    if AUDIO_FORMAT_HEADER in headers:
        audio_attributes[TranscriptionOptions.AUDIO_FORMAT] = str(headers.get(AUDIO_FORMAT_HEADER))

    if SENDING_HEADERS_HEADER in headers:
        audio_attributes[TranscriptionOptions.SENDING_HEADERS] = str(headers.get(SENDING_HEADERS_HEADER)).lower() == 'true'

    if CHANNELS_HEADER in headers:
        audio_attributes[TranscriptionOptions.CHANNELS] = int(headers.get(CHANNELS_HEADER))

    return audio_attributes


def parse_live_stream_config(headers) -> Dict[str, Any]:
    stream_config: Dict[str, Any] = {}

    if FRAME_LEN_HEADER in headers:
        stream_config[TranscriptionOptions.FRAME_LEN] = float(headers[FRAME_LEN_HEADER])

    if FRAME_OVERLAP_HEADER in headers:
        stream_config[TranscriptionOptions.FRAME_OVERLAP] = float(headers[FRAME_OVERLAP_HEADER])

    if BUFFER_OFFSET_HEADER in headers:
        stream_config[TranscriptionOptions.BUFFER_OFFSET] = float(headers[BUFFER_OFFSET_HEADER])

    return stream_config


def parse_hotwords_config(headers) -> Dict[str, Any]:
    hotwords_config: Dict[str, Any] = {}

    if HOTWORDS_KEY in headers:
        hotwords = headers.get(HOTWORDS_KEY)
        parsed_hotwords: Optional[List[str]] = None

        if isinstance(hotwords, list):
            parsed_hotwords = hotwords
        elif isinstance(hotwords, str):
            parsed_hotwords = list(hotwords.split(','))
        elif hotwords is not None:
            logger.warning(f'Couldn\'t parse hotwords: {hotwords}')

        hotwords_config[TranscriptionOptions.HOTWORDS] = parsed_hotwords

    if HOTWORDS_WEIGHT_KEY in headers:
        hotwords_config[TranscriptionOptions.HOTWORDS_WEIGHT] = float(headers.get(HOTWORDS_WEIGHT_KEY))

    return hotwords_config


def parse_formatting_config(headers) -> Dict[str, Any]:
    from vatis.asr_commons.domain import SpokenCommandConfig
    from vatis.asr_commons.domain import FindReplaceConfig

    config: Dict[str, Any] = {}

    if COMMANDS_EXPRESSIONS_HEADER in headers:
        command_configs: list = json.loads(headers[COMMANDS_EXPRESSIONS_HEADER])

        if isinstance(command_configs, dict):
            command_configs = [SpokenCommandConfig.from_json(command_configs)]
        elif isinstance(command_configs, list):
            command_configs = [SpokenCommandConfig.from_json(config) for config in command_configs]
        else:
            logger.warning(f'Spoken commands not parsable: {str(headers[COMMANDS_EXPRESSIONS_HEADER])}')

        config[TranscriptionOptions.COMMANDS_EXPRESSIONS] = command_configs

    if ENABLE_ON_COMMAND_FINAL_FRAME_HEADER in headers:
        config[TranscriptionOptions.ENABLE_ON_COMMAND_FINAL_FRAME] = str(headers[ENABLE_ON_COMMAND_FINAL_FRAME_HEADER]).lower() == 'true'

    if FIND_REPLACE_EXPRESSIONS_HEADER in headers:
        find_replace_configs: list = json.loads(headers[FIND_REPLACE_EXPRESSIONS_HEADER])

        if isinstance(find_replace_configs, dict):
            find_replace_configs = [FindReplaceConfig.from_json(find_replace_configs)]
        elif isinstance(find_replace_configs, list):
            find_replace_configs = [FindReplaceConfig.from_json(config) for config in find_replace_configs]
        else:
            logger.warning(f'find replace not parsable: {str(headers[FIND_REPLACE_EXPRESSIONS_HEADER])}')

        config[TranscriptionOptions.FIND_REPLACE_EXPRESSIONS] = find_replace_configs

    return config


def parse_input_packet(json_packet: dict) -> Union[Base64InputPacket, ConfigPacket]:
    if json_packet.get('type') == PacketType.BASE64_INPUT:
        return Base64InputPacket.from_json(json_packet)
    elif json_packet.get('type') == PacketType.CONFIG:
        return ConfigPacket.from_json(json_packet)
    elif 'type' not in json_packet:  # backwards compatibility
        return Base64InputPacket.from_json(json_packet)
    else:
        raise ValueError(f'Unsupported type: {json_packet.get("type")}')
