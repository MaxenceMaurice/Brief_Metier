import re
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from models.user import Role, NiveauAcces

#Classe parent contenant les informations communes aux utilisateurs.
class UtilisateurCreate(BaseModel):
    """ Informations communes pour créer un utilisateur. """

    nom: str = Field(min_length=1, max_length=50)
    prenom: str = Field(min_length=1, max_length=50)
    email: EmailStr
    is_active: bool = True

#Classe pour creer les apprenants.
class ApprenantCreate(UtilisateurCreate):
    """ Informations nécessaire pour créer un apprenant. """

    role: Role = Field(default=Role.apprenant)
    date_naissance: date
    niveau_etude: Optional[str] = None
    telephone: Optional[str] = None
    date_inscription_plateforme: datetime = Field(default_factory=datetime.now)
    certification_obtenue: Optional[str] = None

    #Vérifie que l'apprenant a au moins 16 ans.
    @field_validator("date_naissance")
    @classmethod
    def verifier_age(cls, valeur: date) -> date:
        """ Vérifie l'âge minimum de l'apprenant. """

        aujourd_hui = date.today()
    
        if aujourd_hui.year - valeur.year < 16:
            raise ValueError("L'apprenant doit avoir au moins 16 ans.")

        if aujourd_hui.year - valeur.year == 16:
            if (valeur.month, valeur.day) > (aujourd_hui.month, aujourd_hui.day):
                raise ValueError("L'apprenant doit avoir au moins 16 ans.")
            
        return valeur 

    #Vérifie que le numéro de téléphone contient bien 10 chiffres.
    @field_validator("telephone")
    @classmethod
    def verifier_telephone(cls, valeur: Optional[str]) -> Optional[str]:
        """Vérifie les caractères du numéro de téléphone. """

        if valeur is None:
            return None
        if not re.match(r"^0[1-9]\d{8}$", valeur):
            raise ValueError("Le téléphone doit contenir 10 chiffres (ex: 0612345678).")
        return valeur

#Classe pour créer les formateurs.
class FormateurCreate(UtilisateurCreate):
    """ Informations nécessaire pour créer un formateur. """
    role: Role = Field(default=Role.formateur)
    specialite: str
    date_embauche: date
    taux_horaire: float = Field(ge=0)
    bio: Optional[str] = None

    #Vérifie que la date d'embauche n'est pas après la date du jour.
    @field_validator("date_embauche")
    @classmethod
    def verifier_date_embauche(cls, valeur: date) -> date:
        """ Vérifie la date d'embauche du formateur. """

        if valeur > date.today():
            raise ValueError("La date d'embauche ne peut pas être dans le futur.")
        return valeur

#Classe pour créer le personnel pédagogique.
class StaffCreate(UtilisateurCreate):
    """ Informations nécessaires pour créer un membre du personnel pédagogique. """

    role: Role = Field(default=Role.staff)
    poste: str
    date_prise_fonction: date
    responsabilites: Optional[dict] = None

#Classe pour créer les administrateurs.
class AdminCreate(UtilisateurCreate):
    """Informations nécessaires pour créer un admin. """
    role: Role = Field(default=Role.admin)
    niveau_acces: NiveauAcces
    date_promotion: date
        



