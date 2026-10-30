
from datetime import datetime, timezone

import pytest
from sqlmodel import SQLModel, Session as DBSession, create_engine

from models.salle import Salle
from models.session import Session
from models.user import Formateur  # Nécessaire pour enregistrer la table
from salle_disponible import is_salle_disponible, SalleIndisponible


@pytest.fixture
def db():
    """Crée une base SQLite en mémoire pour chaque test."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with DBSession(engine) as session:
        yield session

    engine.dispose()


def test_salle_libre(db):
    """Vérifie qu'une salle sans réservation est disponible."""
    salle = Salle(
        nom="Salle A",
        capacite=20,
        localisation="Paris"
    )
    db.add(salle)
    db.commit()
    db.refresh(salle)

    resultat = is_salle_disponible(
        db,
        salle.id,
        datetime(2026, 11, 10, 9, tzinfo=timezone.utc),
        datetime(2026, 11, 10, 12, tzinfo=timezone.utc)
    )

    assert resultat is True


def test_salle_occupee(db):
    """Vérifie qu'une salle déjà réservée est indisponible."""
    salle = Salle(
        nom="Salle B",
        capacite=20,
        localisation="Paris"
    )
    db.add(salle)
    db.commit()
    db.refresh(salle)

    session = Session(
        titre="Formation Python",
        date_debut=datetime(2026, 11, 10, 9, tzinfo=timezone.utc),
        date_fin=datetime(2026, 11, 10, 12, tzinfo=timezone.utc),
        capacite_max=10,
        salle_id=salle.id,
        formateur_id=1
    )
    db.add(session)
    db.commit()

    resultat = is_salle_disponible(
        db,
        salle.id,
        datetime(2026, 11, 10, 10, tzinfo=timezone.utc),
        datetime(2026, 11, 10, 14, tzinfo=timezone.utc)
    )

    assert resultat is False


def test_salle_inexistante(db):
    """Vérifie qu'une salle inexistante provoque une erreur."""
    with pytest.raises(SalleIndisponible):
        is_salle_disponible(
            db,
            999,
            datetime(2026, 11, 10, 9, tzinfo=timezone.utc),
            datetime(2026, 11, 10, 12, tzinfo=timezone.utc)
        )


def test_dates_invalides(db):
    """Vérifie que la date de début précède la date de fin."""
    with pytest.raises(ValueError):
        is_salle_disponible(
            db,
            1,
            datetime(2026, 11, 10, 14, tzinfo=timezone.utc),
            datetime(2026, 11, 10, 9, tzinfo=timezone.utc)
        )
