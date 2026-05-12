import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import io
from collections import Counter

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="🎓 Peer Feedback Tool", layout="wide")

BESTAND = "peer_feedback.csv"
LEERKRACHT_PIN = "1234"

GROEPEN = [
    "Asa en Stella",
    "Alexander en Boudewijn",
    "Minne, Anne en Liam",
    "Ella, Lena en Laura",
    "Casper, Juul en Linus",
    "Axl, Sam en Arno",
    "Eowyn en Liz",
    "Batool en Alyssa",
    "Sadie en Anastasiia"
]

# =========================
# DATA
# =========================

def load_data():
    if os.path.exists(BESTAND):
        return pd.read_csv(BESTAND)
    return pd.DataFrame()

df = load_data()

# =========================
# OPTIES
# =========================

positieve_opties = [
    "Duidelijke presentatie","Goede samenwerking","Sterke visuals","Goede structuur",
    "Zelfzeker gebracht","Goede timing","Goede uitleg","Goede lichaamstaal",
    "Sterke voorbereiding","Publiek betrokken","Duidelijke stem","Goede interactie"
]

negatieve_opties = [
    "Te snel gepresenteerd","Weinig oogcontact","Onvoldoende structuur","Zenuwachtig",
    "Te weinig uitleg","Slechte timing","Onduidelijke uitleg","Monotone stem",
    "Te weinig voorbereiding","Publiek niet betrokken","Onzeker gedrag","Slides te druk"
]

# =========================
# UI HELPER (MAX 3 LOGICA)
# =========================

def checkbox_limited(options, prefix):
    selected = []

    cols = st.columns(3)

    # eerst tellen wat al gekozen is
    temp = []

    for i, opt in enumerate(options):
        # disable als al 3 gekozen EN deze optie is NIET al gekozen
        disabled = False

        if len(selected) >= 3:
            disabled = True

        checked = cols[i % 3].checkbox(
            opt,
            key=f"{prefix}_{i}",
            disabled=disabled
        )

        if checked:
            temp.append(opt)

    # extra safety: max 3 houden
    return temp[:3]

# =========================
# RADAR
# =========================

def radar(scores, klas_scores, labels):

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=klas_scores + [klas_scores[0]],
        theta=labels + [labels[0]],
        fill='toself',
        name="Klasgemiddelde"
    ))

    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=labels + [labels[0]],
        fill='toself',
        name="Groep"
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 7])),
        height=500,
        showlegend=True
    )

    return fig

# =========================
# UI
# =========================

st.title("🎓 Peer Feedback Tool")

mode = st.radio("Kies modus", ["✍️ Leerlingen", "📊 Leerkracht"])

# =========================
# LEERLINGEN
# =========================

if mode == "✍️ Leerlingen":

    groep = st.selectbox("Groep", GROEPEN)

    with st.form("form"):

        presence = st.slider("Presence", 1, 7, 5)
        taal = st.slider("Taal", 1, 7, 5)
        contact = st.slider("Contact", 1, 7, 5)
        visual = st.slider("Visual", 1, 7, 5)
        vragen = st.slider("Vragen", 1, 7, 5)

        st.markdown("### 👍 Positieve punten (max 3)")
        positief = checkbox_limited(positieve_opties, "pos")

        st.markdown("### 👎 Werkpunten (max 3)")
        werkpunt = checkbox_limited(negatieve_opties, "neg")

        submit = st.form_submit_button("Opslaan")

    if submit:

        new = {
            "groep": groep,
            "presence": presence,
            "taal": taal,
            "contact": contact,
            "visual": visual,
            "vragen": vragen,

            "positief_1": positief[0] if len(positief)>0 else None,
            "positief_2": positief[1] if len(positief)>1 else None,
            "positief_3": positief[2] if len(positief)>2 else None,

            "werkpunt_1": werkpunt[0] if len(werkpunt)>0 else None,
            "werkpunt_2": werkpunt[1] if len(werkpunt)>1 else None,
            "werkpunt_3": werkpunt[2] if len(werkpunt)>2 else None,

            "tijdstip": datetime.now()
        }

        df2 = pd.concat([df, pd.DataFrame([new])])
        df2.to_csv(BESTAND, index=False)

        st.success("Opgeslagen!")

# =========================
# LEERKRACHT (zelfde als eerder)
# =========================

if mode == "📊 Leerkracht":

    pin = st.text_input("PIN", type="password")
    if pin != LEERKRACHT_PIN:
        st.stop()

    groep = st.selectbox("Groep", GROEPEN)

    groep_df = df[df["groep"] == groep]

    scores = [
        groep_df["presence"].mean(),
        groep_df["taal"].mean(),
        groep_df["contact"].mean(),
        groep_df["visual"].mean(),
        groep_df["vragen"].mean()
    ]

    klas_scores = [
        df["presence"].mean(),
        df["taal"].mean(),
        df["contact"].mean(),
        df["visual"].mean(),
        df["vragen"].mean()
    ]

    st.plotly_chart(
        radar(scores, klas_scores, ["Presence","Taal","Contact","Visual","Vragen"]),
        use_container_width=True
    )
