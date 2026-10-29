import streamlit as st
from sqlmodel import select
from datetime import date, datetime, timezone
from database import get_session

from models.salle import Salle
from models.session import Session, StatutSession
from models.user import Apprenant, Formateur, StaffPedagogique, Admin, Role, NiveauAcces
from models.inscription import Inscription, StatutInscription

st.set_page_config(page_title="CF-Tech - Gestion", layout="wide")
st.title("CF-Tech - Gestion")
db = next(get_session())

menu = st.sidebar.selectbox("Navigation", ["Dashboard", "Salles", "Utilisateurs", "Sessions", "Inscriptions"])

# DASHBOARD 
if menu == "Dashboard":
    st.header("Tableau de bord")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Apprenants", len(db.exec(select(Apprenant)).all()))
    c2.metric("Formateurs", len(db.exec(select(Formateur)).all()))
    c3.metric("Salles", len(db.exec(select(Salle)).all()))
    c4.metric("Sessions", len(db.exec(select(Session)).all()))

# SALLES 
elif menu == "Salles":
    st.header("Gestion des Salles")
    with st.form("form_salle"):
        nom = st.text_input("Nom")
        capacite = st.number_input("Capacité max", min_value=1, value=15)
        loc = st.text_input("Localisation")
        if st.form_submit_button("Créer"):
            db.add(Salle(nom=nom, capacite=capacite, localisation=loc))
            db.commit()
            st.success("Salle créée !")
            
    salles = db.exec(select(Salle)).all()
    st.dataframe([{"Nom": s.nom, "Capacité": s.capacite, "Lieu": s.localisation} for s in salles], width='stretch')

# UTILISATEURS 
elif menu == "Utilisateurs":
    st.header("Gestion des Utilisateurs")
    t1, t2 = st.tabs(["Ajouter", "Liste"])
    
    with t1:
        type_u = st.selectbox("Rôle", ["Apprenant", "Formateur", "Staff", "Admin"])
        with st.form("form_user"):
            nom, prenom, email = st.text_input("Nom"), st.text_input("Prénom"), st.text_input("Email")
            if st.form_submit_button("Enregistrer"):
                now = datetime.now(timezone.utc)
                if type_u == "Apprenant":
                    u = Apprenant(nom=nom, prenom=prenom, email=email, role=Role.apprenant, date_naissance=date.today(), date_creation=now, date_inscription_plateforme=now)
                elif type_u == "Formateur":
                    u = Formateur(nom=nom, prenom=prenom, email=email, role=Role.formateur, specialite="Général", date_embauche=date.today(), taux_horaire=50.0, date_creation=now)
                elif type_u == "Staff":
                    u = StaffPedagogique(nom=nom, prenom=prenom, email=email, role=Role.staff, poste="Staff", date_prise_fonction=date.today(), date_creation=now)
                else:
                    u = Admin(nom=nom, prenom=prenom, email=email, role=Role.admin, niveau_acces=NiveauAcces.ADMIN_STANDARD, date_promotion=date.today(), date_creation=now)
                db.add(u)
                db.commit()
                st.success("Utilisateur ajouté !")
                
    with t2:
        tous = db.exec(select(Apprenant)).all() + db.exec(select(Formateur)).all() + db.exec(select(StaffPedagogique)).all() + db.exec(select(Admin)).all()
        st.dataframe([{"Nom": u.nom, "Prénom": u.prenom, "Rôle": u.role.value, "Actif": u.is_active} for u in tous], width='stretch')

# SESSIONS
elif menu == "Sessions":
    st.header("Gestion des Sessions")
    salles = db.exec(select(Salle)).all()
    formateurs = db.exec(select(Formateur)).all()
    
    if not salles or not formateurs:
        st.warning("Créez d'abord une salle et un formateur.")
    else:
        with st.form("form_session"):
            titre = st.text_input("Titre")
            d_debut, d_fin = st.date_input("Début"), st.date_input("Fin")
            cap = st.number_input("Capacité max", min_value=1, value=10)
            salle = st.selectbox("Salle", salles, format_func=lambda s: f"{s.nom} ({s.capacite})")
            formateur = st.selectbox("Formateur", formateurs, format_func=lambda f: f"{f.nom} {f.prenom}")
            
            if st.form_submit_button("Créer"):
                if cap > salle.capacite:
                    st.error("Capacité supérieure à la salle !")
                else:
                    dt_deb = datetime.combine(d_debut, datetime.min.time()).replace(tzinfo=timezone.utc)
                    dt_fin = datetime.combine(d_fin, datetime.max.time()).replace(tzinfo=timezone.utc)
                    db.add(Session(titre=titre, date_debut=dt_deb, date_fin=dt_fin, capacite_max=cap, salle_id=salle.id, formateur_id=formateur.id))
                    db.commit()
                    st.success("Session créée !")
                    
    sessions = db.exec(select(Session)).all()
    st.dataframe([{"Titre": s.titre, "Début": s.date_debut.strftime("%Y-%m-%d"), "Capacité": s.capacite_max} for s in sessions], width='stretch')

# INSCRIPTIONS 
elif menu == "Inscriptions":
    st.header("Gestion des Inscriptions")
    apprenants = db.exec(select(Apprenant).where(Apprenant.is_active == True)).all()
    sessions = db.exec(select(Session).where(Session.statut == StatutSession.OPEN)).all()
    
    if not apprenants or not sessions:
        st.warning("Assurez-vous d'avoir des apprenants actifs et des sessions ouvertes.")
    else:
        apprenant = st.selectbox("Apprenant", apprenants, format_func=lambda a: f"{a.nom} {a.prenom}")
        
        for s in sessions:
            inscrits = db.exec(select(Inscription).where(Inscription.session_id == s.id, Inscription.statut_inscription == StatutInscription.ENREGISTRE)).all()
            col1, col2 = st.columns([3, 1])
            col1.text(f"{s.titre} (Places : {len(inscrits)}/{s.capacite_max})")
            
            if col2.button("S'inscrire", key=f"session_{s.id}"):
                db.add(Inscription(apprenant_id=apprenant.id, session_id=s.id, date_inscription=datetime.now(timezone.utc)))
                db.commit()
                st.success("Inscrit !")
                st.rerun()