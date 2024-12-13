from sqlmodel import SQLModel, Field

class AuthorBase(SQLModel):
    author_id: int
    name: str

class Author(AuthorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    avatar: str | None = None
    cover: str | None = None
    description: str | None = None

