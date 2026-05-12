# Verbeterde Streamlit Peer Feedback Tool

```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# =========================
# CONFIGURATIE
# =========================

st.set_page_config(
    page_title="🎓 Peer Feedback Tool",
    page_icon="🎓",
    layout="wide"
)

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

HULPZINNEN = [
    "-- Kies een hulpzin --",
    "Ik vond de presentatie sterk omdat...",
    "Je gebruikte de visual erg goed toen je...",
    "Een tip voor de volgende keer is om...",
    "Je taalgebruik was erg rijk, vooral het woord...",
    "Ik kon je goed verstaan omdat..."
]

BESTAND_NAAM = "peer_feedback.csv"

# =========================
# AI-ACHTIGE SAMENVATTING
# =========================

def genereer_ai_feedback(scores, feedbacktekst):
    gemiddelde = round(sum(scores) / len(scores), 1)

    sterke_punten = []
    werkpunten = []

    if scores[0] >= 6:
        sterke_punten.append("een zeer sterke en zelfzekere presence")
    elif scores[0] <= 3:
        werkpunten.append("meer rust en zelfvertrouwen uitstralen")

    if scores[1] >= 6:
        sterke_punten.append("rijk en verzorgd taalgebruik")
    elif scores[1] <= 3:
        werkpunten.append("meer variatie in taalgebruik gebruiken")

    if scores[2] >= 6:
        sterke_punten.append("sterk contact met het publiek")
    elif scores[2] <= 3:
        werkpunten.append("meer oogcontact maken met het publiek")

    if scores[3] >= 6:
        sterke_punten.append("een duidelijke en ondersteunende visual")
    elif scores[3] <= 3:
        werkpunten.append("de visual overzichtelijker maken")

    if scores[4] >= 6:
        sterke_punten.append("sterke antwoorden op vragen")
    elif scores[4] in [1, 2, 3]:
        werkpunten.append("vragen duidelijker beantwoorden")

    if not sterke_punten:
        sterke_punten.append("een degelijke algemene presentatie")

    if not werkpunten:
        werkpunten.append("verder blijven groeien in presentatievaardigheden")

    rapport = f"""
### 🤖 Automatisch Feedbackrapport

**Algemene indruk:**
Deze presentatie behaalde een gemiddelde score van **{gemiddelde}/7**.

### ⭐ Sterke punten
- {'. '.join(sterke_punten)}.

### 📈 Werkpunten
- {'. '.join(werkpunten)}.

### 💬 Opmerking van medeleerlingen
_{feedbacktekst}_

### 🚀 Groeitip
Blijf inzetten op duidelijke communicatie, rustige presentatievaardigheden en actieve betrokkenheid van het publiek.
"""

    return rapport

# =========================
# OPSLAAN VAN FEEDBACK
# =========================

def sla_feedback_op(data):
    df_nieuw = pd.DataFrame([data])

    if os.path.exists(BESTAND_NAAM):
        df_bestaand = pd.read_csv(BESTAND_NAAM)
        df = pd.concat([df_bestaand, df_nieuw], ignore_index=True)
    else:
        df = df_nieuw

    df.to_csv(BESTAND_NAAM, index=False)

# =========================
# VISUALISATIE
# =========================

def create_modern_radar(scores, categories):

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Score',
        line=dict(width=4),
        marker=dict(size=10)
    ))

    fig.update_layout(
        template="plotly_dark",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 7],
                tickvals=[1,2,3,4,5,6,7],
                gridcolor="rgba(255,255,255,0.2)"
            )
        ),
        showlegend=False,
        height=500,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig

# =========================
# TITEL
# =========================

st.title("🎓 Peer Evaluatie Onderzoeksvaardigheden")
st.markdown("Geef eerlijke, constructieve en concrete feedback aan je medeleerlingen.")

# =========================
# SELECTIE GROEP
# =========================

gekozen_groep = st.selectbox(
    "Welke groep evalueer je?",
    ["-- Selecteer groep --"] + GROEPEN
)

# =========================
# FORMULIER
# =========================

if gekozen_groep != "-- Selecteer groep --":

    with st.form("feedback_form"):

        st.subheader(f"📋 Evaluatie voor: {gekozen_groep}")

        st.markdown("---")

        col1, col2 = st.columns(2)

        # -----------------
        # PRESENCE
        # -----------------

        with col1:
            st.markdown("### 🎤 Presence / Houding")
            st.caption("Hoe sterk en zelfzeker kwam de groep over?")

            score_presence = st.slider(
                "Score Presence",
                1,
                7,
                5
            )

            if score_presence == 7:
                st.success("🌟 Deze groep werd beschouwd als enorm sterk qua presence.")
            elif score_presence >= 5:
                st.info("👍 De groep kwam zelfzeker en rustig over.")

            st.markdown("---")

            # -----------------
            # TAAL
            # -----------------

            st.markdown("### 🗣️ Rijke Taal")
            st.caption("Hoe verzorgd en rijk was het taalgebruik?")

            score_taal = st.slider(
                "Score Taal",
                1,
                7,
                5
            )

            if score_taal == 7:
                st.success("📚 Het taalgebruik werd als uitzonderlijk sterk ervaren.")

            st.markdown("---")

            # -----------------
            # CONTACT
            # -----------------

            st.markdown("### 👀 Publiekscontact")
            st.caption("Hoe goed maakte de groep contact met het publiek?")

            score_contact = st.slider(
                "Score Publiekscontact",
                1,
                7,
                5
            )

            if score_contact == 7:
                st.success("👏 Het contact met het publiek was uitzonderlijk sterk.")

        with col2:

            # -----------------
            # VISUAL
            # -----------------

            st.markdown("### 🖼️ Kwaliteit van de Visual")
            st.caption("Hoe goed ondersteunde de visual de presentatie?")

            score_visual = st.slider(
                "Score Visual",
                1,
                7,
                5
            )

            if score_visual == 7:
                st.success("🎨 De visual werd als bijzonder sterk ervaren.")

            st.markdown("---")

            # -----------------
            # VRAGEN
            # -----------------

            st.markdown("### ❓ Beantwoorden van vragen")
            st.caption("Hoe sterk werden vragen beantwoord?")

            score_vragen = st.slider(
                "Score Vragen",
                0,
                7,
                5,
                help="Gebruik 0 indien er geen vragen gesteld werden."
            )

            if score_vragen == 7:
                st.success("💡 De antwoorden op vragen waren bijzonder sterk.")

        # =========================
        # WOORDELIJKE FEEDBACK
        # =========================

        st.markdown("---")
        st.subheader("✍️ Woordelijke Feedback")

        hulpzin = st.selectbox(
            "Kies een hulpzin",
            HULPZINNEN
        )

        feedback = st.text_area(
            "Geef concrete feedback",
            placeholder="Bijvoorbeeld: Jullie maakten sterk oogcontact en de visual hielp om alles duidelijk te begrijpen.",
            height=150
        )

        if hulpzin != HULPZINNEN[0]:
            volledige_feedback = f"{hulpzin} {feedback}"
        else:
            volledige_feedback = feedback

        # =========================
        # VERZENDEN
        # =========================

        submit = st.form_submit_button("📨 Feedback Verzenden")

        if submit:

            if len(feedback.strip()) < 15:
                st.error("⚠️ Geef wat uitgebreidere feedback (minstens 15 tekens).")

            else:

                data = {
                    "tijdstip": datetime.now(),
                    "groep": gekozen_groep,
                    "presence": score_presence,
                    "taal": score_taal,
                    "contact": score_contact,
                    "visual": score_visual,
                    "vragen": score_vragen,
                    "feedback": volledige_feedback
                }

                sla_feedback_op(data)

                st.success(f"✅ Je feedback voor {gekozen_groep} werd opgeslagen!")

                st.markdown("---")
                st.subheader("📊 Overzicht van jouw evaluatie")

                scores = [
                    score_presence,
                    score_taal,
                    score_contact,
                    score_visual,
                    score_vragen
                ]

                labels = [
                    "Presence",
                    "Taal",
                    "Contact",
                    "Visual",
                    "Vragen"
                ]

                fig = create_modern_radar(scores, labels)
                st.plotly_chart(fig, use_container_width=True)

                # Mooie statistiek-kaartjes
                gemiddelde = round(sum(scores) / len(scores), 1)

                stat1, stat2, stat3 = st.columns(3)

                stat1.metric("Gemiddelde", f"{gemiddelde}/7")
                stat2.metric("Hoogste score", max(scores))
                stat3.metric("Aantal criteria", len(scores))

                st.markdown("---")

                st.markdown(genereer_ai_feedback(scores, volledige_feedback))

# =========================
# EXTRA INFO
# =========================

with st.expander("ℹ️ Over deze tool"):
    st.write("""
    Deze tool helpt leerlingen om:

    - constructieve peerfeedback te geven,
    - concreter te formuleren,
    - presentatievaardigheden te evalueren,
    - en automatisch feedbackrapporten te genereren.
    """)

```

