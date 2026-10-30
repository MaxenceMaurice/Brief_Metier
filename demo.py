from datetime import datetime, timezone, date
from sqlmodel import Session, create_engine

# Import de vos modèles conformes à votre structure
from models.user import Apprenant, Formateur, Role
from models.salle import Salle
from models.session import Session as SessionFormation, StatutSession
from models.inscription import Inscription, StatutInscription

# Connexion à la base de données SQLite (ajustez le chemin si nécessaire)
engine = create_engine("sqlite:///database.db")

def lancer_demo():
    print("=== DÉMONSTRATION ===")
    
    with Session(engine) as session_db:
        # Création d'une Salle 
        salle = Salle(
            nom="Salle de Formation A",
            capacite=30,
            localisation="Bâtiment Principal",
            is_active=True,
            equipements={"projecteur": True, "tableau_blanc": True}
        )
        session_db.add(salle)
        session_db.commit()
        session_db.refresh(salle)
        print(f"Salle créée : {salle.nom} (ID: {salle.id})")

        # Création d'un Formateur
        formateur = Formateur(
            nom="Martin",
            prenom="Alice",
            email="alice.martin@cf-tech.fr",
            date_creation=datetime.now(timezone.utc),
            role=Role.formateur,
            specialite="SQLModel",
            date_embauche=date(2022, 9, 1),
            taux_horaire=50.0,
            bio="Experte en bases de données."
        )
        session_db.add(formateur)
        session_db.commit()
        session_db.refresh(formateur)
        print(f"Formateur créé : {formateur.prenom} {formateur.nom} (ID: {formateur.id})")

        # Création d'un Apprenant 
        apprenant = Apprenant(
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@cf-tech.fr",
            date_creation=datetime.now(timezone.utc),
            role=Role.apprenant,
            date_naissance=date(2000, 5, 14),
            niveau_etude="Bac +3",
            telephone="0612345678",
            date_inscription_plateforme=datetime.now(timezone.utc)
        )
        session_db.add(apprenant)
        session_db.commit()
        session_db.refresh(apprenant)
        print(f"Apprenant créé : {apprenant.prenom} {apprenant.nom} (ID: {apprenant.id})")

        # Création d'une Session de formation (
        session_formation = SessionFormation(
            titre="Session 1",
            description="Atelier pratique sur l'ORM et la gestion des relations",
            date_debut=datetime(2026, 6, 10, 9, 0, 0, tzinfo=timezone.utc),
            date_fin=datetime(2026, 6, 10, 17, 0, 0, tzinfo=timezone.utc),
            capacite_max=20,
            statut=StatutSession.OPEN,
            salle_id=salle.id,
            formateur_id=formateur.id
        )
        session_db.add(session_formation)
        session_db.commit()
        session_db.refresh(session_formation)
        print(f"Session créée : '{session_formation.titre}' (ID: {session_formation.id})")

        # Inscription de l'apprenant à la session 
        inscription = Inscription(
            apprenant_id=apprenant.id,
            session_id=session_formation.id,
            statut_inscription=StatutInscription.ENREGISTRE
        )
        session_db.add(inscription)
        session_db.commit()
        print(f"Inscription validée avec succès pour {apprenant.nom} à la session '{session_formation.titre}' !")

    print("=== FIN DE LA DÉMO ===")

if __name__ == "__main__":
    lancer_demo()
