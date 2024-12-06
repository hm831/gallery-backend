from sqlmodel import SQLModel, Field

class AuthorBase(SQLModel):
    author_id: int
    name: str
    profile: str | None = None
    post: str | None = None
    description: str | None = None

class Author(AuthorBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

