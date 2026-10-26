from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field

class StatutInscription(str, Enum):
    ENREGISTRE = "ENREGISTRE"
    DESINSCRIT = "DESINSCRIT"
    EN_ATTENTE = "EN_ATTENTE"

class Inscription(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    apprenant_id: int = Field(foreign_key="apprenant.id")
    session_id: int = Field(foreign_key="session.id")
    date_inscription: datetime = Field(default_factory=datetime.now)
    statut_inscription:StatutInscription = Field(default=StatutInscription.ENREGISTRE)
    presence: Optional[bool] = None



