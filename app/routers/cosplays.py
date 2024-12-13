from typing import Annotated
import filetype

from ..database import get_session
from sqlmodel import Session, select
from sqlalchemy import desc, func

from fastapi import Depends, APIRouter, Query, UploadFile, File, Form
from ..dependencies import get_server, upload_img_server_file, upload_img_server

from ..models import Cosplay, CosplayBase, CosplayAuthor, CosplayAuthorBase, CosplayPhoto, CosplayPhotoBase
from urllib.parse import quote

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix = "/cosplays",
    tags = ["cosplays"]
)

folder = "/cosplay"
host = "192.168.3.3"
port = 8001

@router.post("/create/author", tags=["cosplay_author"])
async def create_author(
    author: CosplayAuthorBase,
    session: SessionDep
):
    db_author = CosplayAuthor.model_validate(author)
    session.add(db_author)
    session.commit()
    session.refresh(db_author)
    return db_author

@router.post("/create/cosplay")
async def create_cosplay(
    cosplay: CosplayBase,
    session: SessionDep
):
    db_cosplay = Cosplay.model_validate(cosplay)
    session.add(db_cosplay)
    session.commit()
    session.refresh(db_cosplay)
    return db_cosplay

@router.post("/create/photo", tags=["cosplay_photo"])
async def create_photo(
    cosplay_id: int,
    page_index: int,
    author_name: str,
    cosplay_title: str,
    file: UploadFile,
    session: SessionDep
):
    photo = CosplayPhotoBase(cosplay_id=cosplay_id, page_index=page_index)
    db_photo = CosplayPhoto.model_validate(photo)
    extension = filetype.guess_extension(file.file)
    server_file_name = f"{cosplay_id}_p{page_index}.{extension}"
    server_file_path = f"{folder}/{author_name}/{cosplay_title}"
    url = upload_img_server_file(host=host, port=port, 
                                 local_file=file.file, 
                                 server_file_name=server_file_name, 
                                 server_file_path=server_file_path)
    db_photo.link = url
    session.add(db_photo)
    session.commit()
    session.refresh(db_photo)
    return db_photo

@router.put("/update/photo/link/{photo_id}")
async def update_photo_link(
    photo_id: int,
    link: str,
    session: SessionDep
):
    query = select(CosplayPhoto).where(CosplayPhoto.id == photo_id)
    photo = session.exec(query).one()
    photo.link = link
    session.add(photo)
    session.commit()
    session.refresh(photo)
    return photo

@router.get("/photos/{cosplay_id}", tags=["cosplay_photo"])
async def read_photos(
    cosplay_id: int,
    session: SessionDep,
    server: str = Depends(lambda: get_server(host=host, port=port))
):
    query = select(CosplayPhoto.link, CosplayPhoto.page_index, CosplayPhoto.id).where(CosplayPhoto.cosplay_id == cosplay_id)
    photos = session.exec(query).all()
    results =  [{
        "link": server + quote(photo[0]),
        "page_index": photo[1],
        "id": photo[2]
    } for photo in photos]
    return results


@router.get("/select")
async def read_cosplays(
    session: SessionDep,
    server: str = Depends(lambda: get_server(host=host, port=port))
):
    query = select(Cosplay.id, Cosplay.title, CosplayAuthor.name, CosplayPhoto.link)
    query = query.join(CosplayAuthor, Cosplay.author_id == CosplayAuthor.id)
    query = query.join(CosplayPhoto, Cosplay.id == CosplayPhoto.cosplay_id)
    query = query.where(CosplayPhoto.page_index == 0)
    cosplays = session.exec(query).all()
    results = [{
        "id": cosplay[0],
        "title": cosplay[1],
        "author": cosplay[2],
        "cover": server + quote(cosplay[3])
    } for cosplay in cosplays]
    return results

@router.get("/gallery/select")
async def read_gallery(
    session: SessionDep,
    limit: Annotated[int, Query(le=300)] = 100,
    server: str = Depends(lambda: get_server(host=host, port=port))
):
    query = select(CosplayPhoto.id, CosplayPhoto.link).order_by(func.RAND()).limit(limit)
    photos = session.exec(query).all()
    results = [{
        "id": photo[0],
        "link": server + quote(photo[1])
    } for photo in photos]
    return results

# @router.get("/author/select/{author_name}")
# async def read_author(
#     author_name: str,
#     session: SessionDep
# )
