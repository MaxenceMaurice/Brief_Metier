
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlmodel import SQLModel, Session as DBSession, create_engine

from inscription_service import creer_inscription, InscriptionRefusee
from models.user import Apprenant, Formateur
from models.salle import Salle
from models.session import Session, StatutSession
from models.inscription import Inscription


@pytest.fixture
def db():
    """Crée une base SQLite temporaire, indépendante de database.db."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with DBSession(engine) as session:
        yield session

    engine.dispose()


@pytest.fixture
def donnees(db):
    """Prépare un apprenant, un formateur, une salle et une session."""

    apprenant = Apprenant(
        nom="Test",
        prenom="Alice",
        email="alice.test@example.com",
        date_naissance=date(2000, 1, 1),
        date_creation=datetime.now(timezone.utc),
        date_inscription_plateforme=datetime.now(timezone.utc),
    )

    formateur = Formateur(
        nom="Test",
        prenom="Bob",
        email="bob.test@example.com",
        specialite="Python",
        date_embauche=date(2020, 1, 1),
        taux_horaire=50,
        date_creation=datetime.now(timezone.utc),
    )

    salle = Salle(
        nom="Salle test",
        capacite=10,
        localisation="Bâtiment A",
    )

    db.add_all([apprenant, formateur, salle])
    db.flush()

    debut = datetime(2026, 11, 10, 9, 0, tzinfo=timezone.utc)

    session_formation = Session(
        titre="Formation Python",
        date_debut=debut,
        date_fin=debut + timedelta(hours=3),
        capacite_max=2,
        salle_id=salle.id,
        formateur_id=formateur.id,
        statut=StatutSession.OPEN,
    )

    db.add(session_formation)
    db.flush()

    return apprenant, formateur, salle, session_formation


def test_inscription_reussie(db, donnees):
    apprenant, _, _, session_formation = donnees

    inscription = creer_inscription(
        db, apprenant.id, session_formation.id
    )

    assert isinstance(inscription, Inscription)
    assert inscription.apprenant_id == apprenant.id


def test_double_inscription_refusee(db, donnees):
    apprenant, _, _, session_formation = donnees

    creer_inscription(db, apprenant.id, session_formation.id)

    with pytest.raises(InscriptionRefusee):
        creer_inscription(db, apprenant.id, session_formation.id)


def test_session_fermee_refusee(db, donnees):
    apprenant, _, _, session_formation = donnees

    session_formation.statut = StatutSession.CLOSED
    db.flush()

    with pytest.raises(InscriptionRefusee):
        creer_inscription(db, apprenant.id, session_formation.id)


def test_session_complete_refusee(db, donnees):
    apprenant, _, _, session_formation = donnees

    session_formation.capacite_max = 1

    autre_apprenant = Apprenant(
        nom="Test",
        prenom="Charlie",
        email="charlie.test@example.com",
        date_naissance=date(2001, 1, 1),
        date_creation=datetime.now(timezone.utc),
        date_inscription_plateforme=datetime.now(timezone.utc),
    )

    db.add(autre_apprenant)
    db.flush()

    creer_inscription(db, autre_apprenant.id, session_formation.id)

    with pytest.raises(InscriptionRefusee):
        creer_inscription(db, apprenant.id, session_formation.id)


def test_conflit_horaire_refuse(db, donnees):
    apprenant, formateur, salle, premiere_session = donnees

    creer_inscription(db, apprenant.id, premiere_session.id)

    deuxieme_session = Session(
        titre="Autre formation",
        date_debut=premiere_session.date_debut + timedelta(hours=1),
        date_fin=premiere_session.date_fin + timedelta(hours=1),
        capacite_max=2,
        salle_id=salle.id,
        formateur_id=formateur.id,
        statut=StatutSession.OPEN,
    )

    db.add(deuxieme_session)
    db.flush()

    with pytest.raises(InscriptionRefusee):
        creer_inscription(db, apprenant.id, deuxieme_session.id)


def test_apprenant_inexistant_refuse(db, donnees):
    _, _, _, session_formation = donnees

    with pytest.raises(InscriptionRefusee):
        creer_inscription(db, 99999, session_formation.id)
