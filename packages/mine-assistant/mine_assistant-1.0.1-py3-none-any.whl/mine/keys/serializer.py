from typing import Any

from . import helper
from .storage import Storage
from .base import Base, KeyBase, StrBase, base_vars


def write_schema(name: str, data: str | dict[str, Any], fp) -> None:
    
    if isinstance(data, str):
        return
    
    schema: str = (
        "\n\n@dataclass(kw_only=True)\n"
        "class {name}({bases}):\n"
        "{body}"
    )
    
    body: str = ""

    for param, value in data.items():
        
        if param not in base_vars:
            
            param = helper.get_param_name(param)
            body += f"\t{param}: {helper.get_class_name(param, value)}\n"
            write_schema(param, value, fp)
    
    fp.write(schema.format(
        name = helper.get_class_name(name),
        bases = KeyBase.__name__,
        body = body or "\t...\n"
    ))


def serialize(name: str, data: str | dict[str, Any], schemas) -> Base:
    
    if isinstance(data, str):
        return StrBase(data)
    
    env: str = data.pop("ENV", None)

    model: type[KeyBase] = getattr(schemas, helper.get_class_name(name))
    obj: KeyBase = model(**{
        helper.get_param_name(param): serialize(param, value, schemas)
        for param, value in data.items()
    }).set_parent()
    
    obj.ENV = env
    
    return obj


def load_schema(data: dict[str, Any]) -> None:
    
    with open(Storage.schema_path, 'w') as fp:
        
        fp.write(
            "# Generated classes for type hints\n"
            "from dataclasses import dataclass\n\n"
            f"from .base import {KeyBase.__name__}, {StrBase.__name__}\n"
        )
        
        write_schema(Storage.name, data, fp)
