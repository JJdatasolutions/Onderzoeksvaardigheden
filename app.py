import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
import os
import io
from collections import Counter, defaultdict
from wordcloud import WordCloud
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="🎓 AI Feedback Dashboard", layout="wide")

BESTAND = "peer_feedback.csv"

# =========================
# DATA
# =========================

def load_data():
    if os.path.exists(BESTAND):
        return pd.read_csv(BESTAND)
    return pd.DataFrame()

df = load_data()

# =========================
# THEMA CLUSTERING (KEY UPGRADE)
# =========================

THEMAS = {
    "structuur": ["structuur", "opbouw", "logisch", "volgorde"],
    "presentatie": ["presentatie", "spreken", "stem", "duidelijk"],
    "interactie": ["publiek", "oogcontact", "vragen", "betrokken"],
    "voorbereiding": ["voorbereiding", "geoefend", "kennis"],
    "tempo": ["snel", "traag", "timing", "tijd"],
    "samenwerking": ["samenwerking", "team", "groep"]
}

def cluster_themas(woorden):
    clusters = defaultdict(int)

    for w in woorden:
        wl = w.lower()

        matched = False
        for thema, keywords in THEMAS.items():
            if any(k in wl for k in keywords):
                clusters[thema] += 1
                matched = True
                break

        if not matched:
            clusters["overig"] += 1

    return clusters

# =========================
# WORDCLOUD (IMPROVED)
# =========================

def maak_wordcloud(woorden, kleur):

    if len(woorden) == 0:
        woorden = ["geen_feedback"]

    freq = Counter(woorden)

    wc = WordCloud(
        width=900,
        height=450,
        background_color="white",
        colormap=kleur,
        collocations=False,
        prefer_horizontal=1.0
    ).generate_from_frequencies(freq)

    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    buf.seek(0)
    plt.close()

    return buf

# =========================
# AI-STYLE ANALYSE (NO API)
# =========================

def slimme_analyse(positief, werkpunt, scores):

    pos_clusters = cluster_themas(positief)
    neg_clusters = cluster_themas(werkpunt)

    top_pos = sorted(pos_clusters.items(), key=lambda x: x[1], reverse=True)
    top_neg = sorted(neg_clusters.items(), key=lambda x: x[1], reverse=True)

    avg = round(sum(scores)/len(scores),1)

    tekst = f"""
De groep behaalt een gemiddelde score van {avg}/7.

Sterke punten situeren zich vooral in {top_pos[0][0] if top_pos else "geen duidelijke thema's"}.

Werkpunten liggen voornamelijk bij {top_neg[0][0] if top_neg else "geen duidelijke thema's"}.

De feedback toont een duidelijk beeld van de klasdynamiek. Er is een sterke basis aanwezig, maar vooral rond {top_neg[0][0] if top_neg else "verschillende aspecten"} is nog groeimarge.

Aanbevolen focus: verbeter {top_neg[0][0] if top_neg else "algemene structuur en communicatie"} in volgende presentaties.
"""

    return tekst, pos_clusters, neg_clusters

# =========================
# PDF
# =========================

def maak_pdf(groep, scores, klas_scores, positief, werkpunt):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph(f"AI Feedback Rapport - {groep}", styles["Title"]))
    content.append(Spacer(1, 20))

    analyse, pos_c, neg_c = slimme_analyse(positief, werkpunt, scores)

    # radar + wordcloud visuals
    labels = ["Presence","Taal","Contact","Visual","Vragen"]

    content.append(Paragraph("Analyse", styles["Heading2"]))
    content.append(Paragraph(analyse, styles["BodyText"]))
    content.append(Spacer(1, 15))

    pos_img = maak_wordcloud(positief, "Greens")
    neg_img = maak_wordcloud(werkpunt, "Reds")

    content.append(Paragraph("Positieve feedback", styles["Heading2"]))
    content.append(Image(pos_img, width=300, height=150))
    content.append(Spacer(1, 10))

    content.append(Paragraph("Werkpunten", styles["Heading2"]))
    content.append(Image(neg_img, width=300, height=150))

    doc.build(content)
    buffer.seek(0)

    return buffer

# =========================
# UI DEMO (MINIMAL FOR CORE LOGIC)
# =========================

st.title("🎓 AI Feedback Engine (Upgrade)")

groep = st.text_input("Groep")

if st.button("Genereer analyse"):

    if len(df) == 0:
        st.warning("Geen data")
        st.stop()

    groep_df = df[df["groep"] == groep]

    positief = []
    werkpunt = []

    for c in ["positief_1","positief_2","positief_3"]:
        positief += groep_df[c].dropna().tolist()

    for c in ["werkpunt_1","werkpunt_2","werkpunt_3"]:
        werkpunt += groep_df[c].dropna().tolist()

    scores = [
        groep_df["presence"].mean(),
        groep_df["taal"].mean(),
        groep_df["contact"].mean(),
        groep_df["visual"].mean(),
        groep_df["vragen"].mean()
    ]

    st.write(slimme_analyse(positief, werkpunt, scores)[0])

    pdf = maak_pdf(groep, scores, scores, positief, werkpunt)

    st.download_button(
        "Download AI rapport",
        data=pdf,
        file_name=f"rapport_{groep}.pdf",
        mime="application/pdf"
    )
