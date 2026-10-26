from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class StatutSession(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class Session(SQLModel, table=True):
    __tablename__ = "session"

    id: Optional[int] = Field(default=None, primary_key=True)
    titre: str = Field(max_length=100, nullable=False)
    description: Optional[str] = None
    date_debut: datetime = Field(nullable=False)
    date_fin: datetime = Field(nullable=False)
    capacite_max: int = Field(gt=0, nullable=False)
    statut: StatutSession = Field(default=StatutSession.OPEN)

    # Clés étrangères
    salle_id: int = Field(foreign_key="salle.id")
    formateur_id: int = Field(foreign_key="formateur.id")