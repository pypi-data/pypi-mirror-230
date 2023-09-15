from typing import TypeVar

from pydantic import BaseModel, create_model

M = TypeVar("M", bound=BaseModel)


class Settings(BaseModel):
    pass

    @classmethod
    def create_combined_model(cls, *settings: type["Settings"]) -> type["Settings"]:
        field_definitions = {}
        for setting in settings:
            for name, field in setting.__fields__.items():
                field_definitions[name] = (field.annotation, field.default)

        return create_model(cls.__name__, __base__=(cls), **field_definitions)
