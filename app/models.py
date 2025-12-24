from pydantic import BaseModel, Field


class GameSearchResult(BaseModel):
    id: str
    title: str
    platform: str  # 'GOG' o 'Steam'
    supported_os: list[str] = Field(default_factory=list)


class GameVersionResult(BaseModel):
    version: str | None = None
    release_date: str | None = None
