from pydantic import BaseModel


def to_camel(string: str):
    parts = string.split("_")
    for index, _ in enumerate(parts):
        if index > 0:
            parts[index] = parts[index].capitalize()

    return "".join(parts)


class CamelBaseModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True

    def dict(self, by_alias=True, **kwargs):
        return super().dict(by_alias=by_alias, **kwargs)
