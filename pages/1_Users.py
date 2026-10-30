import streamlit as st
from sqlmodel import select
from datetime import date, datetime, timezone
from database import get_session

from models.user import Apprenant, Formateur, StaffPedagogique, Admin, Role, NiveauAcces

st.set_page_config(page_title="CF-Tech - Utilisateurs", layout="wide")
st.header("Gestion des Utilisateurs")
db = next(get_session())

tab_ajout, tab_liste = st.tabs(["Créer un utilisateur", "Liste et Filtres"])

with tab_ajout:
    type_user = st.selectbox("Rôle de l'utilisateur", ["Apprenant", "Formateur", "Staff", "Admin"])
    
    with st.form("form_user"):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        email = st.text_input("Email")
        
        if type_user == "Apprenant":
            date_naissance = st.date_input("Date de naissance", min_value=date(1900, 1, 1), max_value=date.today())
            niveau_etude = st.text_input("Niveau d'étude (optionnel)")
            telephone = st.text_input("Téléphone (optionnel)")
            certification = st.text_input("Certification obtenue (optionnel)")
        elif type_user == "Formateur":
            specialite = st.text_input("Spécialité")
            date_embauche = st.date_input("Date d'embauche")
            taux_horaire = st.number_input("Taux horaire (€)", min_value=0.0, value=50.0)
            bio = st.text_area("Biographie (optionnel)")
        elif type_user == "Staff":
            poste = st.text_input("Poste")
            date_prise_fonction = st.date_input("Date de prise de fonction")
        elif type_user == "Admin": 
            niveau_acces = st.selectbox("Niveau d'accès", [NiveauAcces.SUPERADMIN, NiveauAcces.ADMIN_STANDARD])
            date_promotion = st.date_input("Date de promotion")
            
        if st.form_submit_button("Enregistrer l'utilisateur"):
            now_utc = datetime.now(timezone.utc)
            try:
                if type_user == "Apprenant":
                    user = Apprenant(
                        nom=nom, prenom=prenom, email=email, role=Role.apprenant,
                        date_naissance=date_naissance, niveau_etude=niveau_etude,
                        telephone=telephone, certification_obtenue=certification,
                        date_creation=now_utc, date_inscription_plateforme=now_utc
                    )
                elif type_user == "Formateur":
                    user = Formateur(
                        nom=nom, prenom=prenom, email=email, role=Role.formateur,
                        specialite=specialite, date_embauche=date_embauche,
                        taux_horaire=taux_horaire, bio=bio if 'bio' in locals() else None,
                        date_creation=now_utc
                    )
                elif type_user == "Staff":
                    user = StaffPedagogique(
                        nom=nom, prenom=prenom, email=email, role=Role.staff,
                        poste=poste, date_prise_fonction=date_prise_fonction,
                        date_creation=now_utc
                    )
                elif type_user == "Admin":
                    user = Admin(
                        nom=nom, prenom=prenom, email=email, role=Role.admin,
                        niveau_acces=niveau_acces, date_promotion=date_promotion,
                        date_creation=now_utc
                    )
                
                db.add(user)
                db.commit()
                st.success(f"Utilisateur {prenom} {nom} créé avec succès !")
            except Exception as e:
                db.rollback()
                st.error(f"Erreur lors de la création : {e}")

with tab_liste:
    st.subheader("Filtrer les utilisateurs")
    col_f1, col_f2 = st.columns(2)
    filtre_role = col_f1.selectbox("Filtrer par rôle", ["Tous", "apprenant", "formateur", "staff", "admin"])
    filtre_statut = col_f2.selectbox("Filtrer par statut", ["Tous", "Actif", "Inactif"])
    
    Utilisateurs = (
        db.exec(select(Apprenant)).all() + 
        db.exec(select(Formateur)).all() + 
        db.exec(select(StaffPedagogique)).all() + 
        db.exec(select(Admin)).all()
    )
    
    utilisateurs_filtres = []
    for user in Utilisateurs:
        role_match = (filtre_role == "Tous" or user.role.value == filtre_role)
        statut_match = (
            filtre_statut == "Tous" or 
            (filtre_statut == "Actif" and user.is_active) or 
            (filtre_statut == "Inactif" and not user.is_active)
        )
        if role_match and statut_match:
            utilisateurs_filtres.append(user)
            
    if utilisateurs_filtres:
        data_u = [{
            "ID": user.id, "Nom": user.nom, "Prénom": user.prenom, 
            "Email": user.email, "Rôle": user.role.value, "Actif": user.is_active
        } for user in utilisateurs_filtres]
        st.dataframe(data_u, width='stretch')
    else:
        st.info("Aucun utilisateur trouvé.")