from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class Salle(SQLModel, table=True):
  __tablename__ = "salle"

  id: Optional[int] = Field(default=None, primary_key=True)
  nom: str = Field(unique=True, index=True, nullable=False)
  capacite: int = Field(gt=0, nullable=False)
  localisation: str
  is_active: bool = Field(default=True)
