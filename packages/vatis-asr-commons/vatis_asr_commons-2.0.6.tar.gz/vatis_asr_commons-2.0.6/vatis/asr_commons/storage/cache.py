import os
from pathlib import Path
from threading import RLock

from readerwriterlock.rwlock import RWLockFair
from typing import Union, Dict, Optional, List
import jsonpickle
import shutil

from vatis.asr_commons.config.logging import get_logger, execution_time

from vatis.asr_commons.utils import parse
from vatis.asr_commons.utils.file import get_size

from vatis.asr_commons.storage.store import get_object, StoredObject
from vatis.asr_commons.storage.exception import CacheFullException

logger = get_logger(__name__)


class CacheRegistry:
    REGISTRY_FILE: str = '.registry.json'

    def __init__(self, cache_dir: str):
        self._cache_dir: str = cache_dir
        self._lock: RWLockFair = RWLockFair()

        self._registry: Dict[str, str] = self._load_registry()

    def _load_registry(self) -> Dict[str, str]:
        registry_file: Path = Path(self._cache_dir, CacheRegistry.REGISTRY_FILE)

        if registry_file.exists():
            try:
                with open(registry_file, 'r') as file:
                    lines: List[str] = file.readlines()
                    json_registry: str = ''.join(lines)

                    registry = jsonpickle.decode(json_registry)

                    if not isinstance(registry, Dict):
                        raise ValueError(f'Bad deserialized type: {str(type(registry))}')

                    logger.info(f'Successfully loaded cache: {str(registry)}')

                    return registry
            except Exception as e:
                logger.exception('Corrupted registry cache. Will be deleted: %s', str(e))
                return {}
        else:
            return {}

    def _dump_registry(self):
        registry_file: Path = Path(self._cache_dir, CacheRegistry.REGISTRY_FILE)

        json_registry: str = jsonpickle.encode(self._registry)

        with open(registry_file, 'w') as file:
            file.write(json_registry)

    def get(self, key: str) -> str:
        with self._lock.gen_rlock():
            return self._registry.get(key)

    def add(self, key: str, value: str, override: bool = True) -> Optional[str]:
        """
        Adds synchronously an entry in _registry.
        If an entry with the same key already exists and override is set to False, ValueError is raised
        :param key: key
        :param value: value
        :param override: override if a value exists
        :return: overridden value
        :raises ValueError for duplicate key and override=False
        """
        with self._lock.gen_wlock():
            if key in self._registry and not override:
                raise ValueError(f'Duplicate key: {key}')

            overridden_value: Optional[str] = self._registry.get(key)

            self._registry[key] = value
            self._dump_registry()

            return overridden_value

    def pop(self, key: str) -> Optional[str]:
        with self._lock.gen_wlock():
            if key in self._registry:
                item: str = self._registry.pop(key)
                self._dump_registry()
                return item
            else:
                return None

    def evict(self):
        with self._lock.gen_wlock():
            registry_file: Path = Path(self._cache_dir, CacheRegistry.REGISTRY_FILE)

            if registry_file.exists():
                os.remove(registry_file)
            self._registry = {}

    def get_all(self) -> Dict[str, str]:
        with self._lock.gen_rlock():
            return self._registry.copy()


class ModelsCache:
    def __init__(self, cache_dir: Union[str, Path], cache_max_size: str, disable_cache: bool = False):
        assert cache_dir is not None

        self._cache_dir_path: Path = Path(cache_dir)

        if self._cache_dir_path.is_file():
            raise ValueError(f'{str(self._cache_dir_path)} points to a file')

        self._cache_dir_path.mkdir(exist_ok=True, parents=True)
        self._cache_max_size: int = parse.parse_memory(cache_max_size)
        self._current_cache_size = get_size(self._cache_dir_path)
        self._registry = CacheRegistry(str(self._cache_dir_path))
        self._file_locks_lock: RLock = RLock()
        self._file_locks: Dict[str, RLock] = {}
        self._size_lock: RLock = RLock()
        self._disable_cache: bool = disable_cache

    @execution_time
    def cache_and_get(self, model_path: Union[str, Path]) -> Path:
        stored_object: StoredObject = get_object(model_path)

        if self._disable_cache and stored_object.local():
            return Path(model_path)

        absolute_model_path: Path = stored_object.path()
        cached_model_path: str = self._registry.get(str(absolute_model_path))

        if cached_model_path is not None:
            return Path(cached_model_path)
        else:
            model_path: Path = absolute_model_path

            if not stored_object.exists():
                raise ValueError(f'Object {str(stored_object)} doesn\'t exist')

            model_size: int = stored_object.size()

            if model_size + self._current_cache_size > self._cache_max_size:
                logger.warning(f'Cache is full ({str(self._current_cache_size)})')

                if not stored_object.local():
                    raise CacheFullException()
                else:
                    return model_path
            else:
                self._current_cache_size += model_size

                try:
                    file_name: str = model_path.name
                    cached_file_path: Path = Path(self._cache_dir_path, file_name).absolute()

                    with self._file_locks_lock:
                        cached_file_path_str: str = str(cached_file_path)
                        if cached_file_path_str not in self._file_locks:
                            self._file_locks[cached_file_path_str] = RLock()
                        file_lock: RLock = self._file_locks[cached_file_path_str]

                    with file_lock:
                        if not cached_file_path.exists():
                            stored_object.download(cached_file_path)

                            logger.info(f'Cached {str(model_path)} into {str(cached_file_path)}')

                        self._registry.add(str(model_path), str(cached_file_path))

                    return cached_file_path
                except Exception as e:
                    self._current_cache_size -= model_size
                    raise e

    def get_all(self) -> Dict[str, str]:
        return self._registry.get_all()

    def get(self, key: str) -> Optional[str]:
        return self._registry.get(key)

    def remove(self, key: str):
        cached_model_path: str = self._registry.pop(key)

        if cached_model_path is not None:
            with self._file_locks_lock:
                if cached_model_path not in self._file_locks:
                    self._file_locks[cached_model_path] = RLock()
                file_lock: RLock = self._file_locks[cached_model_path]

            with file_lock:
                cached_model_path: Path = Path(cached_model_path)
                cached_model_size: int = get_size(cached_model_path)

                if cached_model_path.is_file():
                    os.remove(str(cached_model_path))
                    logger.info('Removed cached model file: %s', str(cached_model_path))
                elif cached_model_path.is_dir():
                    cached_model_path.rmdir()
                    logger.info('Removed cached model dir: %s', str(cached_model_path))

                self._current_cache_size -= cached_model_size

            with self._file_locks_lock:
                self._file_locks.pop(str(cached_model_path))

    def evict(self):
        self._registry.evict()
        shutil.rmtree(self._cache_dir_path)
        self._file_locks = {}
        self._current_cache_size = 0

    @property
    def cache_size(self) -> int:
        return self._current_cache_size

    @property
    def max_cache_size(self) -> int:
        return self._cache_max_size
