import streamlit as st
from sqlmodel import select
from database import get_session
from models.salle import Salle

st.set_page_config(page_title="CF-Tech - Salles", layout="wide")
st.header("Gestion des Salles")
db = next(get_session())

with st.form("form_salle"):
    nom = st.text_input("Nom")
    capacite = st.number_input("Capacité max", min_value=1, value=15)
    loc = st.text_input("Localisation")
    if st.form_submit_button("Créer"):
        try:
            db.add(Salle(nom=nom, capacite=capacite, localisation=loc))
            db.commit()
            st.success("Salle créée !")
        except Exception as e:
            db.rollback()
            st.error(f"Erreur : {e}")
        
salles = db.exec(select(Salle)).all()
st.dataframe([{"ID": s.id, "Nom": s.nom, "Capacité": s.capacite, "Lieu": s.localisation, "Active": s.is_active} for s in salles])