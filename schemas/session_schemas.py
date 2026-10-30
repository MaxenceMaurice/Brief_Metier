
from datetime import datetime
from typing import Optional, Dict, List, Union
from pydantic import BaseModel, Field, model_validator
from models.session import StatutSession

#Classe pour créer une session de formation.
class SessionCreate(BaseModel):
    """ Informations nécessaires pour créer une session. """

    titre: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    date_debut: datetime
    date_fin: datetime
    capacite_max: int = Field(gt=0)
    statut: StatutSession = StatutSession.OPEN
    salle_id: int
    formateur_id: int
    prerequis: Optional[Union[Dict, List[str]]] = None

    #Vérifie que la date de fin est après la date qui à commencer.
    @model_validator(mode="after")
    def verifier_dates(self) -> "SessionCreate":
        """ Vérifie les dates lors de la création d'une session.  """

        if self.date_debut >= self.date_fin:
            raise ValueError("La date de fin doit être supérieure à la date de début.")
        return self

#Classe pour modifier une session de formation.
class SessionUpdate(BaseModel):
    """ Informations nécessaires pour modifier une session. """

    titre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    capacite_max: Optional[int] = Field(default=None, gt=0)
    statut: Optional[StatutSession] = None
    salle_id: Optional[int] = None
    formateur_id: Optional[int] = None
    prerequis: Optional[Union[Dict, List[str]]] = None

    #Vérifie les dates si elle sont toute les deux mises.
    @model_validator(mode="after")
    def verifier_dates_optionnelles(self) -> "SessionUpdate":
        if not self.date_debut or not self.date_fin:
            return self

        if self.date_debut >= self.date_fin:
            raise ValueError("La date de fin doit être supérieure à la date de début.")

        return self
