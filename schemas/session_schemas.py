from datetime import datetime
from typing import Optional, Dict, List, Union
from pydantic import BaseModel, model_validator
from models.session import StatutSessionEnum

class SessionCreate(BaseModel):
    titre: str
    description: Optional[str] = None
    date_debut: datetime
    date_fin: datetime
    capacite_max: int
    statut: StatutSessionEnum = StatutSessionEnum.OPEN
    salle_id: int
    formateur_id: int
    prerequis: Optional[Union[Dict, List[str]]] = None

    @model_validator(mode="after")
    def verifier_dates(self) -> "SessionCreate":
        if self.date_debut >= self.date_fin:
            raise ValueError("La date de fin doit être supérieure à la date de début.")
        return self

class SessionUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    capacite_max: Optional[int] = None
    statut: Optional[StatutSessionEnum] = None
    salle_id: Optional[int] = None
    formateur_id: Optional[int] = None
    prerequis: Optional[Union[Dict, List[str]]] = None

    @model_validator(mode="after")
    def verifier_dates_optionnelles(self) -> "SessionUpdate":
        if not self.date_debut or not self.date_fin:
            return self
        
        if self.date_debut >= self.date_fin:
            raise ValueError("La date de fin doit être supérieure à la date de début.")  
        return self