import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATIE & STYLING ---
st.set_page_config(page_title="Peer Feedback Tool", page_icon="🎓", layout="centered")

GROEPEN = [
    "Asa en Stella", "Alexander en Boudewijn", "Minne, Anne en Liam",
    "Ella, Lena en Laura", "Casper, Juul en Linus", "Axl, Sam en Arno",
    "Eowyn en Liz", "Batool en Alyssa", "Sadie en Anastasiia"
]

HULPZINNEN = [
    "-- Kies een hulpzin --",
    "Ik vond de presentatie sterk omdat...",
    "Je gebruikte de visual erg goed toen je...",
    "Een tip voor de volgende keer is om...",
    "Je taalgebruik was erg rijk, vooral het woord...",
    "Ik kon je goed verstaan omdat..."
]

def create_radar_chart(scores, categories):
    """Architecturale keuze: Plotly voor interactieve visualisatie."""
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(31, 119, 180, 0.3)',
        line=dict(color='#1f77b4')
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20)
    )
    return fig

# --- UI LOGICA ---
st.title("🎓 Peer Evaluatie Onderzoeksvaardigheden")
st.write("Geef constructieve feedback aan je medeleerlingen.")

# Stap 1: Selectie
geselecteerde_groep = st.selectbox("Wie ben je aan het beoordelen?", ["-- Selecteer Groep --"] + GROEPEN)

if geselecteerde_groep != "-- Selecteer Groep --":
    with st.form("feedback_form"):
        st.subheader(f"Evaluatie voor: {geselecteerde_groep}")
        
        # Stap 2: Kwantitatieve scores
        col1, col2 = st.columns(2)
        with col1:
            score_presence = st.select_slider("Presence/Houding", options=range(1, 11), value=7)
            score_taal = st.select_slider("Rijke Taal", options=range(1, 11), value=7)
            score_contact = st.select_slider("Publiekscontact", options=range(1, 11), value=7)
        with col2:
            score_visual = st.select_slider("Kwaliteit Visual", options=range(1, 11), value=7)
            score_vragen = st.select_slider("Beantwoorden Vragen", options=range(0, 11), value=7, 
                                            help="Zet op 0 als er geen vragen gesteld zijn.")
        
        # Stap 3: Kwalitatieve feedback met ondersteuning
        st.subheader("Woordelijke feedback")
        hulpzin = st.selectbox("Hulp bij je feedback:", HULPZINNEN)
        user_text = st.text_area("Jouw aanvulling:", placeholder="Typ hier je feedback...")
        
        # Combineer tekst
        volledige_feedback = f"{hulpzin} {user_text}" if hulpzin != HULPZINNEN[0] else user_text

        submit = st.form_submit_button("Feedback Indienen")

        if submit:
            # In een echte productie-omgeving zouden we dit naar een database sturen.
            # Voor nu tonen we direct het resultaat (Preview voor de leerling).
            st.success(f"Bedankt! Je feedback voor {geselecteerde_groep} is verzonden.")
            
            # Rapport preview
            st.divider()
            st.subheader("Jouw ingediende rapport:")
            
            scores = [score_presence, score_taal, score_contact, score_visual, score_vragen]
            labels = ["Presence", "Taal", "Contact", "Visual", "Vragen"]
            
            st.plotly_chart(create_radar_chart(scores, labels))
            st.write(f"**Geleverde commentaar:** {volledige_feedback}")
