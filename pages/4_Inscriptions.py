import streamlit as st
from sqlmodel import select
from datetime import datetime, timezone
from database import get_session

from models.session import Session, StatutSession
from models.user import Apprenant
from models.inscription import Inscription, StatutInscription

st.set_page_config(page_title="CF-Tech - Inscriptions", layout="wide")
st.header("Gestion des Inscriptions")
db = next(get_session())

apprenants = db.exec(select(Apprenant).where(Apprenant.is_active == True)).all()
sessions = db.exec(select(Session).where(Session.statut == StatutSession.OPEN)).all()

if not apprenants or not sessions:
    st.warning("Assurez-vous d'avoir des apprenants actifs et des sessions ouvertes.")
else:
    apprenant_selectionne = st.selectbox("Sélectionner un apprenant", apprenants, format_func=lambda a: f"{a.nom} {a.prenom} ({a.email})")
    st.subheader(f"Inscriptions pour {apprenant_selectionne.prenom} {apprenant_selectionne.nom}")
    
    inscriptions_existantes = db.exec(select(Inscription).where(Inscription.apprenant_id == apprenant_selectionne.id)).all()
    dict_inscriptions = {ins.session_id: ins for ins in inscriptions_existantes}
    
    for session in sessions:
        inscrits_session = db.exec(select(Inscription).where(Inscription.session_id == session.id, Inscription.statut_inscription == StatutInscription.ENREGISTRE)).all()
        nb_inscrits = len(inscrits_session)
        places_restantes = session.capacite_max - nb_inscrits
        
        col1, col2, col3 = st.columns([3, 2, 2])
        col1.markdown(f"{session.titre}<br><small>Du {session.date_debut.strftime('%Y-%m-%d')} au {session.date_fin.strftime('%Y-%m-%d')} | Places libres : {places_restantes}/{session.capacite_max}</small>", unsafe_allow_html=True)
        
        inscription_actuelle = dict_inscriptions.get(session.id)
        est_inscrit = inscription_actuelle and inscription_actuelle.statut_inscription == StatutInscription.ENREGISTRE
        
        if est_inscrit:
            col2.info("Inscrit !")
            if col3.button("Se désinscrire", key=f"desinc_{session.id}"):
                inscription_actuelle.statut_inscription = StatutInscription.DESINSCRIT
                db.add(inscription_actuelle)
                db.commit()
                st.success("Désinscription effectuée.")
                st.rerun()
        else:
            if places_restantes > 0:
                col2.text("Disponible")
                if col3.button("S'inscrire", key=f"inc_{session.id}"):
                    if inscription_actuelle:
                        inscription_actuelle.statut_inscription = StatutInscription.ENREGISTRE
                        inscription_actuelle.date_inscription = datetime.now(timezone.utc)
                        db.add(inscription_actuelle)
                    else:
                        nouvelle_inscription = Inscription(
                            apprenant_id=apprenant_selectionne.id,
                            session_id=session.id,
                            statut_inscription=StatutInscription.ENREGISTRE,
                            date_inscription=datetime.now(timezone.utc)
                        )
                        db.add(nouvelle_inscription)
                    db.commit()
                    st.success("Inscription validée avec succès !")
                    st.rerun()
            else:
                col2.warning("Complet !")
                col3.text("-")