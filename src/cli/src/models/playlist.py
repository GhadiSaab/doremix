from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class PlaylistVisibility(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    SHARED = "SHARED"


class PlaylistSchema(BaseModel):
    idPlaylist: int
    name: str
    idGenre: int
    idOwner: int
    vote: int
    visibility: PlaylistVisibility
    coverImage: str | None = None
    createdAt: datetime
    updatedAt: datetime
