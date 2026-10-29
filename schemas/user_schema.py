import re
from datetime import date, datetime
from typing import Optional
from sqlmodel import JSON
from pydantic import BaseModel, EmailStr, Field, field_validator
from models.user import Role, NiveauAcces, Utilisateur
class UtilisateurCreate(BaseModel):
    nom: str = Field(min_length=1, max_lenght=50)
    prenom: str = Field(min_length=1, max_lenght=50)
    email: EmailStr
    is_active: bool = True

class ApprenantCreate(UtilisateurCreate):
    role: Role = Field(default=Role.apprenant)
    date_naissance: date
    niveau_etude: Optional[str] = None
    telephone: Optional[str] = None
    date_inscription_plateforme: datetime = Field(default_factory=datetime.now)
    certification_obtenue: Optional[str] = None

    @field_validator("date_naissance")
    @classmethod
    def verifier_age(cls, valeur:date) -> date:
        aujourd_hui = date.today()
    
        if aujourd_hui.year - valeur.year < 16:
            raise ValueError("L'apprenant doit avoir aumoins 16 ans.")

        if aujourd_hui.year - valeur.year == 16:
            if (valeur.month, valeur.day) > (aujourd_hui.month, aujourd_hui.day):
                raise ValueError("L'apprenant doit avoir aumoins 16 ans.")
            
            return valeur 

    @field_validator("telephone")
    @classmethod
    def verifier_telephone(cls, valeur: Optional[str]) -> Optional[str]:
        if valeur is None:
            return None
        if not re.match(r"^0[1-9]\d{8}$", valeur):
            raise ValueError("Le téléphone doit contenir 10 chiffres (ex: 0612345678).")
        return valeur


class FormateurCreate(Utilisateur, table=True):
    specialite: str
    date_embauche: date
    taux_horaire:float = Field(ge=0)
    bio: Optional[str] = None

    @field_validator("date_embauche")
    @classmethod
    def verifier_date_embauche(cls,valeur:date) -> date:
        if valeur > date.today():
            raise ValueError("La date d'embauche ne peut pas être dans le futur.")
        
        return valeur

    

class StaffPedagogique(Utilisateur, table=True):
    poste: str
    date_prise_fonction: date
    responsabilites: Optional[dict] = Field(
        default=None,
        sa_type=(JSON)
    )


class Admin(Utilisateur, table=True):
    niveau_acces: NiveauAcces
    date_promotion: date  
        



