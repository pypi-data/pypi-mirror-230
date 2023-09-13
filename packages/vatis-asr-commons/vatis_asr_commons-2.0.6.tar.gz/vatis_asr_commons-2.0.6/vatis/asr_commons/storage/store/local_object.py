import shutil
from pathlib import Path
from typing import Union

from .stored_object import StoredObject, ObjectUrl

from vatis.asr_commons.utils.file import get_size


class LocalObject(StoredObject):
    def exists(self) -> bool:
        return self.path().exists()

    def size(self) -> int:
        return get_size(self.path())

    def path(self) -> Path:
        return Path(self._url.path).absolute().resolve(strict=True)

    def is_dir(self) -> bool:
        return Path(self.path()).is_dir()

    def download(self, dest: Union[str, Path]):
        if self.is_dir():
            shutil.copytree(str(self.path()), str(dest))
        else:
            shutil.copy(str(self.path()), str(dest))




