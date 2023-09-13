from pathlib import Path
from typing import Union

from .stored_object import ObjectUrl, StoredObject


def get_object(url: Union[str, Path]) -> StoredObject:
    object_url: ObjectUrl = ObjectUrl(url)

    if object_url.local_url:
        from .local_object import LocalObject

        return LocalObject(object_url)
    elif object_url.scheme == 's3':
        from .s3_object import S3Object

        return S3Object(object_url)
    else:
        raise TypeError(f'Unknown type: {str(url)}')