# Wat werd verbeterd?

## ✅ Punt 1 toegevoegd: slechte feedback blokkeren

De app controleert nu:

* minimum 15 tekens,
* dus geen "goed gedaan" meer,
* leerlingen moeten concreter schrijven.

---

## ✅ Punt 4 toegevoegd: AI-achtig feedbackrapport

Na indienen krijgt de leerling automatisch:

* sterke punten,
* werkpunten,
* samenvatting,
* groeitip.

---

## ✅ Mooiere visualisatie

De radar chart werd:

* moderner,
* interactiever,
* visueel aantrekkelijker,
* donker thema,
* dikkere lijnen,
* professionelere layout.

---

## ✅ Nieuwe schaal op 7

Alle sliders:

* gaan nu van 1 tot 7,
* behalve vragen (0–7 wegens NVT).

---

## ✅ Slimme feedback bij topscores

Bij 7/7 verschijnt automatisch een positieve standaardzin.

Bijvoorbeeld:

> 🌟 Deze groep werd beschouwd als enorm sterk qua presence.

Dat versterkt de interpretatie van de score.

---

## ✅ Feedback wordt opgeslagen

Alle evaluaties worden nu automatisch bewaard in:

```python
peer_feedback.csv
```

Daardoor kun je later:

* gemiddelden berekenen,
* rapporten exporteren,
* dashboards bouwen,
* analyses maken.
