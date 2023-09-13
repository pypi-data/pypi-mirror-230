import abc
from pathlib import Path
from typing import Union, Optional

from urllib import parse


class ObjectUrl:
    def __init__(self, url: Union[str, Path]):
        self._parsed = parse.urlparse(str(url), allow_fragments=False)

    @property
    def scheme(self) -> Optional[str]:
        if self._parsed.scheme == '':
            return None
        else:
            return self._parsed.scheme

    @property
    def local_url(self) -> bool:
        return self.scheme is None or self.scheme == 'file'

    @property
    def bucket(self) -> Optional[str]:
        if self.local_url:
            return None
        else:
            if self._parsed.hostname is not None and self._parsed.hostname != '':
                return self._parsed.hostname
            else:
                path = Path(self._parsed.path)
                return path.parts[1]

    @property
    def path(self) -> str:
        if self.local_url:
            if self._parsed.hostname is not None and self._parsed.hostname != '':
                return self._parsed.hostname + self._parsed.path
            else:
                return self._parsed.path
        elif self._parsed.hostname is not None and self._parsed.hostname != '':
            path = Path(self._parsed.path)

            return '/'.join(path.parts[1:])  # omit root
        else:
            path = Path(self._parsed.path)

            return '/'.join(path.parts[2:])  # omit root and bucket

    def __str__(self):
        return str(self._parsed)

    def __repr__(self):
        return str(self)


class StoredObject(abc.ABC):
    def __init__(self, url: ObjectUrl):
        self._url: ObjectUrl = url

    def path(self) -> Path:
        return Path(self._url.path)

    def name(self) -> str:
        return Path(self._url.path).name

    def bucket(self) -> Optional[str]:
        return self._url.bucket

    def local(self) -> bool:
        return self._url.local_url

    def url(self) -> ObjectUrl:
        return self._url

    @abc.abstractmethod
    def exists(self) -> bool:
        pass

    @abc.abstractmethod
    def size(self) -> int:
        pass

    @abc.abstractmethod
    def is_dir(self) -> bool:
        pass

    @abc.abstractmethod
    def download(self, dest: Union[str, Path]):
        pass

    def __str__(self):
        return str(self._url)

    def __repr__(self):
        return str(self)
