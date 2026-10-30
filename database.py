from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(DATABASE_URL, echo=True)

import models.user
import models.salle
import models.session
import models.inscription

def creer_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

if __name__ == "__main__":
    creer_tables()





