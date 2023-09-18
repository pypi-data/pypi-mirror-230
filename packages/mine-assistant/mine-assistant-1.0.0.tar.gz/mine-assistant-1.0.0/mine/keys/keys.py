from typing import Any

from . import helper
from . import serializer
from .storage import Storage


__data: dict[str, Any] = helper.load_json()
serializer.load_schema(__data)


from . import schemas

Keys: schemas.KeyRecord = serializer.serialize(Storage.name, __data, schemas)
Storage.keys = Keys

del __data


def init(path: str):
    
    Storage.user_path = path
    
    data: dict[str, Any] = helper.load_json()
    serializer.load_schema(data)
    
    Storage.config.save()

    return data
