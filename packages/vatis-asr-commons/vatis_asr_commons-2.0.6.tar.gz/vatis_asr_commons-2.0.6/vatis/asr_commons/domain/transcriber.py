import base64
import binascii

import numpy as np

from typing import List, Tuple, Type, ClassVar

from vatis.asr_commons.domain.word import Word
from vatis.asr_commons.json.deserialization import JSONDeserializable
from vatis.asr_commons.live.headers import FLUSH_HEADER, FINAL_FRAME_HEADER
from vatis.asr_commons.domain.find_replace import FindReplaceConfig
from vatis.asr_commons.domain.spoken_commands import SpokenCommandConfig


class PacketType:
    STRING: ClassVar[str] = 'STRING'
    BYTE_DATA: ClassVar[str] = 'BYTE'
    BASE64_INPUT: ClassVar[str] = 'DATA'
    CONFIG: ClassVar[str] = 'CONFIG'
    CONFIG_APPLIED: ClassVar[str] = 'CONFIG_APPLIED'
    TRANSCRIPTION: ClassVar[str] = 'TRANSCRIPTION'
    TIMESTAMPED_TRANSCRIPTION: ClassVar[str] = 'TIMESTAMPED_TRANSCRIPTION'
    NUMPY_ARRAY: ClassVar[str] = 'NUMPY_ARRAY'
    LOGITS: ClassVar[str] = 'LOGITS'
    SPACED_LOGITS: ClassVar[str] = 'SPACED_LOGITS'
    PROCESSED_TIMESTAMPED_TRANSCRIPTION: ClassVar[str] = 'PROCESSED_TIMESTAMPED_TRANSCRIPTION'


class DataPacket:
    def __init__(self, headers=None, type: str = None, **kwargs):
        if type is None:
            raise ValueError(f'"type" cannot be None')

        self.type: str = type
        self.headers = {} if headers is None else headers.copy()

    def get_header(self, name, default=None, dtype: Type = str):
        if name not in self.headers:
            return default

        if default is not None:
            dtype = type(default)

        if dtype == bool:
            return str(self.headers.get(name)) == 'True'
        else:
            return dtype(self.headers.get(name))

    def set_header(self, name, value):
        self.headers[name] = value

    def __str__(self):
        return f'"headers": {str(self.headers)}'

    def __repr__(self):
        return self.__str__()


class StringPacket(DataPacket):
    def __init__(self, data: str, headers=None, type: str = PacketType.STRING, **kwargs):
        super().__init__(headers, type, **kwargs)
        self.data = data

    def __str__(self):
        return f'{{"data": {self.data}, {super().__str__()}}}'


class ByteDataPacket(DataPacket):
    def __init__(self, data: bytes, headers=None, type: str = PacketType.BYTE_DATA, **kwargs):
        super().__init__(headers, type, **kwargs)
        self.data = data

    def __str__(self):
        return f'{{"data": {hash(self.data)}, {super().__str__()}}}'


class Base64InputPacket(ByteDataPacket, JSONDeserializable):
    def __init__(self, data: str,
                 close: bool = False,
                 flush: bool = False,
                 headers: dict = None,
                 type: str = PacketType.BASE64_INPUT, **kwargs):
        try:
            data_encoded: bytes = data.encode('utf-8')
            parsed_data: bytes = base64.b64decode(data_encoded)
        except binascii.Error:
            data_no_headers: str = data.split(',')[1]
            data_encoded = data_no_headers.encode('utf-8')
            parsed_data: bytes = base64.b64decode(data_encoded)

        if flush:
            if headers is None:
                headers = {}
            headers[FLUSH_HEADER] = flush
            headers[FINAL_FRAME_HEADER] = flush

        super(Base64InputPacket, self).__init__(data=parsed_data, headers=headers, type=type, **kwargs)
        self.close: bool = close
        self.flush = flush

    @staticmethod
    def from_json(json_dict: dict):
        if 'close' in json_dict:
            if json_dict.get('close') == 'False':
                json_dict['close'] = False
            elif json_dict.get('close') == 'True':
                json_dict['close'] = True

        if 'flush' in json_dict:
            if json_dict.get('flush') == 'False':
                json_dict['flush'] = False
            elif json_dict.get('flush') == 'True':
                json_dict['flush'] = True

        return Base64InputPacket(**json_dict)


