import os
import json
from typing import Any

from .storage import Storage


def get_class_name(name: str, value: str | dict[str, Any] = None) -> str:
    
    if isinstance(value, str):
        
        from .base import StrBase
        return StrBase.__name__

    return name.title().replace('_', '').replace('-', '')


def get_param_name(name: str) -> str:
    
    return name.replace('-', '_').lower()


def get_json_key(name) -> str:
    
    return name.replace('_', '-')


def load_json() -> dict[str, Any]:
    
    file: str = Storage.user_path
    
    if os.path.exists(file):

        with open(file) as fp:
            
            try:
                return json.load(fp)
            
            except json.decoder.JSONDecodeError:
                raise SyntaxError(f"File already exists with invalid JSON content at '{file}'")
    
    data: dict[str, Any] = {}
    
    with open(file, 'w') as fp:
        json.dump(data, fp)
    
    return data


def save_json() -> None:
    
    with open(Storage.user_path, 'w') as fp:
        json.dump(Storage.keys.dict(), fp, indent=4)
