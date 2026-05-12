import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="🎓 Peer Feedback Tool", layout="wide")

BESTAND = "peer_feedback.csv"

LEERKRACHT_PIN = "1234"  # 🔐 verander dit naar jouw geheime code

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
        showlegend=False,
        height=500
    )

    return fig

# =========================
# AI FEEDBACK (fallback + simpel)
# =========================

def genereer_ai_feedback(scores, tekst):

    avg = round(sum(scores) / len(scores), 1)

    sterke = []
    werk = []

    if scores[0] >= 6:
        sterke.append("sterke presence en zelfvertrouwen")
    elif scores[0] <= 3:
        werk.append("meer zelfvertrouwen tonen")

    if scores[1] >= 6:
        sterke.append("rijk taalgebruik")
    elif scores[1] <= 3:
        werk.append("taalgebruik uitbreiden")

    if scores[2] >= 6:
        sterke.append("goed publiekscontact")
    elif scores[2] <= 3:
        werk.append("meer oogcontact maken")

    if scores[3] >= 6:
        sterke.append("sterke visual ondersteuning")
    elif scores[3] <= 3:
        werk.append("visual duidelijker maken")

    if scores[4] >= 6:
        sterke.append("goede antwoorden op vragen")

    return f"""
## 🤖 Groepsrapport

**Gemiddelde score:** {avg}/7

### ⭐ Sterktes
- {", ".join(sterke) if sterke else "algemene degelijke presentatie"}

### 📈 Werkpunten
- {", ".join(werk) if werk else "blijven groeien in presentatievaardigheden"}

### 💬 Leerlingenfeedback
{tekst}

### 🚀 Advies
Blijf werken aan duidelijkheid, structuur en publiekcontact.
"""

# =========================
# UI
# =========================

st.title("🎓 Peer Feedback Tool")

mode = st.radio(
    "Kies modus",
    ["✍️ Leerlingen: feedback geven", "📊 Leerkracht: groepsrapport"]
)

# =========================
# LEERLINGEN MODE
# =========================

if mode == "✍️ Leerlingen: feedback geven":

    groep = st.selectbox("Selecteer groep", GROEPEN)

    with st.form("feedback_form"):

        st.subheader(f"Evaluatie: {groep}")

        presence = st.slider("Presence (1 = onzeker, 7 = zeer zelfzeker)", 1, 7, 5)
        taal = st.slider("Rijke taal", 1, 7, 5)
        contact = st.slider("Publiekscontact", 1, 7, 5)
        visual = st.slider("Visual ondersteuning", 1, 7, 5)
        vragen = st.slider("Vragen (0 = niet van toepassing)", 0, 7, 5)

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
# LEERKRACHT MODE
# =========================

if mode == "📊 Leerkracht: groepsrapport":

    pin = st.text_input("Voer leerkracht-PIN in", type="password")

    if pin != LEERKRACHT_PIN:
        st.warning("Geen toegang.")
        st.stop()

    st.success("Toegang verleend")

    groep = st.selectbox("Selecteer groep", GROEPEN)

    if df.empty:
        st.warning("Nog geen data beschikbaar.")
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

    labels = ["Presence", "Taal", "Contact", "Visual", "Vragen"]

    st.subheader(f"📊 Rapport: {groep}")

    st.plotly_chart(radar(scores, labels), use_container_width=True)

    st.metric("Gemiddelde score", round(sum(scores)/len(scores), 1))
    st.metric("Aantal evaluaties", len(groep_df))

    # =========================
    # TEKST SAMENVOEGEN
    # =========================

    tekst = "\n".join(groep_df["feedback"].astype(str).tolist())

    st.markdown(genereer_ai_feedback(scores, tekst))

# =========================
# DEBUG
# =========================

with st.expander("📁 Data bekijken"):
    st.dataframe(df)
