from pydantic import BaseModel, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional


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
    coverImage: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(from_attributes=True)


class PlaylistCreate(BaseModel):
    name: str
    idGenre: int = 1
    visibility: PlaylistVisibility = PlaylistVisibility.PUBLIC
    # idOwner: int  # TODO: À récupérer depuis le token JWT quand l'auth sera en place


class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    idGenre: Optional[int] = None
    visibility: Optional[PlaylistVisibility] = None
    model_config = ConfigDict(from_attributes=True)
