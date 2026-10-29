
from sqlmodel import Session as DBSession, select

from models.session import Session, StatutSession
from models.salle import Salle
from models.user import Formateur

from salle_disponible import is_salle_disponible, SalleIndisponible


class SessionRefusee(Exception):
    """Erreur lorsqu'une session ne respecte pas les règles métier."""
    pass


def creer_session(
    db: DBSession,
    titre: str,
    date_debut,
    date_fin,
    capacite_max: int,
    salle_id: int,
    formateur_id: int,
    description=None,
    prerequis=None,
):
    """Crée une session si toutes les conditions sont respectées."""

    # 1. Vérifier les dates
    if date_debut >= date_fin:
        raise SessionRefusee(
            "La date de début doit être avant la date de fin."
        )

    # 2. Vérifier le titre et la capacité
    if not titre or not titre.strip() or len(titre) > 100:
        raise SessionRefusee(
            "Le titre doit contenir entre 1 et 100 caractères."
        )

    if capacite_max <= 0:
        raise SessionRefusee(
            "La capacité doit être supérieure à zéro."
        )

    # 3. Vérifier que la salle existe et est active
    salle = db.get(Salle, salle_id)

    if salle is None:
        raise SessionRefusee("Cette salle n'existe pas.")

    if not salle.is_active:
        raise SessionRefusee("Cette salle est désactivée.")

    # 4. Vérifier la capacité de la salle
    if capacite_max > salle.capacite:
        raise SessionRefusee(
            "La capacité de la session dépasse celle de la salle."
        )

    # 5. Vérifier la disponibilité de la salle
    try:
        disponible = is_salle_disponible(
            db, salle_id, date_debut, date_fin
        )
    except (SalleIndisponible, ValueError) as erreur:
        raise SessionRefusee(str(erreur)) from erreur

    if not disponible:
        raise SessionRefusee(
            "Cette salle est déjà occupée sur ces horaires."
        )

    # 6. Vérifier que le formateur existe et est actif
    formateur = db.get(Formateur, formateur_id)

    if formateur is None:
        raise SessionRefusee("Ce formateur n'existe pas.")

    if not formateur.is_active:
        raise SessionRefusee("Ce formateur est désactivé.")

    # 7. Vérifier la disponibilité du formateur
    sessions_formateur = db.exec(
        select(Session).where(
            Session.formateur_id == formateur_id,
            Session.statut != StatutSession.ARCHIVED,
            Session.date_debut < date_fin,
            Session.date_fin > date_debut,
        )
    ).all()

    if sessions_formateur:
        raise SessionRefusee(
            "Ce formateur anime déjà une session sur ces horaires."
        )

    # 8. Créer la session
    nouvelle_session = Session(
        titre=titre,
        description=description,
        date_debut=date_debut,
        date_fin=date_fin,
        capacite_max=capacite_max,
        statut=StatutSession.OPEN,
        salle_id=salle_id,
        formateur_id=formateur_id,
        prerequis=prerequis,
    )

    db.add(nouvelle_session)

    # Le commit est géré par le code qui appelle cette fonction.
    db.flush()

    return nouvelle_session
