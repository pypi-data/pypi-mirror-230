import abc


class JSONDeserializable(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def from_json(json_dict: dict):
        pass
