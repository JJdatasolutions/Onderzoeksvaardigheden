import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import io
from collections import Counter
from wordcloud import WordCloud

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
# MAX 3 SELECTIE
# =========================

def checkbox_limited(options, prefix):
    selected = []
    cols = st.columns(3)

    temp = []

    for i, opt in enumerate(options):

        disabled = len(temp) >= 3

        checked = cols[i % 3].checkbox(
            opt,
            key=f"{prefix}_{i}",
            disabled=disabled
        )

        if checked:
            temp.append(opt)

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
# WORDCLOUDS
# =========================

def maak_wordcloud(woorden, kleur):

    if len(woorden) == 0:
        woorden = ["geen data"]

    tekst = " ".join(woorden)

    wc = WordCloud(
        width=800,
        height=400,
        background_color="white",
        colormap=kleur,
        collocations=False
    ).generate(tekst)

    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    buf.seek(0)
    plt.close()

    return buf

# =========================
# ANALYSE
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
# PDF EXPORT
# =========================

def maak_pdf(groep, scores, klas_scores, groep_df):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    labels = ["Presence","Taal","Contact","Visual","Vragen"]

    content = []

    content.append(Paragraph(f"Peer Feedback Rapport - {groep}", styles["Title"]))
    content.append(Spacer(1, 20))

    # RADAR
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    scores_plot = scores + scores[:1]
    klas_plot = klas_scores + klas_scores[:1]

    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))

    ax.plot(angles, klas_plot, linestyle="dashed", label="Klas")
    ax.plot(angles, scores_plot, label="Groep")
    ax.fill(angles, scores_plot, alpha=0.3)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 7)
    ax.legend()

    img = io.BytesIO()
    plt.savefig(img, format="png", dpi=200, bbox_inches="tight")
    img.seek(0)
    plt.close()

    content.append(Image(img, width=400, height=400))
    content.append(Spacer(1, 15))

    # WORDCLOUDS
    top_pos, top_neg = analyseer_groep(groep_df)

    pos_img = maak_wordcloud(top_pos, "Greens")
    neg_img = maak_wordcloud(top_neg, "Reds")

    content.append(Paragraph("POSITIEVE FEEDBACK", styles["Heading2"]))
    content.append(Image(pos_img, width=300, height=150))
    content.append(Spacer(1, 10))

    content.append(Paragraph("WERKPUNTEN", styles["Heading2"]))
    content.append(Image(neg_img, width=300, height=150))

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

    st.plotly_chart(
        radar(scores, klas_scores, ["Presence","Taal","Contact","Visual","Vragen"]),
        use_container_width=True
    )

    pdf = maak_pdf(groep, scores, klas_scores, groep_df)

    st.download_button(
        "Download PDF",
        data=pdf,
        file_name=f"rapport_{groep}.pdf",
        mime="application/pdf"
    )
