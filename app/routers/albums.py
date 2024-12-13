from typing import Annotated
import filetype

from ..database import get_session
from sqlmodel import Session, select
from sqlalchemy import desc, func, and_

from fastapi import Depends, APIRouter, Query, UploadFile, File, HTTPException
from ..dependencies import get_server, upload_img_server_file, upload_img_server

from ..models import Author, AuthorBase, Artwork, ArtworkBase, ArtworkRestrict

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/albums",
    tags = ["albums"]
)

folder = "/pixiv/p_users"
host = "192.168.3.3"
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

@router.put("/update/author/avatar/{author_id}", tags=["author"])
async def update_author_avatar(
    session: SessionDep,
    author_id: int,
    avatar_file: UploadFile = File()
):
    extension = filetype.guess_extension(avatar_file.file)
    server_file_name = f"{author_id}_avatar.{extension}"
    server_file_path = f"{folder}/{author_id}"
    author = session.exec(select(Author).where(Author.author_id == author_id)).one()
    avatar_url = upload_img_server_file(host=host, port=port, 
                                        local_file=avatar_file.file,
                                        server_file_name=server_file_name,
                                        server_file_path=server_file_path)
    author.avatar = avatar_url
    session.add(author)
    session.commit()
    session.refresh(author)
    return author

@router.put("/update/author/avatar/link/{author_id}", tags=["author"])
async def update_author_avatar_link(
    session: SessionDep,
    author_id: int,
    avatar: str
):
    author = session.exec(select(Author).where(Author.author_id == author_id)).one()
    author.avatar = avatar
    session.add(author)
    session.commit()
    session.refresh(author)
    return author

@router.put("/update/author/cover/{author_id}", tags=["author"])
async def update_author_cover(
    session: SessionDep,
    author_id: int,
    cover_file: UploadFile = File()
):
    extension = filetype.guess_extension(cover_file.file)
    server_file_name = f"{author_id}_cover.{extension}"
    server_file_path = f"{folder}/{author_id}"
    author = session.exec(select(Author).where(Author.author_id == author_id)).one()
    cover_url = upload_img_server_file(host=host, port=port, 
                                       local_file=cover_file.file,
                                       server_file_name=server_file_name, 
                                       server_file_path=server_file_path)
    author.cover = cover_url
    session.add(author)
    session.commit()
    session.refresh(author)
    return author

@router.put("/update/author/cover/link/{author_id}", tags=["author"])
async def update_author_cover(
    session: SessionDep,
    author_id: int,
    cover: str
):
    author = session.exec(select(Author).where(Author.author_id == author_id)).one()
    author.cover = cover
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
    query = select(Author.name, Author.avatar, Author.cover, Author.author_id).offset(offset).limit(limit)
    authors = session.exec(query).all()
    results = [{
        "name": author[0],
        "avatar": server + author[1],
        "cover": server + author[2],
        "authorId": author[3]
    } for author in authors]
    return results

@router.post("/create/artwork/", tags=["artwork"])
async def create_artwork(
    artwork: ArtworkBase, 
    local_file_path: str,
    session: SessionDep
):
    db_artwork = Artwork.model_validate(artwork)
    query = select(Artwork).where(and_(Artwork.page_index == artwork.page_index, Artwork.p_id == db_artwork.p_id))
    if (session.exec(query).first() == None):
        server_file_name = local_file_path.split("/")[-1]
        server_file_path = f"{folder}/{db_artwork.user_id}"
        url = upload_img_server(host=host, port=port, 
                                local_file_path=local_file_path, 
                                server_file_name=server_file_name,
                                server_file_path=server_file_path)
        db_artwork.link = url
        session.add(db_artwork)
        session.commit()
        session.refresh(db_artwork)
        return db_artwork
    else:
        raise HTTPException(
            status_code = 409,
            detail = "Resource already exists"
        )

@router.get("/artwork/{author_id}", tags=["artwork"])
async def read_author_artworks(
    author_id: int, 
    session: SessionDep, 
    server: str = Depends(lambda: get_server(host=host, port=port))
):
    query = select(Artwork.id, Artwork.title, Artwork.link, Artwork.p_id, Artwork.page_index)
    query = query.where(Artwork.user_id == author_id)
    query = query.order_by(desc(Artwork.date))
    artworks = session.exec(query).all()
    results = [{
        "id": artwork[0],
        "title": artwork[1],
        "link": server + artwork[2],
        "p_id": artwork[3],
        "page_index": artwork[4]
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

@router.put("/update/artwork/link/{artwork_id}")
async def update_artwork_link(
    artwork_id: int,
    new_link: str,
    session: SessionDep
):
    query = select(Artwork).where(Artwork.id == artwork_id)
    artwork = session.exec(query).one()
    artwork.link = new_link
    session.add(artwork)
    session.commit()
    session.refresh(artwork)
    return artwork
