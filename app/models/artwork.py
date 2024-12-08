from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum

class ArtworkRestrict(str, Enum):
    AllAges =  "AllAges"
    R18 =  "R-18" 

class ArtworkBase(SQLModel):
    p_id: int #pixivId
    page: int #页数
    page_index: int = 0
    link: str | None = None #图片url
    title: str #图片名
    tags: str
    user_id: int
    description: str | None = None
    restrict_type: ArtworkRestrict
    date: datetime #图片pixiv上传日期
    width: int
    height: int

class Artwork(ArtworkBase, table=True):
    id: int | None = Field(default=None, primary_key=True)