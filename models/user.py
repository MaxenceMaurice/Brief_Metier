from datetime import datetime, date
from enum import Enum
from typing import Optional

from sqlmodel import Relationship, SQLModel, Field
from sqlalchemy import JSON



class Role(str, Enum):
    apprenant = "apprenant"
    formateur = "formateur"
    staff = "staff"
    admin = "admin"

class NiveauAcces(str, Enum):
    SUPERADMIN = "SUPERADMIN"
    ADMIN_STANDARD = "ADMIN_STANDARD"


class Utilisateur(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    nom: str = Field(max_length=50)
    prenom: str = Field(max_length=50)
    email: str = Field(unique=True)
    date_creation: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)
    role: Role = Field(default=Role.apprenant)


class Apprenant(Utilisateur, table=True):
    role: Role = Field(default=Role.apprenant)
    date_naissance: date
    niveau_etude: Optional[str] = None
    telephone: Optional[str] = None
    date_inscription_plateforme: datetime = Field(default_factory=datetime.now)
    certification_obtenue: Optional[str] = None


class Formateur(Utilisateur, table=True):
    specialite: str
    date_embauche: date
    taux_horaire:float = Field(ge=0)
    bio: Optional[str] = None


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




    





                                
                                    
                                    
                                    
                                    
