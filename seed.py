from datetime import datetime, date, timedelta, timezone
import random
from sqlmodel import Session as DBSession, select

from database import engine
from models.salle import Salle
from models.user import Formateur, Apprenant, StaffPedagogique, Admin, Role, NiveauAcces
from models.session import Session, StatutSession
from models.inscription import Inscription, StatutInscription

noms_famille = ["Dupont", "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois", "Moreau"]
prenoms_liste = ["Alice", "Bob", "Charlie", "David", "Emma", "Fanny", "Gabriel", "Hugo", "Ines", "Juliette"]
specialites_liste = ["Data Science", "DevOps", "Développement Web", "Cybersécurité"]
cours_titres = ["Initiation à Python", "Pipeline ETL", "Docker & Kubernetes", "Architecture FastAPI", "Bases de données SQL"]

def seed_database():
    with DBSession(engine) as session:
        print("🌱 Début de la génération de toutes les données...")

        # 1. Création des Salles
        salles = []
        noms_salles = ["Salle A101", "Salle B202", "Labo Info 1", "Amphithéâtre"]
        for nom in noms_salles:
            salle = Salle(
                nom=nom,
                capacite=random.randint(15, 30),
                localisation="Bâtiment Principal, 1er étage",
                is_active=True
            )
            session.add(salle)
            salles.append(salle)
        
        session.commit()
        print("✅ Salles créées !")

        # 2. Création des Formateurs
        formateurs = []
        for i in range(3):
            formateur = Formateur(
                nom=noms_famille[i],
                prenom=prenoms_liste[i],
                email=f"formateur.{i+1}@ecole.fr",
                date_creation=datetime.now(timezone.utc),
                is_active=True,
                role=Role.formateur,
                specialite=specialites_liste[i],
                date_embauche=date(2022, 1, 15),
                taux_horaire=45.0,
                bio="Formateur expert avec plusieurs années d'expérience."
            )
            session.add(formateur)
            formateurs.append(formateur)

        # 3. Création des Apprenants
        apprenants = []
        for i in range(10):
            apprenant = Apprenant(
                nom=random.choice(noms_famille),
                prenom=random.choice(prenoms_liste),
                email=f"apprenant.{i+1}@etudiant.fr",
                date_creation=datetime.now(timezone.utc),
                is_active=True,
                role=Role.apprenant,
                date_naissance=date(1998, 5, 12),
                niveau_etude="Bac+3",
                telephone=f"06000000{i:02d}",
                date_inscription_plateforme=datetime.now(timezone.utc),
                certification_obtenue=None
            )
            session.add(apprenant)
            apprenants.append(apprenant)

        # 4. Création du Staff Pédagogique
        staff = StaffPedagogique(
            nom="Lefebvre",
            prenom="Sophie",
            email="sophie.staff@ecole.fr",
            date_creation=datetime.now(timezone.utc),
            is_active=True,
            role=Role.staff,
            poste="Coordination Pédagogique",
            date_prise_fonction=date(2021, 9, 1),
            responsabilites={"planning": True, "suivi_etudiants": True}
        )
        session.add(staff)

        # 5. Création de l'Admin
        admin = Admin(
            nom="Directeur",
            prenom="Marc",
            email="admin@ecole.fr",
            date_creation=datetime.now(timezone.utc),
            is_active=True,
            role=Role.admin,
            niveau_acces=NiveauAcces.SUPERADMIN,
            date_promotion=date(2020, 1, 1)
        )
        session.add(admin)

        session.commit()
        print("✅ Utilisateurs (Formateurs, Apprenants, Staff, Admin) créés !")

        # 6. Création des Sessions
        sessions_list = []
        maintenant = datetime.now(timezone.utc)
        for i in range(4):
            date_debut = maintenant + timedelta(days=i+1)
            date_fin = date_debut + timedelta(hours=7)
            salle_choisie = salles[i % len(salles)]
            formateur_choisi = formateurs[i % len(formateurs)]
            
            sess = Session(
                titre=cours_titres[i],
                description="Session de formation pratique et intensive.",
                date_debut=date_debut,
                date_fin=date_fin,
                capacite_max=salle_choisie.capacite,
                statut=StatutSession.OPEN,
                salle_id=salle_choisie.id,
                formateur_id=formateur_choisi.id
            )
            session.add(sess)
            sessions_list.append(sess)

        session.commit()
        print("✅ Sessions créées !")

        # 7. Création des Inscriptions
        for apprenant in apprenants:
            sess_choisie = random.choice(sessions_list)
            
            existing = session.exec(
                select(Inscription).where(
                    Inscription.apprenant_id == apprenant.id,
                    Inscription.session_id == sess_choisie.id
                )
            ).first()
            
            if not existing:
                inscription = Inscription(
                    apprenant_id=apprenant.id,
                    session_id=sess_choisie.id,
                    date_inscription=datetime.now(timezone.utc),
                    statut_inscription=StatutInscription.ENREGISTRE,
                    presence=True
                )
                session.add(inscription)

        session.commit()
        print("✅ Inscriptions créées !")
        print("🎉 Toutes vos tables ont été peuplées avec succès !")

if __name__ == "__main__":
    seed_database()