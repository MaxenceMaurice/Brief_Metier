import streamlit as st
from sqlmodel import select
from datetime import date, datetime, timezone
from database import get_session

from models.salle import Salle
from models.session import Session, StatutSession
from models.user import Apprenant, Formateur, StaffPedagogique, Admin, Role, NiveauAcces
from models.inscription import Inscription, StatutInscription

st.set_page_config(page_title="CF-Tech - Gestion", layout="wide")
st.title("🎓 CF-Tech - Application de Gestion")
db = next(get_session())

menu = st.sidebar.selectbox("Navigation", ["Dashboard", "Salles", "Utilisateurs", "Sessions", "Inscriptions"])

# ==========================================
# 1. GESTION DES UTILISATEURS (CRUD + Filtres)
# ==========================================
if menu == "Utilisateurs":
    st.header("👥 Gestion des Utilisateurs")
    
    tab_ajout, tab_liste = st.tabs(["Créer un utilisateur", "Liste et Filtres"])
    
    with tab_ajout:
        type_user = st.selectbox("Rôle de l'utilisateur", ["Apprenant", "Formateur", "Staff", "Admin"])
        
        with st.form("form_user"):
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email")
            
            # Champs spécifiques complets selon le rôle
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
            else: # Admin
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
        
        tous = (
            db.exec(select(Apprenant)).all() + 
            db.exec(select(Formateur)).all() + 
            db.exec(select(StaffPedagogique)).all() + 
            db.exec(select(Admin)).all()
        )
        
        utilisateurs_filtres = []
        for u in tous:
            role_match = (filtre_role == "Tous" or u.role.value == filtre_role)
            statut_match = (
                filtre_statut == "Tous" or 
                (filtre_statut == "Actif" and u.is_active) or 
                (filtre_statut == "Inactif" and not u.is_active)
            )
            if role_match and statut_match:
                utilisateurs_filtres.append(u)
                
        if utilisateurs_filtres:
            data_u = [{
                "ID": u.id, "Nom": u.nom, "Prénom": u.prenom, 
                "Email": u.email, "Rôle": u.role.value, "Actif": u.is_active
            } for u in utilisateurs_filtres]
            st.dataframe(data_u, width='stretch')
        else:
            st.info("Aucun utilisateur trouvé.")

# ==========================================
# 2. GESTION DES SALLES
# ==========================================
elif menu == "Salles":
    st.header("🏢 Gestion des Salles")
    with st.form("form_salle"):
        nom = st.text_input("Nom")
        capacite = st.number_input("Capacité max", min_value=1, value=15)
        loc = st.text_input("Localisation")
        if st.form_submit_button("Créer"):
            db.add(Salle(nom=nom, capacite=capacite, localisation=loc))
            db.commit()
            st.success("Salle créée !")
            
    salles = db.exec(select(Salle)).all()
    st.dataframe([{"ID": s.id, "Nom": s.nom, "Capacité": s.capacite, "Lieu": s.localisation, "Active": s.is_active} for s in salles], width='stretch')

# ==========================================
# 3. GESTION DES SESSIONS (Validations & Conflits)
# ==========================================
elif menu == "Sessions":
    st.header("📅 Gestion des Sessions")
    salles = db.exec(select(Salle)).all()
    formateurs = db.exec(select(Formateur)).all()
    
    if not salles or not formateurs:
        st.warning("⚠️ Veuillez créer au moins une salle et un formateur avant de planifier une session.")
    else:
        with st.form("form_session"):
            titre = st.text_input("Titre de la session")
            description = st.text_area("Description")
            date_debut = st.date_input("Date de début")
            date_fin = st.date_input("Date de fin")
            capacite_max = st.number_input("Capacité maximale de la session", min_value=1, value=10)
            prerequis_txt = st.text_input("Prérequis (séparés par des virgules)")
            
            salle_choisie = st.selectbox("Salle assignée", salles, format_func=lambda s: f"{s.nom} (Capacité : {s.capacite})")
            formateur_choisi = st.selectbox("Formateur assigné", formateurs, format_func=lambda f: f"{f.nom} {f.prenom}")
            statut = st.selectbox("Statut", [StatutSession.OPEN, StatutSession.CLOSED, StatutSession.ARCHIVED])
            
            if st.form_submit_button("Créer la session"):
                if capacite_max > salle_choisie.capacite:
                    st.error(f"❌ Erreur : La capacité de la session ({capacite_max}) dépasse la capacité de la salle '{salle_choisie.nom}' ({salle_choisie.capacite}).")
                else:
                    dt_debut = datetime.combine(date_debut, datetime.min.time()).replace(tzinfo=timezone.utc)
                    dt_fin = datetime.combine(date_fin, datetime.max.time()).replace(tzinfo=timezone.utc)
                    
                    if dt_debut > dt_fin:
                        st.error("❌ Erreur : La date de début ne peut pas être supérieure à la date de fin.")
                    else:
                        # Vérification des conflits d'occupation de salle en temps réel
                        sessions_existantes = db.exec(
                            select(Session).where(
                                Session.salle_id == salle_choisie.id, 
                                Session.statut == StatutSession.OPEN
                            )
                        ).all()
                        
                        conflit = False
                        for se in sessions_existantes:
                            se_debut = se.date_debut.replace(tzinfo=timezone.utc) if se.date_debut.tzinfo is None else se.date_debut
                            se_fin = se.date_fin.replace(tzinfo=timezone.utc) if se.date_fin.tzinfo is None else se.date_fin
                            if not (dt_fin < se_debut or dt_debut > se_fin):
                                conflit = True
                                break
                                
                        if conflit:
                            st.error(f"❌ Conflit de planning : La salle '{salle_choisie.nom}' est déjà occupée sur cette période !")
                        else:
                            liste_prerequis = [p.strip() for p in prerequis_txt.split(",")] if prerequis_txt else None
                            session_obj = Session(
                                titre=titre, description=description,
                                date_debut=dt_debut, date_fin=dt_fin,
                                capacite_max=capacite_max, statut=statut,
                                prerequis=liste_prerequis, salle_id=salle_choisie.id,
                                formateur_id=formateur_choisi.id
                            )
                            db.add(session_obj)
                            db.commit()
                            st.success("✅ Session créée avec succès et validée !")
                            
    st.subheader("Liste des sessions enregistrées")
    sessions = db.exec(select(Session)).all()
    if sessions:
        st.dataframe([{
            "ID": s.id, "Titre": s.titre, 
            "Début": s.date_debut.strftime("%Y-%m-%d") if s.date_debut else "",
            "Fin": s.date_fin.strftime("%Y-%m-%d") if s.date_fin else "", 
            "Capacité": s.capacite_max, "Statut": s.statut
        } for s in sessions], width='stretch')
    else:
        st.info("Aucune session enregistrée.")

