from pathlib import Path
from typing import Optional, Union
import os

from vatis.asr_commons.config.logging import get_logger

from .stored_object import StoredObject, ObjectUrl

logger = get_logger(__name__)

AWS_S3_ACCESS_KEY_ID_KEY: str = 'AWS_S3_ACCESS_KEY_ID'
AWS_S3_SECRET_ACCESS_KEY_KEY: str = 'AWS_S3_SECRET_ACCESS_KEY'
AWS_ACCESS_KEY_ID_DEFAULT_KEY: str = 'AWS_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY_DEFAULT_KEY: str = 'AWS_SECRET_ACCESS_KEY'
AWS_S3_REGION_KEY: str = 'AWS_S3_REGION'

DEFAULT_AWS_S3_REGION: str = 'eu-central-1'

SYMLINK_HEADER_KEY: str = 'x-vat-symlink-key'

AWS_ACCESS_KEY_ID: Optional[str] = None
AWS_SECRET_ACCESS_KEY: Optional[str] = None
AWS_S3_REGION: Optional[str] = None

try:
    import boto3
    from botocore.exceptions import ClientError
except ModuleNotFoundError as e:
    logger.error("Install boto3 dependency")
    raise e

try:
    if AWS_S3_ACCESS_KEY_ID_KEY in os.environ:
        AWS_ACCESS_KEY_ID = os.environ[AWS_S3_ACCESS_KEY_ID_KEY]
    elif AWS_ACCESS_KEY_ID_DEFAULT_KEY in os.environ:
        AWS_ACCESS_KEY_ID = os.environ[AWS_ACCESS_KEY_ID_DEFAULT_KEY]
    else:
        raise KeyError()

    if AWS_S3_SECRET_ACCESS_KEY_KEY in os.environ:
        AWS_SECRET_ACCESS_KEY = os.environ[AWS_S3_SECRET_ACCESS_KEY_KEY]
    elif AWS_SECRET_ACCESS_KEY_DEFAULT_KEY in os.environ:
        AWS_SECRET_ACCESS_KEY = os.environ[AWS_SECRET_ACCESS_KEY_DEFAULT_KEY]
    else:
        raise KeyError()

    AWS_S3_REGION = os.environ.get(AWS_S3_REGION_KEY, DEFAULT_AWS_S3_REGION)
except KeyError as e:
    logger.error("AWS credentials not set")
    raise e


try:
    session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                    region_name=AWS_S3_REGION)
except Exception as e:
    logger.error(f'Error creating S3 session: {str(e)}')
    raise e


class S3Object(StoredObject):
    def __init__(self, url: ObjectUrl):
        super().__init__(url)

        self._s3 = session.resource('s3')
        self._exists: bool = True
        self._is_dir: bool = False
        self._object = None

        file_object = self._s3.Object(bucket_name=url.bucket, key=url.path)

        try:
            file_object.load()
            self._object = file_object
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                dir_object = self._s3.Object(bucket_name=url.bucket, key=url.path + '/')

                try:
                    dir_object.load()
                    self._object = dir_object
                    self._is_dir = True
                except ClientError as e2:
                    if e2.response['Error']['Code'] == "404":
                        self._exists = False
                    else:
                        raise e2
            else:
                raise e

    def exists(self, follow_symlinks: bool = True) -> bool:
        if not self._exists:
            return False

        original_object: 'S3Object' = self._fetch_original_object() if follow_symlinks else self

        return original_object._exists

    def size(self, follow_symlinks: bool = True) -> int:
        if not self.exists():
            return 0

        original_object: 'S3Object' = self._fetch_original_object() if follow_symlinks else self

        size: int = original_object._object.content_length

        if original_object.is_dir(follow_symlinks=follow_symlinks):
            bucket = original_object._s3.Bucket(original_object.bucket())
            prefix: str = original_object.url().path + '/'

            for obj in bucket.objects.filter(Prefix=prefix):
                if obj.key != prefix:
                    obj_url: ObjectUrl = S3Object.build_url(obj.bucket_name, obj.key)
                    s3_obj: 'S3Object' = S3Object(obj_url)

                    size += s3_obj.size(follow_symlinks=follow_symlinks)

        return size

    def is_dir(self, follow_symlinks: bool = True) -> bool:
        if not self.exists():
            return False

        original_object: 'S3Object' = self._fetch_original_object() if follow_symlinks else self

        return original_object._is_dir

    def is_symlink(self) -> bool:
        if not self._exists:  # prevent infinite recursion
            return False

        metadata = self._object.metadata

        return metadata is not None and \
               SYMLINK_HEADER_KEY in metadata and \
               metadata[SYMLINK_HEADER_KEY] is not None and \
               metadata[SYMLINK_HEADER_KEY] != ''

    def get_original_object(self) -> 'S3Object':
        if not self.exists():
            return self

        return self._fetch_original_object()

    def _fetch_original_object(self) -> 'S3Object':
        original_object: 'S3Object' = self

        while original_object.is_symlink():
            metadata = original_object._object.metadata
            original_key: str = metadata[SYMLINK_HEADER_KEY]
            original_url: ObjectUrl = S3Object.build_url(original_object.bucket(), original_key)

            original_object = S3Object(original_url)

        return original_object

    def path(self, follow_symlinks: bool = True) -> Path:
        if not self.exists():
            return Path(self._url.path)

        original_object: 'S3Object' = self._fetch_original_object() if follow_symlinks else self

        return Path(original_object.url().path)

    def name(self, follow_symlinks: bool = True) -> str:
        if not self.exists():
            return super().name()

        original_object: 'S3Object' = self._fetch_original_object() if follow_symlinks else self

        return original_object.path(follow_symlinks=follow_symlinks).name

    @staticmethod
    def build_url(bucket: str, key: str) -> ObjectUrl:
        return ObjectUrl(f's3://{bucket}/{key}')

    def download(self, dest: Union[str, Path]):
        if not self.exists():
            return

        dest = str(dest)

        if self.is_symlink():
            original_object: 'S3Object' = self.get_original_object()
            original_object.download(dest)
        elif self.is_dir():
            Path(dest).mkdir(parents=True, exist_ok=True)

            bucket = self._s3.Bucket(self.bucket())
            prefix: str = self.url().path + '/'

            for obj in bucket.objects.filter(Prefix=prefix):
                rel_key: str = obj.key[len(prefix):]

                if rel_key == '':
                    continue

                obj_url: ObjectUrl = S3Object.build_url(obj.bucket_name, obj.key)
                s3_obj: 'S3Object' = S3Object(obj_url)
                obj_dest: str = dest + ('' if dest.endswith('/') else '/') + rel_key

                s3_obj.download(obj_dest)
        else:
            if Path(dest).exists():
                dest = str(Path(dest, self.name()))

            self._object.download_file(dest)
