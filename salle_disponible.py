
from sqlmodel import select
from models.session import Session, StatutSession
from models.salle import Salle


class SalleIndisponible(Exception):
    """Erreur lorsqu'une salle ne peut pas être réservée."""
    pass


def is_salle_disponible(db, salle_id, date_debut, date_fin):
    """Vérifie qu'une salle est libre sur la période demandée."""

    if date_debut >= date_fin:
        raise ValueError("La date de début doit être avant la date de fin.")

    salle = db.get(Salle, salle_id)

    if salle is None:
        raise SalleIndisponible("Cette salle n'existe pas.")

    if not salle.is_active:
        raise SalleIndisponible("Cette salle est désactivée.")

    sessions = db.exec(
        select(Session).where(
            Session.salle_id == salle_id,
            Session.statut != StatutSession.ARCHIVED,
            Session.date_debut < date_fin,
            Session.date_fin > date_debut
        )
    ).all()

    return len(sessions) == 0
