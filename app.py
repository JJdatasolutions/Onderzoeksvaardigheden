import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import io

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    HRFlowable
)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER

import requests

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
# SECRETS (SAFE)
# =========================

HF_TOKEN = st.secrets.get("HF_TOKEN", None)

# =========================
# DATA
# =========================

def load_data():
    if os.path.exists(BESTAND):
        return pd.read_csv(BESTAND)
    return pd.DataFrame()

df = load_data()

# =========================
# RADAR CHART
# =========================

def radar(scores, klas_scores, labels):

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=klas_scores + [klas_scores[0]],
        theta=labels + [labels[0]],
        fill='toself',
        name="Klasgemiddelde",
        opacity=0.2
    ))

    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=labels + [labels[0]],
        fill='toself',
        name="Groep",
        opacity=0.7
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 7])),
        height=550
    )

    return fig

# =========================
# RADAR PDF
# =========================

def radar_pdf(scores, klas_scores, labels):

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    scores = scores + scores[:1]
    klas_scores = klas_scores + klas_scores[:1]

    fig, ax = plt.subplots(figsize=(6.5, 6.5), subplot_kw=dict(polar=True))

    ax.plot(angles, klas_scores, linestyle="dashed", label="Klas")
    ax.fill(angles, klas_scores, alpha=0.1)

    ax.plot(angles, scores, label="Groep")
    ax.fill(angles, scores, alpha=0.3)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 7)
    ax.legend()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", dpi=200)
    buffer.seek(0)
    plt.close()

    return buffer

# =========================
# AI FEEDBACK (SAFE + FALLBACK)
# =========================

def genereer_ai_feedback(scores, klas_scores, tekst):

    avg = round(sum(scores) / len(scores), 1)

    labels = ["Presence", "Taal", "Contact", "Visual", "Vragen"]

    # -------------------------
    # 1. Analyse per criterium
    # -------------------------

    sterk = []
    zwak = []

    for i, s in enumerate(scores):
        klas = klas_scores[i]

        if s >= 6 and s >= klas:
            sterk.append(labels[i])
        elif s < klas:
            zwak.append(labels[i])

    # -------------------------
    # 2. Tekstanalyse (ECHTE variatie per groep)
    # -------------------------

    tekst_lower = tekst.lower()

    positieve_woorden = ["goed", "sterk", "duidelijk", "vlot", "interessant", "fijn", "goed voorbereid"]
    negatieve_woorden = ["onduidelijk", "onzeker", "stil", "chaotisch", "moeilijk", "te snel", "te traag"]

    pos_count = sum(1 for w in positieve_woorden if w in tekst_lower)
    neg_count = sum(1 for w in negatieve_woorden if w in tekst_lower)

    if pos_count > neg_count:
        toon = "overwegend positief"
    elif neg_count > pos_count:
        toon = "kritisch"
    else:
        toon = "gemengd"

    # -------------------------
    # 3. Dynamische samenvatting (verschilt per groep!)
    # -------------------------

    samenvatting = f"""
De groep behaalt een gemiddelde score van {avg}/7.

De feedback is {toon} en toont duidelijke aandacht voor presentatievaardigheden.
Er is vooral commentaar op {', '.join(zwak) if zwak else 'een stabiel niveau over alle onderdelen'}.
"""

    # -------------------------
    # 4. Variabele conclusie
    # -------------------------

    if avg >= 6:
        conclusie = "De presentatie is sterk uitgewerkt en professioneel gebracht."
    elif avg >= 5:
        conclusie = "De presentatie is degelijk met ruimte voor verfijning."
    else:
        conclusie = "De presentatie toont duidelijke groeimogelijkheden."

    # -------------------------
    # 5. Eindrapport
    # -------------------------

    feedback = f"""
SAMENVATTING
{samenvatting}

STERKE PUNTEN
{", ".join(sterk) if sterk else "Geen duidelijke uitschieters, maar een stabiel basisniveau."}

VERBETERPUNTEN
{", ".join(zwak) if zwak else "Geen duidelijke zwakke punten t.o.v. klasgemiddelde."}

CONCLUSIE
{conclusie}
"""

    return {
        "gemiddelde": avg,
        "feedback": feedback,
        "positief": sterk,
        "verbeter": zwak,
        "profiel": "Presentator"
    }
# =========================
# PDF EXPORT
# =========================

def maak_pdf(groep, scores, klas_scores, analyse):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()

    content = []

    labels = ["Presence", "Taal", "Contact", "Visual", "Vragen"]

    # TITLE
    content.append(Paragraph(f"Peer Feedback Rapport - {groep}", styles["Title"]))
    content.append(Spacer(1, 20))

    # SCORE
    content.append(Paragraph(f"Gemiddelde score: {analyse['gemiddelde']}/7", styles["Heading2"]))
    content.append(Spacer(1, 10))

    # RADAR
    img = radar_pdf(scores, klas_scores, labels)
    content.append(Image(img, width=400, height=400))

    content.append(Spacer(1, 20))

    # AI TEXT
    content.append(Paragraph("Analyse", styles["Heading2"]))
    content.append(Paragraph(analyse["feedback"], styles["BodyText"]))

    doc.build(content)
    buffer.seek(0)

    return buffer

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
        vragen = st.slider("Vragen", 0, 7, 5)

        feedback = st.text_area("Feedback")

        submit = st.form_submit_button("Opslaan")

        if submit:

            new = {
                "groep": groep,
                "presence": presence,
                "taal": taal,
                "contact": contact,
                "visual": visual,
                "vragen": vragen,
                "feedback": feedback,
                "tijdstip": datetime.now()
            }

            df2 = pd.concat([df, pd.DataFrame([new])])
            df2.to_csv(BESTAND, index=False)

            st.success("Opgeslagen!")

# =========================
# LEERKRACHT
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

    labels = ["Presence", "Taal", "Contact", "Visual", "Vragen"]

    st.plotly_chart(radar(scores, klas_scores, labels), use_container_width=True)

    tekst = "\n".join(groep_df["feedback"].astype(str).tolist())

    analyse = genereer_ai_feedback(scores, klas_scores, tekst)

    st.markdown("## AI Analyse")
    st.write(analyse["feedback"])

    pdf = maak_pdf(groep, scores, klas_scores, analyse)

    st.download_button(
        "Download PDF",
        data=pdf,
        file_name=f"rapport_{groep}.pdf",
        mime="application/pdf"
    )