# ==========================================
# 4. GESTION DES INSCRIPTIONS
# ==========================================
elif menu == "Inscriptions":
    st.header("📝 Gestion des Inscriptions")
    apprenants = db.exec(select(Apprenant).where(Apprenant.is_active == True)).all()
    sessions = db.exec(select(Session).where(Session.statut == StatutSession.OPEN)).all()
    
    if not apprenants or not sessions:
        st.warning("Assurez-vous d'avoir des apprenants actifs et des sessions ouvertes.")
    else:
        apprenant_selectionne = st.selectbox("Sélectionner un apprenant", apprenants, format_func=lambda a: f"{a.nom} {a.prenom} ({a.email})")
        st.subheader(f"Inscriptions pour {apprenant_selectionne.prenom} {apprenant_selectionne.nom}")
        
        # Dictionnaire pour retrouver facilement l'inscription existante par session_id
        inscriptions_existantes = db.exec(select(Inscription).where(Inscription.apprenant_id == apprenant_selectionne.id)).all()
        dict_inscriptions = {ins.session_id: ins for ins in inscriptions_existantes}
        
        for s in sessions:
            # Calcul précis des places restantes en comptant uniquement les actifs
            inscrits_session = db.exec(select(Inscription).where(Inscription.session_id == s.id, Inscription.statut_inscription == StatutInscription.ENREGISTRE)).all()
            nb_inscrits = len(inscrits_session)
            places_restantes = s.capacite_max - nb_inscrits
            
            col1, col2, col3 = st.columns([3, 2, 2])
            col1.markdown(f"**{s.titre}**<br><small>Du {s.date_debut.strftime('%Y-%m-%d')} au {s.date_fin.strftime('%Y-%m-%d')} | Places libres : {places_restantes}/{s.capacite_max}</small>", unsafe_allow_html=True)
            
            inscription_actuelle = dict_inscriptions.get(s.id)
            est_inscrit = inscription_actuelle and inscription_actuelle.statut_inscription == StatutInscription.ENREGISTRE
            
            if est_inscrit:
                col2.info("Inscrit ✅")
                if col3.button("Se désinscrire", key=f"desinc_{s.id}"):
                    # Mise à jour du statut existant au lieu de recréer une ligne
                    inscription_actuelle.statut_inscription = StatutInscription.DESINSCRIT
                    db.add(inscription_actuelle)
                    db.commit()
                    st.success("Désinscription effectuée.")
                    st.rerun()
            else:
                if places_restantes > 0:
                    col2.text("Disponible")
                    if col3.button("S'inscrire", key=f"inc_{s.id}"):
                        if inscription_actuelle:
                            # S'il existe déjà une ancienne ligne (désinscrit), on la réactive
                            inscription_actuelle.statut_inscription = StatutInscription.ENREGISTRE
                            inscription_actuelle.date_inscription = datetime.now(timezone.utc)
                            db.add(inscription_actuelle)
                        else:
                            # Sinon on crée la première inscription
                            nouvelle_ins = Inscription(
                                apprenant_id=apprenant_selectionne.id,
                                session_id=s.id,
                                statut_inscription=StatutInscription.ENREGISTRE,
                                date_inscription=datetime.now(timezone.utc)
                            )
                            db.add(nouvelle_ins)
                        db.commit()
                        st.success("Inscription validée avec succès !")
                        st.rerun()
                else:
                    col2.warning("Complet ❌")
                    col3.text("-")

# ==========================================
# 5. DASHBOARD DE REPORTING
# ==========================================
elif menu == "Dashboard":
    st.header("📊 Tableau de bord & Reporting")
    apprenants = db.exec(select(Apprenant)).all()
    formateurs = db.exec(select(Formateur)).all()
    salles = db.exec(select(Salle)).all()
    sessions = db.exec(select(Session)).all()
    inscriptions = db.exec(select(Inscription).where(Inscription.statut_inscription == StatutInscription.ENREGISTRE)).all()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Apprenants", len(apprenants))
    col2.metric("Total Formateurs", len(formateurs))
    col3.metric("Salles enregistrées", len(salles))
    col4.metric("Sessions totales", len(sessions))
    
    st.markdown("---")
    st.subheader("📈 Statistiques de remplissage")
    if sessions:
        capacite_totale_offerte = sum([s.capacite_max for s in sessions])
        total_inscrits = len(inscriptions)
        taux_remplissage = (total_inscrits / capacite_totale_offerte * 100) if capacite_totale_offerte > 0 else 0
        st.progress(min(taux_remplissage / 100.0, 1.0), text=f"Taux de remplissage moyen global : {taux_remplissage:.1f}%")