from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum

class Restrict(str, Enum):
    SFW = "SFW"
    NSFW = "NSFW"
    R18 = "R18"

class IllustBase(SQLModel):
    p_id: int #pixivId
    page: int #页数
    page_index: int = 0
    restrict: Restrict #敏感内容分类
    link: str | None = None #图片url
    title: str #图片名
    tags: str
    user: str #作者名
    user_id: int
    description: str
    date: datetime #图片pixiv上传日期
    width: int
    height: int
    bookmark: bool
    bmk_id: str | None = Field(default=None, index=True) #收藏夹id，id越大表示越近收藏

class Illust(IllustBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
