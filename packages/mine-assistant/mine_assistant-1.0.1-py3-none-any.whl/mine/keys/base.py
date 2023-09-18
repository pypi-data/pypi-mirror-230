from __future__ import annotations

import os
import json
from typing import Any

from . import helper


base_vars: list[str] = ["ENV", "PARENT"]


class Base:

    PARENT: KeyBase | None = None


class KeyBase(Base):
    
    ENV: str | None = None

    def set_parent(self) -> KeyBase:

        for value in self.__dict__.values():
            
            if isinstance(value, Base):
                value.PARENT = self
        
        return self
    
    def dict(self) -> dict[str, Any]:
        
        return {
            helper.get_json_key(param): value.dict() if isinstance(value, KeyBase) else value
            for param, value in self.__dict__.items() if param != "PARENT"
        }

    def json(self) -> str:
        return json.dumps(self.dict(), indent=4)
    
    def set(self, param: str) -> None:

        try:
            value: StrBase = getattr(self, helper.get_param_name(param))

            if not isinstance(value, StrBase) and value:
                raise ValueError(f"Value of '{param}' is not a non-empty string")
        
        except AttributeError:
            raise AttributeError(f"Key '{param}' not found in '{self.__class__.__name__}'")
        
        if self.ENV is None:
            raise KeyError(f"ENV key not found for '{self.__class__.__name__}'")
        
        os.environ[self.ENV] = value
    
    def get(self) -> str:
        return self.ENV and os.environ.get(self.ENV)
    
    def config(self, env: str = ...) -> str:
        
        if env not in (self.ENV, ...):
            
            self.ENV = env
            helper.save_json()
        
        return self.ENV


class StrBase(str, Base):
    
    def set(self) -> None:
        
        if self.PARENT.ENV is None:
            raise KeyError(f"ENV key not found for '{self.__class__.__name__}'")
        
        os.environ[self.PARENT.ENV] = self
