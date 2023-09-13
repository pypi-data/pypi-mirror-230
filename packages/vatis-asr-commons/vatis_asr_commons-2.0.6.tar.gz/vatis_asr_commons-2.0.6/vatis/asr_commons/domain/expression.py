from os import PathLike
from pathlib import Path
from typing import List, Dict, Optional


class Expressions:

    def __init__(self, expressions: Dict[str, List[str]] = None):
        self._expressions: Dict[str, List[str]] = expressions if expressions is not None else {}

    @staticmethod
    def _parse_tsv_string(tsv_str: str) -> Dict[str, List[str]]:
        expressions: Dict[str, List[str]] = {}

        for line in tsv_str.split('\n'):
            line = line.strip()

            if line.startswith('#') or not len(line):
                continue

            tokens = line.split('\t')
            expressions[tokens[0]] = tokens[1:]

        return expressions

    def get(self, key: str) -> List[str]:
        expressions: Optional[List[str]] = self._expressions.get(key, [])

        if expressions is None:
            expressions = []

        return expressions

    def keys(self) -> List[str]:
        return [key for key in self._expressions]

    def items(self):
        return self._expressions.items()

    def __hash__(self):
        return hash(frozenset(self._expressions))

    def __eq__(self, other):
        if isinstance(other, Expressions):
            return self._expressions == other

        return False

    @staticmethod
    def from_tsv_str(tsv: str) -> 'Expressions':
        expressions = Expressions._parse_tsv_string(tsv)
        return Expressions(expressions)

    @staticmethod
    def from_tsv_file(tsv_file: PathLike, raise_if_not_found: bool = False) -> 'Expressions':
        tsv_file = Path(tsv_file)

        if tsv_file.exists():
            with open(tsv_file, 'r') as f:
                lines = f.readlines()

            tsv = ''.join(lines)

            return Expressions.from_tsv_str(tsv)
        else:
            message = f'Expressions path does not exist: {str(tsv_file)}'

            if raise_if_not_found:
                raise FileNotFoundError(message)

        return Expressions.empty()

    @staticmethod
    def empty():
        return Expressions()

    @staticmethod
    def from_dict(expressions: Dict[str, List[str]]):
        return Expressions(expressions.copy())
