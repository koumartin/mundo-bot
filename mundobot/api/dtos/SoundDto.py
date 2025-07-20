from pydantic import BaseModel


class SoundDto(BaseModel):
    name: str
    default: bool
