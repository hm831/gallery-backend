from sqlmodel import SQLModel, Field
from fastapi import UploadFile

class CosplayBase(SQLModel):
    title: str
    author_id: int

class Cosplay(CosplayBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class CosplayPhotoBase(SQLModel):
    cosplay_id: int
    page_index: int

class CosplayPhoto(CosplayPhotoBase, table=True):
    __tablename__ = "cosplay_photo"
    link: str = None
    id: int | None = Field(default=None, primary_key=True)

class CosplayAuthorBase(SQLModel):
    name: str
    x_name: str | None = None
    x_id: str | None = None
    link: str | None = None
    profile: str | None = None

class CosplayAuthor(CosplayAuthorBase, table=True):
    __tablename__ = "cosplay_author"
    id: int | None = Field(default=None, primary_key=True)