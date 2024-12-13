from typing import Annotated

from ..database import get_session
from sqlmodel import Session, select
from ..models import IllustBase, Illust, Restrict
from fastapi import Depends, APIRouter, Query
from ..dependencies import upload_img_server, get_server
from sqlalchemy import func

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/illusts",
    tags=["illusts"]
)

folder = "/pixiv/p_stars"
host = "192.168.3.3"
port = 8001

@router.post("/create/")
async def create_illust(
    illust: IllustBase,
    local_file_path: str,
    session: SessionDep, 
):
    db_illust = Illust.model_validate(illust)
    server_file_name = local_file_path.split("/")[-1]
    server_file_path = folder
    url = upload_img_server(host=host, port=port, 
                            local_file_path=local_file_path, 
                            server_file_name=server_file_name, 
                            server_file_path=server_file_path)
    db_illust.link = url
    session.add(db_illust)
    session.commit()
    session.refresh(db_illust)
    return db_illust

@router.get("/sfw")
async def read_sfw_illusts(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=300)] = 100,
    server: str = Depends(lambda: get_server(host=host, port=port))
):
    illusts = session.exec(select(Illust.link).where(Illust.restrict == Restrict.SFW).offset(offset).limit(limit)).all()
    results = [{"link": server + illust} for illust in illusts]
    return results

@router.get("/nsfw")
async def read__nsfw_illusts(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=300)] = 100,
    server: str = Depends(lambda: get_server(host=host, port=port))
):
    illusts = session.exec(select(Illust.link).where(Illust.restrict == Restrict.NSFW).offset(offset).limit(limit)).all()
    results = [{"link": server + illust} for illust in illusts]
    return results

@router.get("/r18")
async def read__r18_illusts(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=300)] = 100,
    server: str = Depends(lambda: get_server(host=host, port=port))
):
    illusts = session.exec(select(Illust.link).where(Illust.restrict == Restrict.R18).offset(offset).limit(limit)).all()
    results = [{"link": server + illust} for illust in illusts]
    return results

@router.get("/select")
async def read_illusts(
    session: SessionDep,
    sfw: bool = True, 
    nsfw: bool = False, 
    r18: bool = False,
    offset: int = 0,
    limit: Annotated[int, Query(le=300)] = 100,
    server: str = Depends(lambda: get_server(host=host, port=port))
):
    query = select(Illust.id, Illust.title, Illust.link, Illust.user)
    restrict_select = []
    if sfw:
        restrict_select.append(Restrict.SFW)
    if nsfw:
        restrict_select.append(Restrict.NSFW)
    if r18:
        restrict_select.append(Restrict.R18)
    query = query.where(Illust.restrict.in_(restrict_select)).offset(offset).order_by(func.RAND()).limit(limit)
    illusts = session.exec(query).all()
    results = [{
        "id": illust[0],
        "title": illust[1],
        "link": server + illust[2],
        "author": illust[3]
    } for illust in illusts]
    return results

@router.get("/links/all")
async def read_all_links(session: SessionDep):
    query = select(Illust.id, Illust.link)
    illusts = session.exec(query).all()
    results = [{
        "id": illust[0],
        "link": illust[1]
    } for illust in illusts]
    return results
    
@router.put("/update/link/{id}")
async def update_link(
    id: int,
    new_link: str,
    session: SessionDep
):
    query = select(Illust).where(Illust.id == id)
    illust = session.exec(query).one()
    illust.link = new_link
    session.add(illust)
    session.commit()
    session.refresh(illust)
    return illust
