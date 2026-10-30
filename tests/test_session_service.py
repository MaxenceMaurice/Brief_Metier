
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlmodel import SQLModel, Session as DBSession, create_engine

from session_service import creer_session, SessionRefusee
from models.user import Formateur
from models.salle import Salle
from models.session import Session


@pytest.fixture
def db():
    """Crée une base SQLite en mémoire pour chaque test."""
    engine = create_engine("sqlite:///:memory:")

    SQLModel.metadata.create_all(engine)

    with DBSession(engine) as session:
        yield session

    engine.dispose()


@pytest.fixture
def donnees(db):
    """Prépare une salle et deux formateurs pour les tests."""

    salle = Salle(
        nom="Salle Python",
        capacite=10,
        localisation="Bâtiment A",
        is_active=True,
    )

    formateur = Formateur(
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        specialite="Python",
        date_embauche=date(2020, 1, 1),
        taux_horaire=50,
        date_creation=datetime.now(timezone.utc),
    )

    autre_formateur = Formateur(
        nom="Martin",
        prenom="Sophie",
        email="sophie.martin@example.com",
        specialite="SQL",
        date_embauche=date(2021, 1, 1),
        taux_horaire=45,
        date_creation=datetime.now(timezone.utc),
    )

    db.add_all([salle, formateur, autre_formateur])
    db.flush()

    debut = datetime(2026, 11, 10, 9, 0, tzinfo=timezone.utc)
    fin = debut + timedelta(hours=3)

    return salle, formateur, autre_formateur, debut, fin


def test_creation_session_reussie(db, donnees):
    """Une session valide doit pouvoir être créée."""

    salle, formateur, _, debut, fin = donnees

    nouvelle_session = creer_session(
        db=db,
        titre="Formation Python",
        date_debut=debut,
        date_fin=fin,
        capacite_max=8,
        salle_id=salle.id,
        formateur_id=formateur.id,
    )

    assert isinstance(nouvelle_session, Session)
    assert nouvelle_session.titre == "Formation Python"
    assert nouvelle_session.capacite_max == 8
    assert nouvelle_session.salle_id == salle.id
    assert nouvelle_session.formateur_id == formateur.id
    assert nouvelle_session.id is not None


def test_capacite_salle_depassee(db, donnees):
    """La capacité de la session ne doit pas dépasser celle de la salle."""

    salle, formateur, _, debut, fin = donnees

    with pytest.raises(SessionRefusee):
        creer_session(
            db=db,
            titre="Formation trop grande",
            date_debut=debut,
            date_fin=fin,
            capacite_max=15,
            salle_id=salle.id,
            formateur_id=formateur.id,
        )


def test_salle_deja_occupee(db, donnees):
    """Deux sessions ne peuvent pas utiliser la même salle en même temps."""

    salle, formateur, autre_formateur, debut, fin = donnees

    creer_session(
        db=db,
        titre="Première formation",
        date_debut=debut,
        date_fin=fin,
        capacite_max=8,
        salle_id=salle.id,
        formateur_id=formateur.id,
    )

    with pytest.raises(SessionRefusee):
        creer_session(
            db=db,
            titre="Deuxième formation",
            date_debut=debut + timedelta(hours=1),
            date_fin=fin + timedelta(hours=1),
            capacite_max=5,
            salle_id=salle.id,
            formateur_id=autre_formateur.id,
        )


def test_formateur_deja_occupe(db, donnees):
    """Un formateur ne peut pas animer deux sessions en même temps."""

    salle, formateur, _, debut, fin = donnees

    autre_salle = Salle(
        nom="Salle SQL",
        capacite=15,
        localisation="Bâtiment B",
        is_active=True,
    )

    db.add(autre_salle)
    db.flush()

    creer_session(
        db=db,
        titre="Première formation",
        date_debut=debut,
        date_fin=fin,
        capacite_max=8,
        salle_id=salle.id,
        formateur_id=formateur.id,
    )

    with pytest.raises(SessionRefusee):
        creer_session(
            db=db,
            titre="Deuxième formation",
            date_debut=debut + timedelta(hours=1),
            date_fin=fin + timedelta(hours=1),
            capacite_max=10,
            salle_id=autre_salle.id,
            formateur_id=formateur.id,
        )


def test_dates_invalides(db, donnees):
    """La date de début doit être avant la date de fin."""

    salle, formateur, _, debut, fin = donnees

    with pytest.raises(SessionRefusee):
        creer_session(
            db=db,
            titre="Formation dates invalides",
            date_debut=fin,
            date_fin=debut,
            capacite_max=5,
            salle_id=salle.id,
            formateur_id=formateur.id,
        )


def test_salle_desactivee(db, donnees):
    """Une salle désactivée ne peut pas accueillir de session."""

    salle, formateur, _, debut, fin = donnees

    salle.is_active = False
    db.flush()

    with pytest.raises(SessionRefusee):
        creer_session(
            db=db,
            titre="Formation salle désactivée",
            date_debut=debut,
            date_fin=fin,
            capacite_max=5,
            salle_id=salle.id,
            formateur_id=formateur.id,
        )


def test_formateur_inexistant(db, donnees):
    """Une session ne peut pas utiliser un formateur inexistant."""

    salle, _, _, debut, fin = donnees

    with pytest.raises(SessionRefusee):
        creer_session(
            db=db,
            titre="Formation sans formateur",
            date_debut=debut,
            date_fin=fin,
            capacite_max=5,
            salle_id=salle.id,
            formateur_id=99999,
        )