class ConfigPacket(DataPacket, JSONDeserializable):

    def __init__(self,
                 spokenCommandsList: List[SpokenCommandConfig] = None,
                 findReplaceList: List[FindReplaceConfig] = None,
                 headers=None,
                 type: str = PacketType.CONFIG, **kwargs):
        super().__init__(headers, type, **kwargs)
        self.spokenCommandsList: List[SpokenCommandConfig] = spokenCommandsList
        self.findReplaceList: List[FindReplaceConfig] = findReplaceList

    @staticmethod
    def from_json(json_dict: dict):
        if 'spokenCommandsList' in json_dict:
            spoken_commands_list: List[SpokenCommandConfig] = []

            for spoken_command in json_dict['spokenCommandsList']:
                spoken_commands_list.append(SpokenCommandConfig.from_json(spoken_command))

            json_dict['spokenCommandsList'] = spoken_commands_list

        if 'findReplaceList' in json_dict:
            find_replace_list: List[FindReplaceConfig] = []

            for find_replace in json_dict['findReplaceList']:
                find_replace_list.append(FindReplaceConfig.from_json(find_replace))

            json_dict['findReplaceList'] = find_replace_list

        return ConfigPacket(**json_dict)


class ConfigAppliedPacket(DataPacket):
    def __init__(self, config_packet: ConfigPacket, headers: dict = None, type: str = PacketType.CONFIG_APPLIED, **kwargs):
        if headers is None:
            headers = config_packet.headers
        super(ConfigAppliedPacket, self).__init__(headers, type, **kwargs)
        self.config_packet: ConfigPacket = config_packet


class TranscriptionPacket(DataPacket):
    def __init__(self, transcript: str, headers=None, type: str = PacketType.TRANSCRIPTION, **kwargs):
        super().__init__(headers, type, **kwargs)
        self.transcript = transcript

    def __str__(self):
        return f'{{"transcript": {hash(self.transcript)}, {super().__str__()}}}'


class TimestampedTranscriptionPacket(TranscriptionPacket):
    """
    Packet that contains the transcript with the timestamps associated to each word.

    Params:
     - words: list of transcribed words
     - headers: headers of the packet
    """

    def __init__(self, words: List[Word], headers=None, transcript=None, type: str = PacketType.TIMESTAMPED_TRANSCRIPTION, **kwargs):
        transcript = transcript if transcript is not None else ' '.join([word.word for word in words])
        super().__init__(transcript, headers, type, **kwargs)

        self.words = words

    def __str__(self):
        return f'{{"words": {str(self.words)}, {super().__str__()}}}'


class NdArrayDataPacket(DataPacket):
    def __init__(self, data: np.ndarray, headers=None, type: str = PacketType.NUMPY_ARRAY, **kwargs):
        super().__init__(headers, type, **kwargs)
        self.data: np.ndarray = data

    def __str__(self):
        return f'{{"data": {hash(self.data.tobytes())}, {super().__str__()}}}'


class LogitsDataPacket(NdArrayDataPacket):
    def __init__(self, data: np.ndarray, timestep_duration: float, headers=None, type: str = PacketType.LOGITS, **kwargs):
        super().__init__(data, headers, type, **kwargs)
        self.timestep_duration = timestep_duration

    def __str__(self):
        return f'{{"timestep_duration": {self.timestep_duration}, {super().__str__()}}}'


class SpacedLogitsDataPacket(LogitsDataPacket):
    def __init__(self, data: np.ndarray,
                 timestep_duration: float,
                 spaces: List[Tuple[int, int]],
                 headers=None,
                 type: str = PacketType.SPACED_LOGITS, **kwargs):
        super().__init__(data, timestep_duration, headers, type, **kwargs)
        self.spaces = spaces

    def __str__(self):
        return f'{{"spaces": {str(self.spaces)}, {super().__str__()}}}'


class ProcessedTranscriptionPacket(TimestampedTranscriptionPacket):
    def __init__(self, processed_words: List[Word],
                 raw_transcription_packet: TimestampedTranscriptionPacket,
                 type: str = PacketType.PROCESSED_TIMESTAMPED_TRANSCRIPTION, **kwargs):
        super().__init__(words=raw_transcription_packet.words,
                         headers=raw_transcription_packet.headers,
                         transcript=' '.join([word.word for word in processed_words]),
                         type=type, **kwargs)
        self.processed_words = processed_words
