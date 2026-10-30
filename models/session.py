from datetime import datetime
from enum import Enum
from typing import Optional, List, Union, Dict
from sqlmodel import SQLModel, Field, Column, JSON

#Les différents statuts possibles pour une session.
class StatutSession(str, Enum):
    """ Liste des statuts possibles pour une session. """

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"

#Classe pour les sessions de formation.
class Session(SQLModel, table=True):
    """ Informations sur les sessions de formation. """

    __tablename__ = "session"

    id: Optional[int] = Field(default=None, primary_key=True)
    titre: str = Field(max_length=100, nullable=False)
    description: Optional[str] = None
    date_debut: datetime = Field(nullable=False)
    date_fin: datetime = Field(nullable=False)
    capacite_max: int = Field(gt=0, nullable=False)
    statut: StatutSession = Field(default=StatutSession.OPEN)
    prerequis: Optional[Union[Dict, List[str]]] = Field(default=None, sa_column=Column(JSON))

    # Clés étrangères vers la salle et le formateur.
    salle_id: int = Field(foreign_key="salle.id")
    formateur_id: int = Field(foreign_key="formateur.id")