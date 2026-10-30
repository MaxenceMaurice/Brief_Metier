#Importation des types nécessaires pour les dates, les rôles et ainsi que les champs optionnels.
from datetime import datetime, date
from enum import Enum
from typing import Optional

from sqlmodel import SQLModel, Field
from sqlalchemy import JSON


#Les différents rôles des utilisateurs.
class Role(str, Enum):
    """ Liste des rôles possible pour un utilisateur. """
    apprenant = "apprenant"
    formateur = "formateur"
    staff = "staff"
    admin = "admin"

#Les niveaux d'accès des administrateurs.
class NiveauAcces(str, Enum):
    """ Liste des niveaux d'accès des administrateurs. """
    SUPERADMIN = "SUPERADMIN"
    ADMIN_STANDARD = "ADMIN_STANDARD"

#Classe parent contenant les informations communes aux utilisateurs.
class Utilisateur(SQLModel):
    """ Informations communes à tous les utilisateurs. """
    id: int | None = Field(default=None, primary_key=True)
    nom: str = Field(max_length=50)
    prenom: str = Field(max_length=50)
    email: str = Field(unique=True)
    date_creation: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)
    role: Role = Field(default=Role.apprenant)

#Classe pour les apprenants.
class Apprenant(Utilisateur, table=True):
    """ Informations pour les apprenants. """
    role: Role = Field(default=Role.apprenant)
    date_naissance: date
    niveau_etude: Optional[str] = None
    telephone: Optional[str] = None
    date_inscription_plateforme: datetime = Field(default_factory=datetime.now)
    certification_obtenue: Optional[str] = None

#Classe pour les formateurs.
class Formateur(Utilisateur, table=True):
    """ Informations pour les formateurs. """
    specialite: str
    date_embauche: date
    taux_horaire:float = Field(ge=0)
    bio: Optional[str] = None

#Classe pour le personnel pédagogique.
class StaffPedagogique(Utilisateur, table=True):
    """ Informations pour le personnel pédagogique. """
    poste: str
    date_prise_fonction: date
    responsabilites: Optional[dict] = Field(
        default=None,
        sa_type=(JSON)
    )
#Classe pour les admins.
class Admin(Utilisateur, table=True):
    """ Informations pour les aministrateurs. """
    niveau_acces: NiveauAcces
    date_promotion: date




    





                                
                                    
                                    
                                    
                                    
