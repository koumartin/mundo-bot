from typing import Annotated, Optional
from fastapi import Header, Depends


# Not the cleanest but since openapi-generator does not support not including it, then I have to do this
def __get_selected_guild(guild_id: Annotated[Optional[str], Header(include_in_schema=False)]):
    return int(guild_id) if guild_id else None


get_selected_guild_depends = Annotated[Optional[int], Depends(__get_selected_guild)]
