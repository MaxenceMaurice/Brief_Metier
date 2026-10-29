from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field, UniqueConstraint

class StatutInscription(str, Enum):
    ENREGISTRE = "ENREGISTRE"
    DESINSCRIT = "DESINSCRIT"
    EN_ATTENTE = "EN_ATTENTE"

class Inscription(SQLModel, table=True):
    # Ajout de la contrainte d'unicité sur le couple apprenant / session
    __table_args__ = (
        UniqueConstraint("apprenant_id", "session_id", name="unique_apprenant_session"),
    )
    id: int | None = Field(default=None, primary_key=True)
    apprenant_id: int = Field(foreign_key="apprenant.id")
    session_id: int = Field(foreign_key="session.id")
    date_inscription: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    statut_inscription:StatutInscription = Field(default=StatutInscription.ENREGISTRE)
    presence: Optional[bool] = None



