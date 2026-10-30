from typing import List, Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON

#classe pour les salles possibles.
class Salle(SQLModel, table=True):
  """ Informations sur les salles. """
  
  __tablename__ = "salle"

  id: Optional[int] = Field(default=None, primary_key=True)
  nom: str = Field(unique=True, index=True, nullable=False)
  capacite: int = Field(gt=0, nullable=False)
  localisation: str
  is_active: bool = Field(default=True)
  equipements: dict | None = Field(default=None, sa_column=Column(JSON))
