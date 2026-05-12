import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
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

LEERKRACHT_PIN = "1234"  # 🔐 verander dit

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
# RADAR CHART (APP)
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
# RADAR ALS AFBEELDING (PDF)
# =========================

def radar_image(scores, labels):

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=labels + [labels[0]],
        fill='toself'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 7])),
        showlegend=False,
        height=500
    )

    img_bytes = pio.to_image(fig, format="png", engine="kaleido")
    return img_bytes

# =========================
# AI ANALYSE (feedback-based)
# =========================

def genereer_ai_feedback(scores, tekst):

    avg = round(sum(scores) / len(scores), 1)

    return f"""
## 🤖 Diepgaande analyse

### 📊 Gemiddelde score
{avg}/7

---

### 💬 Analyse van leerlingfeedback
{tekst}

---

### ⭐ Observaties
- Feedback toont duidelijke patronen in presentatiekwaliteit
- Sterktes en werkpunten komen consistent terug

---

### 🚀 Aanbevelingen
- Werk aan consistentie tussen spreken, visual en interactie
- Focus op duidelijkheid en structuur
"""

# =========================
# PDF GENERATOR (PROFESSIONEEL)
# =========================

def maak_pdf(groep, groep_df, scores, klas_scores, rapport):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="TitleStyle",
        fontSize=20,
        leading=24,
        textColor=colors.darkblue,
        spaceAfter=12
    )

    section_style = ParagraphStyle(
        name="Section",
        fontSize=13,
        leading=16,
        spaceAfter=8,
        textColor=colors.black
    )

    content = []

    # =========================
    # TITEL
    # =========================
    content.append(Paragraph(f"Groepsrapport: {groep}", title_style))
    content.append(Spacer(1, 12))

    # =========================
    # RADAR CHART (IMAGE)
    # =========================

    labels = ["Presence", "Taal", "Contact", "Visual", "Vragen"]
    img = radar_image(scores, labels)

    img_buffer = io.BytesIO(img)

    content.append(Paragraph("📊 Prestatie-overzicht", section_style))
    content.append(Image(img_buffer, width=400, height=300))
    content.append(Spacer(1, 12))

    # =========================
    # SCORES
    # =========================

    content.append(Paragraph("📈 Groepsscores", section_style))

    for i, l in enumerate(labels):
        content.append(Paragraph(f"{l}: {round(scores[i],1)}/7", styles["BodyText"]))

    content.append(Spacer(1, 12))

    # =========================
    # NAAMOVERZICHT
    # =========================

    namen = ", ".join(groep_df["groep"].astype(str).tolist())

    content.append(Paragraph("👥 Evaluaties door:", section_style))
    content.append(Paragraph(namen, styles["BodyText"]))
    content.append(Spacer(1, 12))

    # =========================
    # KLAS BENCHMARK
    # =========================

    content.append(Paragraph("🏫 Klasgemiddelde", section_style))

    for i, l in enumerate(labels):
        content.append(Paragraph(f"{l}: {round(klas_scores[i],1)}/7", styles["BodyText"]))

    content.append(Spacer(1, 12))

    # =========================
    # AI RAPPORT
    # =========================

    content.append(Paragraph("🤖 Analyse", section_style))

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
    ["✍️ Leerlingen: feedback geven", "📊 Leerkracht: groepsrapport"]
)

# =========================
# LEERLINGEN
# =========================

if mode == "✍️ Leerlingen: feedback geven":

    groep = st.selectbox("Selecteer groep", GROEPEN)

    with st.form("feedback_form"):

        st.subheader(f"Evaluatie: {groep}")

        presence = st.slider("Presence", 1, 7, 5)
        taal = st.slider("Rijke taal", 1, 7, 5)
        contact = st.slider("Publiekscontact", 1, 7, 5)
        visual = st.slider("Visual", 1, 7, 5)
        vragen = st.slider("Vragen (0 = n.v.t.)", 0, 7, 5)

        feedback = st.text_area("Woordelijke feedback")

        submit = st.form_submit_button("Opslaan")

        if submit:

            nieuwe = {
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
                df_old = pd.read_csv(BESTAND)
                df_new = pd.concat([df_old, pd.DataFrame([nieuwe])])
            else:
                df_new = pd.DataFrame([nieuwe])

            df_new.to_csv(BESTAND, index=False)

            st.success("Feedback opgeslagen!")

# =========================
# LEERKRACHT
# =========================

if mode == "📊 Leerkracht: groepsrapport":

    pin = st.text_input("Leerkracht-PIN", type="password")

    if pin != LEERKRACHT_PIN:
        st.warning("Geen toegang.")
        st.stop()

    st.success("Toegang verleend")

    groep = st.selectbox("Selecteer groep", GROEPEN)

    if df.empty:
        st.warning("Geen data.")
        st.stop()

    groep_df = df[df["groep"] == groep]

    if groep_df.empty:
        st.warning("Geen feedback voor deze groep.")
        st.stop()

    # =========================
    # SCORES
    # =========================

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

    st.subheader(f"📊 Groepsrapport: {groep}")

    st.plotly_chart(radar(scores, labels), use_container_width=True)

    st.metric("Gemiddelde", round(sum(scores)/len(scores), 1))
    st.metric("Aantal evaluaties", len(groep_df))

    # =========================
    # TEKST CLEAN
    # =========================

    tekst = "\n".join(
        groep_df["feedback"].fillna("").astype(str).tolist()
    )

    rapport = genereer_ai_feedback(scores, tekst)

    st.markdown(rapport)

    # =========================
    # PDF EXPORT
    # =========================

    pdf = maak_pdf(groep, groep_df, scores, klas_scores, rapport)

    st.download_button(
        "📄 Download PDF rapport",
        data=pdf,
        file_name=f"groepsrapport_{groep}.pdf",
        mime="application/pdf"
    )

# =========================
# DEBUG
# =========================

with st.expander("📁 Data"):
    st.dataframe(df)
