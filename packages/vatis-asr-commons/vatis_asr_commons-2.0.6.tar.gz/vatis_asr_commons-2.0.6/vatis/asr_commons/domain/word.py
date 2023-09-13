from typing import Optional, ClassVar, Union


class Word:
    class Entity:
        PERSON: ClassVar[str] = 'PERSON'
        GPE: ClassVar[str] = 'GPE'
        LOC: ClassVar[str] = 'LOC'
        ORG: ClassVar[str] = 'ORG'
        LANGUAGE: ClassVar[str] = 'LANGUAGE'
        NAT_REL_POL: ClassVar[str] = 'NAT_REL_POL'
        DATETIME: ClassVar[str] = 'DATETIME'
        DATE: ClassVar[str] = 'DATE'
        TIME: ClassVar[str] = 'TIME'
        PERIOD: ClassVar[str] = 'PERIOD'
        QUANTITY: ClassVar[str] = 'QUANTITY'
        MONEY: ClassVar[str] = 'MONEY'
        NUMERIC: ClassVar[str] = 'NUMERIC'
        ORDINAL: ClassVar[str] = 'ORDINAL'
        FACILITY: ClassVar[str] = 'FACILITY'
        WORK_OF_ART: ClassVar[str] = 'WORK_OF_ART'
        EVENT: ClassVar[str] = 'EVENT'
        REPLACED: ClassVar[str] = 'REPLACED'
        CODE: ClassVar[str] = 'CODE'
        ELECTRONIC: ClassVar[str] = 'ELECTRONIC'
        RANGE: ClassVar[str] = 'RANGE'
        BRAND: ClassVar[str] = 'BRAND'

    def __init__(self, word: str, start_time_millis: float, end_time_millis: float, speaker: Optional[Union[str, int]] = None,
                 confidence: float = 0, entity: Optional[str] = None, entity_group_id: Optional[Union[int, str]] = None,
                 speaker_id: Optional[str] = None):
        self.word: str = word
        self.start_time: float = start_time_millis
        self.end_time: float = end_time_millis
        self.speaker: Optional[str] = str(speaker) if speaker is not None else None
        self.speaker_id: Optional[str] = speaker_id
        self.confidence: float = confidence
        self.entity: Optional[str] = entity
        self.entity_group_id: Optional[str] = str(entity_group_id) if entity_group_id is not None else None

    def __str__(self):
        return f'''
        {{
            "word": "{self.word}",
            "start_time": {self.start_time},
            "end_time": {self.end_time},
            "speaker": "{self.speaker}",
            "speaker_id": "{self.speaker_id}",
            "confidence": {self.confidence},
            "entity": "{self.entity}",
            "entity_group_id": {self.entity_group_id}
        }}
        '''

    def __repr__(self):
        return self.__str__()

    def copy(self):
        return Word(
            word=self.word,
            start_time_millis=self.start_time,
            end_time_millis=self.end_time,
            speaker=self.speaker,
            speaker_id=self.speaker_id,
            confidence=self.confidence,
            entity=self.entity,
            entity_group_id=self.entity_group_id
        )
