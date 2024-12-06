from typing import Annotated

from ..database import get_session
from sqlmodel import Session, select
from fastapi import Depends, APIRouter, Query, UploadFile, File, Form
from ..dependencies import get_server, upload_img_server_file
from ..models import Author, AuthorBase

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/portfolios",
    tags = ["portfolios"]
)

host = "127.0.0.1"
port = 8001

@router.post("/create/author/")
async def create_author(
    author: AuthorBase,
    session: SessionDep
):
    db_author = Author.model_validate(author)
    session.add(db_author)
    session.commit()
    session.refresh(db_author)
    return db_author

@router.put("/update/author/profile/{author_id}")
async def update_author_profile(
    session: SessionDep,
    author_id: int,
    profile_file: UploadFile = File()
):
    author = session.exec(select(Author).where(Author.author_id == author_id)).one()
    profile_url = upload_img_server_file(host=host, port=port, file=profile_file.file)
    author.profile = profile_url
    session.add(author)
    session.commit()
    session.refresh(author)
    return author

@router.put("/update/author/post/{author_id}")
async def update_author_post(
    session: SessionDep,
    author_id: int,
    post_file: UploadFile = File()
):
    author = session.exec(select(Author).where(Author.author_id == author_id)).one()
    post_url = upload_img_server_file(host=host, port=port, file=post_file.file)
    author.post = post_url
    session.add(author)
    session.commit()
    session.refresh(author)
    return author

@router.get("/author/info/select")
async def read_author_info(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=300)] = 100,
    server: str = Depends(lambda: get_server(host=host, port=port))
):
    authors = session.exec(select(Author.name, Author.profile, Author.post).offset(offset).limit(limit)).all()
    results = [{
        "name": author[0],
        "profile": server + author[1],
        "post": server + author[2]
    } for author in authors]
    return results