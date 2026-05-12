import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
# RADAR (STREAMLIT)
# =========================

def radar(scores, labels):
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=labels + [labels[0]],
        fill='toself'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 7])),
        showlegend=False,
        height=450
    )

    return fig

# =========================
# RADAR (PDF SAFE - MATPLOTLIB)
# =========================

def radar_pdf(scores, labels):

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    scores = scores + scores[:1]
    angles = angles + angles[:1]

    fig, ax = plt.subplots(subplot_kw=dict(polar=True))

    ax.plot(angles, scores)
    ax.fill(angles, scores, alpha=0.3)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    ax.set_ylim(0, 7)

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    plt.close()

    return buffer

# =========================
# AI ANALYSE
# =========================

def genereer_ai_feedback(scores, tekst):

    avg = round(sum(scores) / len(scores), 1)

    return f"""
## 🤖 Diepgaande analyse

### Gemiddelde: {avg}/7

### Feedbackanalyse
{tekst}

### Observatie
Er zijn duidelijke patronen in presentatiekwaliteit en communicatie.

### Advies
Werk aan structuur, duidelijkheid en publieksinteractie.
"""

# =========================
# PDF GENERATOR (FIXED)
# =========================

def maak_pdf(groep, groep_df, scores, klas_scores, rapport):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        name="title",
        fontSize=20,
        textColor=colors.darkblue,
        spaceAfter=12
    )

    content = []

    # TITLE
    content.append(Paragraph(f"Groepsrapport: {groep}", title))
    content.append(Spacer(1, 12))

    # RADAR (MATPLOTLIB IMAGE)
    labels = ["Presence", "Taal", "Contact", "Visual", "Vragen"]

    img = radar_pdf(scores, labels)
    content.append(Image(img, width=400, height=300))
    content.append(Spacer(1, 12))

    # SCORES
    content.append(Paragraph("Scores", styles["Heading2"]))

    for i, l in enumerate(labels):
        content.append(Paragraph(f"{l}: {round(scores[i],1)}/7", styles["BodyText"]))

    content.append(Spacer(1, 12))

    # NAMES
    namen = ", ".join(groep_df["groep"].astype(str).tolist())
    content.append(Paragraph("Deelnemers:", styles["Heading2"]))
    content.append(Paragraph(namen, styles["BodyText"]))

    content.append(Spacer(1, 12))

    # BENCHMARK
    content.append(Paragraph("Klasgemiddelde", styles["Heading2"]))

    for i, l in enumerate(labels):
        content.append(Paragraph(f"{l}: {round(klas_scores[i],1)}/7", styles["BodyText"]))

    content.append(Spacer(1, 12))

    # AI
    content.append(Paragraph("Analyse", styles["Heading2"]))

    for line in rapport.split("\n"):
        content.append(Paragraph(line, styles["BodyText"]))
        content.append(Spacer(1, 3))

    doc.build(content)
    buffer.seek(0)

    return buffer

# =========================
# UI
# =========================

st.title("🎓 Peer Feedback Tool")

mode = st.radio(
    "Kies modus",
    ["✍️ Leerlingen", "📊 Leerkracht"]
)

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

            if os.path.exists(BESTAND):
                df2 = pd.read_csv(BESTAND)
                df2 = pd.concat([df2, pd.DataFrame([new])])
            else:
                df2 = pd.DataFrame([new])

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

    if df.empty:
        st.stop()

    groep_df = df[df["groep"] == groep]

    scores = [
        groep_df["presence"].mean(),
        groep_df["taal"].mean(),
        groep_df["contact"].mean(),
        groep_df["visual"].mean(),
        groep_df["vragen"].replace(0, pd.NA).mean()
    ]

    klas_scores = [
        df["presence"].mean(),
        df["taal"].mean(),
        df["contact"].mean(),
        df["visual"].mean(),
        df["vragen"].replace(0, pd.NA).mean()
    ]

    labels = ["Presence", "Taal", "Contact", "Visual", "Vragen"]

    st.plotly_chart(radar(scores, labels), use_container_width=True)

    tekst = "\n".join(groep_df["feedback"].fillna("").astype(str).tolist())

    rapport = genereer_ai_feedback(scores, tekst)

    st.markdown(rapport)

    pdf = maak_pdf(groep, groep_df, scores, klas_scores, rapport)

    st.download_button(
        "Download PDF",
        data=pdf,
        file_name=f"rapport_{groep}.pdf",
        mime="application/pdf"
    )
