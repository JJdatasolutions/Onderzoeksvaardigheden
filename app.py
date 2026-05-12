import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="🎓 Peer Feedback Tool", layout="wide")

BESTAND = "peer_feedback.csv"

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
# DATA LADEN
# =========================

def load_data():
    if os.path.exists(BESTAND):
        return pd.read_csv(BESTAND)
    return pd.DataFrame()

df = load_data()

# =========================
# RADAR CHART
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
        showlegend=False
    )

    return fig

# =========================
# AI FEEDBACK (optioneel OpenAI)
# =========================

def ai_feedback(text, avg):
    try:
        import openai

        openai.api_key = st.secrets["OPENAI_API_KEY"]

        prompt = f"""
Je bent een leerkracht onderzoeksvaardigheden.

Maak een professioneel maar begrijpelijk feedbackrapport voor leerlingen.

Gemiddelde score: {avg}/7

Feedback:
{text}

Geef:
- sterke punten
- werkpunten
- korte samenvatting
- 1 concrete groeitip
"""

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response["choices"][0]["message"]["content"]

    except:
        return f"""
## Automatisch feedbackrapport

**Samenvatting**
De groep behaalde een gemiddelde score van {avg}/7.

**Feedback (samenvatting van leerlingen):**
{text}

**Werkpunt:**
Blijf werken aan duidelijkheid, structuur en publiekscontact.

**Sterkte:**
De presentatie toont een goed begrip van het onderwerp.
"""

# =========================
# PDF GENERATOR
# =========================

def create_pdf(groep, rapport):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph(f"<b>Groepsrapport: {groep}</b>", styles["Title"]))
    content.append(Spacer(1, 12))

    for line in rapport.split("\n"):
        content.append(Paragraph(line, styles["BodyText"]))
        content.append(Spacer(1, 6))

    doc.build(content)
    buffer.seek(0)

    return buffer

# =========================
# UI
# =========================

st.title("🎓 Peer Feedback + Groepsrapport Generator")

# =========================
# GROEP SELECTIE
# =========================

groep = st.selectbox("Selecteer groep", ["-- kies --"] + GROEPEN)

if groep != "-- kies --":

    if df.empty:
        st.warning("Nog geen data beschikbaar.")
    else:

        groep_df = df[df["groep"] == groep]

        if groep_df.empty:
            st.warning("Geen feedback voor deze groep.")
        else:

            st.subheader(f"📊 Rapport voor {groep}")

            # =========================
            # GEMIDDELDEN
            # =========================

            cols = ["presence", "taal", "contact", "visual", "vragen"]
            gemiddelden = groep_df[cols].replace(0, pd.NA).mean().fillna(0).tolist()

            labels = ["Presence", "Taal", "Contact", "Visual", "Vragen"]

            st.plotly_chart(radar(gemiddelden, labels), use_container_width=True)

            avg = round(sum(gemiddelden) / len(gemiddelden), 1)

            st.metric("Gemiddelde score", f"{avg}/7")
            st.metric("Aantal evaluaties", len(groep_df))

            # =========================
            # TEKST FEEDBACK SAMENVOEGEN
            # =========================

            tekst = "\n".join(groep_df["feedback"].astype(str).tolist())

            # =========================
            # AI RAPPORT
            # =========================

            rapport = ai_feedback(tekst, avg)

            st.markdown("## 🤖 AI Groepsrapport")
            st.markdown(rapport)

            # =========================
            # PDF EXPORT
            # =========================

            pdf = create_pdf(groep, rapport)

            st.download_button(
                "📄 Download PDF rapport",
                data=pdf,
                file_name=f"rapport_{groep}.pdf",
                mime="application/pdf"
            )

# =========================
# DEBUG DATA VIEW
# =========================

with st.expander("📁 Alle data"):
    st.dataframe(df)
