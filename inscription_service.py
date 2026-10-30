
from sqlmodel import Session as DBSession, select

from models.inscription import Inscription, StatutInscription
from models.session import Session, StatutSession
from models.user import Apprenant


class InscriptionRefusee(Exception):
    """Erreur lorsqu'une inscription ne respecte pas les règles métier."""
    pass


def creer_inscription(db: DBSession, apprenant_id: int, session_id: int):
    """Inscrit un apprenant si toutes les conditions sont respectées."""

    # 1. Vérifier que l'apprenant existe
    apprenant = db.get(Apprenant, apprenant_id)

    if apprenant is None:
        raise InscriptionRefusee("Cet apprenant n'existe pas.")

    if not apprenant.is_active:
        raise InscriptionRefusee("Cet apprenant est désactivé.")

    # 2. Vérifier que la session existe et est ouverte
    session_formation = db.get(Session, session_id)

    if session_formation is None:
        raise InscriptionRefusee("Cette session n'existe pas.")

    if session_formation.statut != StatutSession.OPEN:
        raise InscriptionRefusee("Cette session n'est pas ouverte.")

    # 3. Empêcher les doubles inscriptions
    inscription_existante = db.exec(
        select(Inscription).where(
            Inscription.apprenant_id == apprenant_id,
            Inscription.session_id == session_id,
        )
    ).first()

    if inscription_existante is not None:
        raise InscriptionRefusee(
            "Cet apprenant possède déjà une inscription pour cette session."
        )

    # 4. Vérifier le nombre de places disponibles
    inscriptions = db.exec(
        select(Inscription).where(
            Inscription.session_id == session_id,
            Inscription.statut_inscription == StatutInscription.ENREGISTRE,
        )
    ).all()

    if len(inscriptions) >= session_formation.capacite_max:
        raise InscriptionRefusee("Cette session est complète.")

    # 5. Vérifier les conflits d'horaires pour l'apprenant
    inscriptions_apprenant = db.exec(
        select(Inscription).where(
            Inscription.apprenant_id == apprenant_id,
            Inscription.statut_inscription == StatutInscription.ENREGISTRE,
        )
    ).all()

    for inscription in inscriptions_apprenant:
        autre_session = db.get(Session, inscription.session_id)

        if autre_session is None:
            continue

        chevauchement = (
            session_formation.date_debut < autre_session.date_fin
            and session_formation.date_fin > autre_session.date_debut
        )

        if chevauchement:
            raise InscriptionRefusee(
                "Cet apprenant est déjà inscrit à une session sur ces horaires."
            )

    # 6. Créer l'inscription
    nouvelle_inscription = Inscription(
        apprenant_id=apprenant_id,
        session_id=session_id,
        statut_inscription=StatutInscription.ENREGISTRE,
    )

    db.add(nouvelle_inscription)

    # On ne fait pas de commit ici :
    # l'application qui appelle cette fonction gère l'enregistrement.
    db.flush()

    return nouvelle_inscription
