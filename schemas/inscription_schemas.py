from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from models.inscription import StatutInscription


#Classe pour les inscriptions des apprenants aux sessions.
class InscriptionCreate(BaseModel):
    """Informations nécessaires pour créer une inscription.  """

    apprenant_id: int = Field(gt=0)
    session_id: int = Field(gt=0)
    date_inscription: datetime = Field(default_factory=datetime.now)
    statut_inscription:StatutInscription = Field(default=StatutInscription.ENREGISTRE)
    presence: Optional[bool] = None







