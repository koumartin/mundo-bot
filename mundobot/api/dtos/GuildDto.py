from pydantic import BaseModel


class GuildDto(BaseModel):
    id: int
    name: str
