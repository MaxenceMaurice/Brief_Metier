from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from models.inscription import StatutInscription



class InscriptionCreate(BaseModel):
    apprenant_id: int = Field(gt=0)
    session_id: int = Field(gt=0)
    date_inscription: datetime = Field(default_factory=datetime.now)
    statut_inscription:StatutInscription = Field(default=StatutInscription.ENREGISTRE)
    presence: Optional[bool] = None







