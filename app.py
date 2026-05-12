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

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
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
# MAX 3 SELECTIE UI
# =========================

def checkbox_limited(options, prefix):

    cols = st.columns(3)
    selected = []

    for i, opt in enumerate(options):
        disabled = len(selected) >= 3

        if cols[i % 3].checkbox(opt, key=f"{prefix}_{i}", disabled=disabled):
            selected.append(opt)

    return selected[:3]

# =========================
# RADAR
# =========================

def radar(scores, klas_scores, labels):

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=klas_scores + [klas_scores[0]],
        theta=labels + [labels[0]],
        fill='toself',
        name="Klas"
    ))

    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=labels + [labels[0]],
        fill='toself',
        name="Groep"
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,7])),
        height=500,
        showlegend=True
    )

    return fig

# =========================
# WORDCLOUD FIX (BELANGRIJK)
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
# ANALYSE
# =========================

def analyseer_groep(groep_df):

    positief = []
    werkpunt = []

    for c in ["positief_1","positief_2","positief_3"]:
        positief += groep_df[c].dropna().tolist()

    for c in ["werkpunt_1","werkpunt_2","werkpunt_3"]:
        werkpunt += groep_df[c].dropna().tolist()

    return positief, werkpunt

# =========================
# PDF
# =========================

def maak_pdf(groep, scores, klas_scores, groep_df):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    # =========================
    # CUSTOM STYLES
    # =========================

    title_style = styles["Title"]
    title_style.fontSize = 22
    title_style.spaceAfter = 10

    subtitle_style = styles["Heading2"]
    subtitle_style.textColor = colors.HexColor("#2E4057")

    body = styles["BodyText"]
    body.fontSize = 10
    body.leading = 14

    content = []

    # =========================
    # HEADER
    # =========================

    content.append(Paragraph("🎓 Peer Feedback Rapport", title_style))
    content.append(Paragraph(f"Groep: <b>{groep}</b>", subtitle_style))
    content.append(Paragraph(f"Datum: {datetime.now().strftime('%d/%m/%Y')}", body))

    content.append(Spacer(1, 15))

    # lijn
    content.append(Paragraph("<hr/>", body))
    content.append(Spacer(1, 10))

    # =========================
    # RADAR
    # =========================

    labels = ["Presence","Taal","Contact","Visual","Vragen"]

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    scores_plot = scores + scores[:1]
    klas_plot = klas_scores + klas_scores[:1]

    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))

    ax.plot(angles, klas_plot, linestyle="dashed", label="Klasgemiddelde")
    ax.plot(angles, scores_plot, label="Groep")
    ax.fill(angles, scores_plot, alpha=0.25)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0,7)
    ax.legend(loc="upper right")

    img = io.BytesIO()
    plt.savefig(img, format="png", dpi=200, bbox_inches="tight")
    img.seek(0)
    plt.close()

    content.append(Paragraph("📊 Prestatie-overzicht", subtitle_style))
    content.append(Spacer(1, 10))
    content.append(Image(img, width=420, height=420))

    content.append(Spacer(1, 20))

    # =========================
    # SCORES TABEL (BELANGRIJK DESIGN-IMPROVEMENT)
    # =========================

    data = [["Categorie", "Groep", "Klas"]]
    for i, l in enumerate(labels):
        data.append([l, round(scores[i],1), round(klas_scores[i],1)])

    table = Table(data, colWidths=[200, 80, 80])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2E4057")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 10),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,1), (-1,-1), colors.whitesmoke),
    ]))

    content.append(Paragraph("📈 Scores overzicht", subtitle_style))
    content.append(Spacer(1, 10))
    content.append(table)

    content.append(Spacer(1, 20))

    # =========================
    # WORDCLOUDS
    # =========================

    positief, werkpunt = analyseer_groep(groep_df)

    pos_img = maak_wordcloud(positief, "Greens")
    neg_img = maak_wordcloud(werkpunt, "Reds")

    content.append(Paragraph("👍 Sterke punten", subtitle_style))
    content.append(Image(pos_img, width=300, height=150))

    content.append(Spacer(1, 15))

    content.append(Paragraph("👎 Werkpunten", subtitle_style))
    content.append(Image(neg_img, width=300, height=150))

    # =========================
    # FOOTER NOTE
    # =========================

    content.append(Spacer(1, 20))
    content.append(Paragraph(
        "Dit rapport werd automatisch gegenereerd op basis van peer feedback data.",
        body
    ))

    doc.build(content)
    buffer.seek(0)

    return buffer

# =========================
# UI
# =========================

st.title("🎓 Peer Feedback Tool")

mode = st.radio("Kies modus", ["✍️ Leerlingen", "📊 Leerkracht"])

# =========================
# LEERLINGEN (HERSTELD)
# =========================

if mode == "✍️ Leerlingen":

    groep = st.selectbox("Groep", GROEPEN)

    with st.form("form"):

        presence = st.slider("Presence", 1,7,5)
        taal = st.slider("Taal", 1,7,5)
        contact = st.slider("Contact", 1,7,5)
        visual = st.slider("Visual", 1,7,5)
        vragen = st.slider("Vragen", 1,7,5)

        st.markdown("### 👍 Positief (max 3)")
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
