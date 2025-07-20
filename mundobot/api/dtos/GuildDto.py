from pydantic import BaseModel


class GuildDto(BaseModel):
    id: str
    name: str
