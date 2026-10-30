import streamlit as st
from sqlmodel import select
from database import get_session

from models.salle import Salle
from models.session import Session
from models.user import Apprenant, Formateur
from models.inscription import Inscription, StatutInscription

st.set_page_config(page_title="CF-Tech - Accueil", layout="wide", page_icon="🎓")
st.title("CF-Tech - Tableau de bord")

db = next(get_session())

try:
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
    st.subheader("Statistiques de remplissage")
    if sessions:
        capacite_totale_offerte = sum([s.capacite_max for s in sessions])
        total_inscrits = len(inscriptions)
        taux_remplissage = (total_inscrits / capacite_totale_offerte * 100) if capacite_totale_offerte > 0 else 0
        st.progress(min(taux_remplissage / 100.0, 1.0), text=f"Taux de remplissage moyen global : {taux_remplissage:.1f}%")
    else:
        st.info("Aucune session disponible pour calculer le taux de remplissage.")

except Exception as e:
    st.error(f"Erreur de chargement des données : {e}")
    st.info("Vérifiez que vos migrations Alembic ont bien été appliquées via 'alembic upgrade head'.")