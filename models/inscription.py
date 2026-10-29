from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field, UniqueConstraint

#Les différents statuts de l'inscription.
class StatutInscription(str, Enum):
    """ Liste des statuts possible pour une inscription. """
    ENREGISTRE = "ENREGISTRE"
    DESINSCRIT = "DESINSCRIT"
    EN_ATTENTE = "EN_ATTENTE"

#Classe pour les inscriptions des apprenants aux sessions.
class Inscription(SQLModel, table=True):
    """ Informations pour les inscriptions des apprenants. """
    __table_args__ = (
        UniqueConstraint("apprenant_id", "session_id", name="unique_apprenant_session"),
    )
    id: int | None = Field(default=None, primary_key=True)
    apprenant_id: int = Field(foreign_key="apprenant.id")
    session_id: int = Field(foreign_key="session.id")
    date_inscription: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    statut_inscription:StatutInscription = Field(default=StatutInscription.ENREGISTRE)
    presence: Optional[bool] = None



