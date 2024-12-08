from typing import Annotated

from ..database import get_session
from sqlmodel import Session, select
from sqlalchemy import desc, func

from fastapi import Depends, APIRouter, Query, UploadFile, File, Form
from ..dependencies import get_server, upload_img_server_file, upload_img_server

from ..models import Author, AuthorBase, Artwork, ArtworkBase, ArtworkRestrict

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/albums",
    tags = ["albums"]
)

host = "127.0.0.1"
port = 8001

@router.post("/create/author/",  tags=["author"])
async def create_author(
    author: AuthorBase,
    session: SessionDep
):
    db_author = Author.model_validate(author)
    session.add(db_author)
    session.commit()
    session.refresh(db_author)
    return db_author

@router.put("/update/author/profile/{author_id}", tags=["author"])
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

@router.put("/update/author/post/{author_id}", tags=["author"])
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

@router.get("/author/info/select", tags=["author"])
async def read_author_info(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=300)] = 100,
    server: str = Depends(lambda: get_server(host=host, port=port))
):
    query = select(Author.name, Author.profile, Author.post, Author.author_id).offset(offset).limit(limit)
    authors = session.exec(query).all()
    results = [{
        "name": author[0],
        "profile": server + author[1],
        "post": server + author[2],
        "authorId": author[3]
    } for author in authors]
    return results

@router.post("/create/artwork/", tags=["artwork"])
async def create_artwork(artwork: ArtworkBase, file_path: str, session: SessionDep):
    db_artwork = Artwork.model_validate(artwork)
    url = upload_img_server(host=host, port=port, file_path=file_path)
    db_artwork.link = url
    session.add(db_artwork)
    session.commit()
    session.refresh(db_artwork)
    return db_artwork

@router.get("/artwork/{author_id}", tags=["artwork"])
async def read_author_artworks(
    author_id: int, 
    session: SessionDep, 
    server: str = Depends(lambda: get_server(host=host, port=port))
):
    query = select(Artwork.id, Artwork.title, Artwork.link)
    query = query.where(Artwork.user_id == author_id)
    query = query.order_by(desc(Artwork.date))
    artworks = session.exec(query).all()
    results = [{
        "id": artwork[0],
        "title": artwork[1],
        "link": server + artwork[2]
    } for artwork in artworks]
    return results

@router.get("/artwork/gallery/select", tags=["artwork"])
async def read_artwork_gallery(
    session: SessionDep, 
    allage: bool = True,
    r18: bool = False,
    limit: Annotated[int, Query(le=300)] = 100,
    server: str = Depends(lambda: get_server(host=host, port=port))
):
    query = select(Artwork.id, Artwork.title, Artwork.link, Author.name)
    query = query.join(Author, Artwork.user_id == Author.author_id)
    restrict_select = []
    if allage:
        restrict_select.append(ArtworkRestrict.AllAges)
    if r18:
        restrict_select.append(ArtworkRestrict.R18)
    query = query.where(Artwork.restrict_type.in_(restrict_select))
    query = query.order_by(func.RAND()).limit(limit)
    artworks = session.exec(query).all()
    results = [{
        "id": artwork[0],
        "title": artwork[1],
        "link": server + artwork[2],
        "author": artwork[3]
    } for artwork in artworks]
    return results

