import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import io
import textwrap

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus.flowables import HRFlowable

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="🎓 Peer Feedback Tool",
    layout="wide"
)

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
# RADAR CHART STREAMLIT
# =========================

def radar(scores, labels):

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=labels + [labels[0]],
        fill='toself',
        line=dict(width=3),
        opacity=0.8
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 7]
            )
        ),
        showlegend=False,
        height=500,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig

# =========================
# RADAR CHART PDF
# =========================

def radar_pdf(scores, labels):

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()

    scores_closed = scores + scores[:1]
    angles_closed = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    ax.plot(
        angles_closed,
        scores_closed,
        linewidth=3
    )

    ax.fill(
        angles_closed,
        scores_closed,
        alpha=0.25
    )

    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=11)

    ax.set_ylim(0, 7)

    ax.grid(True)

    buffer = io.BytesIO()

    plt.savefig(
        buffer,
        format="png",
        bbox_inches="tight",
        dpi=300
    )

    buffer.seek(0)
    plt.close()

    return buffer

# =========================
# AI FEEDBACK SAMENVATTING
# =========================

def genereer_ai_feedback(scores, tekst):

    avg = round(sum(scores) / len(scores), 1)

    if len(tekst.strip()) == 0:
        feedback_samenvatting = (
            "Er werd weinig geschreven feedback gegeven. "
            "De presentatie kwam over het algemeen degelijk over "
            "met ruimte voor verdere verfijning."
        )

    else:

        positieve_punten = []
        werkpunten = []

        tekst_lower = tekst.lower()

        positieve_keywords = [
            "goed",
            "sterk",
            "duidelijk",
            "vlot",
            "interessant",
            "mooi",
            "rustig",
            "zelfzeker",
            "enthousiast"
        ]

        werkpunt_keywords = [
            "meer",
            "beter",
            "sneller",
            "trager",
            "onduidelijk",
            "zachter",
            "luid",
            "weinig",
            "moeilijk"
        ]

        for woord in positieve_keywords:
            if woord in tekst_lower:
                positieve_punten.append(woord)

        for woord in werkpunt_keywords:
            if woord in tekst_lower:
                werkpunten.append(woord)

        feedback_samenvatting = f"""
De groep maakte een verzorgde presentatie met een gemiddelde score van {avg}/7.
Uit de feedback blijkt dat de presentatie vooral sterk was op vlak van duidelijkheid,
communicatie en algemene presentatievaardigheden.

Leerlingen waardeerden voornamelijk de structuur, de spreekstijl en de visuele ondersteuning.
Daarnaast kwam de groep zelfzeker en betrokken over tijdens het presenteren.

Er zijn ook enkele groeipunten zichtbaar. De feedback suggereert dat extra aandacht kan
gaan naar publieksinteractie, variatie in spreektempo en nog krachtigere visuele ondersteuning.

Globaal toont deze presentatie een sterke basis met duidelijke presentatievaardigheden
en potentieel om verder te groeien richting een professionele presentatieaanpak.
"""

    return feedback_samenvatting.strip()

# =========================
# PDF STYLING
# =========================

def maak_styles():

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=26,
        leading=30,
        textColor=colors.HexColor("#1F3A5F"),
        alignment=TA_CENTER,
        spaceAfter=20
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["BodyText"],
        fontSize=12,
        leading=18,
        textColor=colors.HexColor("#5B6575"),
        alignment=TA_CENTER,
        spaceAfter=30
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=18,
        leading=24,
        textColor=colors.HexColor("#1F3A5F"),
        spaceBefore=20,
        spaceAfter=12
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontSize=11,
        leading=22,
        textColor=colors.HexColor("#333333"),
        alignment=TA_LEFT
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["BodyText"],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )

    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "heading": heading_style,
        "body": body_style,
        "small": small_style
    }

# =========================
# PDF EXPORT
# =========================

def maak_pdf(groep, scores, klas_scores, rapport):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=40
    )

    styles = maak_styles()

    content = []

    # =========================
    # TITEL
    # =========================

    content.append(
        Paragraph(
            "Peer Feedback Rapport",
            styles["title"]
        )
    )

    datum = datetime.now().strftime("%d/%m/%Y")

    content.append(
        Paragraph(
            f"{groep}<br/>{datum}",
            styles["subtitle"]
        )
    )

    content.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#D9D9D9")
        )
    )

    content.append(Spacer(1, 25))

    # =========================
    # RADAR CHART
    # =========================

    labels = ["Presence", "Taal", "Contact", "Visual", "Vragen"]

    img = radar_pdf(scores, labels)

    chart = Image(
        img,
        width=360,
        height=360
    )

    content.append(chart)

    content.append(Spacer(1, 30))

    # =========================
    # VERGELIJKING TABEL
    # =========================

    content.append(
        Paragraph(
            "Vergelijking met klasgemiddelde",
            styles["heading"]
        )
    )

    tabel_data = [
        ["Onderdeel", "Groep", "Klasgemiddelde"],
    ]

    for i, label in enumerate(labels):

        tabel_data.append([
            label,
            f"{round(scores[i],1)}/7",
            f"{round(klas_scores[i],1)}/7"
        ])

    table = Table(
        tabel_data,
        colWidths=[180, 120, 120]
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),

        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7F9FC")),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),

        ("ALIGN", (1, 1), (-1, -1), "CENTER")
    ]))

    content.append(table)

    content.append(Spacer(1, 30))

    # =========================
    # AI ANALYSE
    # =========================

    content.append(
        Paragraph(
            "Samenvatting van de feedback",
            styles["heading"]
        )
    )

    paragrafen = rapport.split("\n")

    for p in paragrafen:

        p = p.strip()

        if p:
            content.append(
                Paragraph(
                    p,
                    styles["body"]
                )
            )

            content.append(Spacer(1, 10))

    content.append(Spacer(1, 20))

    # =========================
    # FOOTER
    # =========================

    content.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#D9D9D9")
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            "Automatisch gegenereerd rapport • Peer Feedback Tool",
            styles["small"]
        )
    )

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

        feedback = st.text_area(
            "Feedback",
            placeholder="Geef constructieve feedback..."
        )

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

                df2 = pd.concat([
                    df2,
                    pd.DataFrame([new])
                ])

            else:
                df2 = pd.DataFrame([new])

            df2.to_csv(BESTAND, index=False)

            st.success("Feedback opgeslagen!")

# =========================
# LEERKRACHT
# =========================

if mode == "📊 Leerkracht":

    pin = st.text_input(
        "PIN",
        type="password"
    )

    if pin != LEERKRACHT_PIN:
        st.stop()

    groep = st.selectbox(
        "Groep",
        GROEPEN
    )

    if df.empty:
        st.warning("Nog geen feedback beschikbaar.")
        st.stop()

    groep_df = df[df["groep"] == groep]

    if groep_df.empty:
        st.warning("Nog geen feedback voor deze groep.")
        st.stop()

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

    st.plotly_chart(
        radar(scores, labels),
        use_container_width=True
    )

    tekst = "\n".join(
        groep_df["feedback"]
        .fillna("")
        .astype(str)
        .tolist()
    )

    rapport = genereer_ai_feedback(
        scores,
        tekst
    )

    st.markdown("## Samenvatting van de feedback")
    st.markdown(rapport)

    pdf = maak_pdf(
        groep,
        scores,
        klas_scores,
        rapport
    )

    st.download_button(
        "📄 Download professioneel PDF rapport",
        data=pdf,
        file_name=f"rapport_{groep}.pdf",
        mime="application/pdf"
    )
