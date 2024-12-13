from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import create_db_and_tables
from .routers import albums, illusts, cosplays

@asynccontextmanager
async def lifespan(app: FastAPI):
   create_db_and_tables()
   yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(illusts.router)
app.include_router(albums.router)
app.include_router(cosplays.router)