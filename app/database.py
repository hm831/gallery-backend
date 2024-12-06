from sqlmodel import Session, create_engine
from .models import Illust

mysql_url = "mysql+pymysql://root:@localhost:3306/gallery"
engine = create_engine(mysql_url)

def create_db_and_tables():
    Illust.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session