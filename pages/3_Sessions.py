import streamlit as st
from sqlmodel import select
from datetime import datetime, timezone
from database import get_session

from models.salle import Salle
from models.session import Session, StatutSession
from models.user import Formateur

st.set_page_config(page_title="CF-Tech - Sessions", layout="wide")
st.header("Gestion des Sessions")
db = next(get_session())

salles = db.exec(select(Salle)).all()
formateurs = db.exec(select(Formateur)).all()

if not salles or not formateurs:
    st.warning("Veuillez créer au moins une salle et un formateur avant de planifier une session.")
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
                st.error(f"La capacité de la session ({capacite_max}) dépasse la capacité de la salle '{salle_choisie.nom}' ({salle_choisie.capacite}).")
            else:
                dt_debut = datetime.combine(date_debut, datetime.min.time()).replace(tzinfo=timezone.utc)
                dt_fin = datetime.combine(date_fin, datetime.max.time()).replace(tzinfo=timezone.utc)
                
                if dt_debut > dt_fin:
                    st.error("La date de début ne peut pas être supérieure à la date de fin.")
                else:
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
                        st.error(f"La salle '{salle_choisie.nom}' est déjà occupée sur cette période !")
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
        "ID": session.id, "Titre": session.titre, 
        "Début": session.date_debut.strftime("%Y-%m-%d") if session.date_debut else "",
        "Fin": session.date_fin.strftime("%Y-%m-%d") if session.date_fin else "", 
        "Capacité": session.capacite_max, "Statut": session.statut
    } for session in sessions])
else:
    st.info("Aucune session enregistrée.")