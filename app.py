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
    Image,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

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
# STELLINGEN (ALLE ZICHTBAAR)
# =========================

positieve_opties = [
    "Duidelijke presentatie",
    "Goede samenwerking",
    "Sterke visuals",
    "Goede structuur",
    "Zelfzeker gebracht",
    "Goede timing",
    "Goede uitleg",
    "Goede lichaamstaal",
    "Sterke voorbereiding",
    "Publiek betrokken",
    "Duidelijke stem",
    "Goede interactie",
]

negatieve_opties = [
    "Te snel gepresenteerd",
    "Weinig oogcontact",
    "Onvoldoende structuur",
    "Zenuwachtig",
    "Te weinig uitleg",
    "Slechte timing",
    "Onduidelijke uitleg",
    "Monotone stem",
    "Te weinig voorbereiding",
    "Publiek niet betrokken",
    "Onzeker gedrag",
    "Slides te druk"
]

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
        showlegend=True   # 👈 belangrijk
    )

    return fig

# =========================
# GROEP ANALYSE
# =========================

def analyseer_groep(groep_df):

    positief = []
    werkpunt = []

    for col in ["positief_1","positief_2","positief_3"]:
        positief += groep_df[col].dropna().tolist()

    for col in ["werkpunt_1","werkpunt_2","werkpunt_3"]:
        werkpunt += groep_df[col].dropna().tolist()

    return (
        [x[0] for x in Counter(positief).most_common(5)],
        [x[0] for x in Counter(werkpunt).most_common(5)]
    )

# =========================
# PDF RADAR (met LEGEND)
# =========================

def radar_pdf(scores, klas_scores, labels):

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    scores = scores + scores[:1]
    klas_scores = klas_scores + klas_scores[:1]

    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))

    ax.plot(angles, klas_scores, linestyle="dashed", label="Klasgemiddelde")
    ax.fill(angles, klas_scores, alpha=0.1)

    ax.plot(angles, scores, label="Groep")
    ax.fill(angles, scores, alpha=0.3)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 7)

    # ✅ LEGEND TOEGEVOEGD
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=200, bbox_inches="tight")
    buffer.seek(0)
    plt.close()

    return buffer

# =========================
# PDF
# =========================

def maak_pdf(groep, scores, klas_scores, groep_df):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    labels = ["Presence", "Taal", "Contact", "Visual", "Vragen"]

    content = []

    # TITLE
    content.append(Paragraph(f"Peer Feedback Rapport - {groep}", styles["Title"]))
    content.append(Spacer(1, 20))

    # RADAR
    img = radar_pdf(scores, klas_scores, labels)
    content.append(Image(img, width=400, height=400))
    content.append(Spacer(1, 20))

    # ANALYSE
    top_pos, top_neg = analyseer_groep(groep_df)

    content.append(Paragraph("STERKE PUNTEN", styles["Heading2"]))
    content.append(Paragraph(", ".join(top_pos) if top_pos else "Geen data", styles["BodyText"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph("WERKPUNTEN", styles["Heading2"]))
    content.append(Paragraph(", ".join(top_neg) if top_neg else "Geen data", styles["BodyText"]))

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
    vragen = st.slider("Vragen", 1, 7, 5)

    st.markdown("### 👍 Positieve punten")
    positief = []
    for i, opt in enumerate(positieve_opties):
        if st.checkbox(opt, key=f"pos_{i}"):
            positief.append(opt)

    st.markdown("### 👎 Werkpunten")
    werkpunt = []
    for i, opt in enumerate(negatieve_opties):
        if st.checkbox(opt, key=f"neg_{i}"):
            werkpunt.append(opt)

    # 👇 MOET BINNEN FORM STAAN
    submit = st.form_submit_button("Opslaan")


# 👇 BUITEN FORM
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

    st.plotly_chart(radar(scores, klas_scores, ["Presence","Taal","Contact","Visual","Vragen"]),
                    use_container_width=True)

    pdf = maak_pdf(groep, scores, klas_scores, groep_df)

    st.download_button(
        "Download PDF",
        data=pdf,
        file_name=f"rapport_{groep}.pdf",
        mime="application/pdf"
    )
