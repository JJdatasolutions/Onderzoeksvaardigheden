import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import io

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    HRFlowable
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER

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

def radar(scores, klas_scores, labels):

    fig = go.Figure()

    # KLASGEMIDDELDE

    fig.add_trace(go.Scatterpolar(
        r=klas_scores + [klas_scores[0]],
        theta=labels + [labels[0]],
        fill='toself',
        name="Klasgemiddelde",
        opacity=0.25,
        line=dict(width=2)
    ))

    # GROEP

    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=labels + [labels[0]],
        fill='toself',
        name="Groep",
        opacity=0.7,
        line=dict(width=4)
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 7]
            )
        ),
        height=550,
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="center",
            x=0.5
        )
    )

    return fig

# =========================
# RADAR CHART PDF
# =========================

def radar_pdf(scores, klas_scores, labels):

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False
    ).tolist()

    angles += angles[:1]

    scores_closed = scores + scores[:1]
    klas_closed = klas_scores + klas_scores[:1]

    fig, ax = plt.subplots(
        figsize=(6.5, 6.5),
        subplot_kw=dict(polar=True)
    )

    # KLASGEMIDDELDE

    ax.plot(
        angles,
        klas_closed,
        linewidth=2,
        linestyle="dashed",
        label="Klasgemiddelde"
    )

    ax.fill(
        angles,
        klas_closed,
        alpha=0.12
    )

    # GROEP

    ax.plot(
        angles,
        scores_closed,
        linewidth=3,
        label="Groep"
    )

    ax.fill(
        angles,
        scores_closed,
        alpha=0.30
    )

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11)

    ax.set_ylim(0, 7)

    ax.grid(True)

    ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.2, 1.1)
    )

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
# AI ANALYSE
# =========================

def genereer_ai_feedback(scores, tekst):

    avg = round(sum(scores) / len(scores), 1)

    tekst_lower = tekst.lower()

    positieve_punten = []
    verbeterpunten = []

    # POSITIEVE ANALYSE

    if any(w in tekst_lower for w in [
        "duidelijk",
        "helder",
        "structuur"
    ]):

        positieve_punten.append(
            "De presentatie werd als duidelijk en goed gestructureerd ervaren."
        )

    if any(w in tekst_lower for w in [
        "zelfzeker",
        "vlot",
        "rustig"
    ]):

        positieve_punten.append(
            "De groep kwam zelfzeker en professioneel over tijdens het presenteren."
        )

    if any(w in tekst_lower for w in [
        "interessant",
        "boeiend",
        "enthousiast"
    ]):

        positieve_punten.append(
            "Het publiek bleef betrokken dankzij een enthousiaste presentatieaanpak."
        )

    if any(w in tekst_lower for w in [
        "slides",
        "visual",
        "mooi"
    ]):

        positieve_punten.append(
            "De visuele ondersteuning versterkte de inhoud van de presentatie."
        )

    # VERBETERPUNTEN

    if any(w in tekst_lower for w in [
        "tempo",
        "sneller",
        "trager"
    ]):

        verbeterpunten.append(
            "Meer controle over het spreektempo kan de presentatie nog krachtiger maken."
        )

    if any(w in tekst_lower for w in [
        "zachter",
        "luider",
        "volume"
    ]):

        verbeterpunten.append(
            "Extra aandacht voor stemvolume en verstaanbaarheid zou de presentatie verbeteren."
        )

    if any(w in tekst_lower for w in [
        "interactie",
        "vragen",
        "meer"
    ]):

        verbeterpunten.append(
            "Meer interactie met het publiek kan de betrokkenheid nog verhogen."
        )

    if any(w in tekst_lower for w in [
        "onduidelijk",
        "verwarrend"
    ]):

        verbeterpunten.append(
            "Sommige onderdelen mogen nog iets duidelijker uitgewerkt worden."
        )

    # FALLBACKS

    if len(positieve_punten) == 0:

        positieve_punten.append(
            "De groep bracht een verzorgde en degelijke presentatie."
        )

    if len(verbeterpunten) == 0:

        verbeterpunten.append(
            "De presentatie heeft een sterke basis en kan verder verfijnd worden."
        )

    uitgebreide_feedback = f"""
De presentatie behaalde een gemiddelde score van {avg}/7 en maakte in het algemeen een sterke indruk op het publiek. 
Uit de verzamelde feedback blijkt dat de groep erin slaagde om de informatie op een duidelijke en gestructureerde manier over te brengen. 
De presentatie kwam verzorgd over en de groep straalde voldoende zelfvertrouwen uit tijdens het spreken.

Positieve elementen die regelmatig terugkwamen in de feedback waren onder andere de duidelijke uitleg, de rustige presentatiehouding 
en de kwaliteit van de visuele ondersteuning. Verschillende leerlingen gaven aan dat de presentatie aangenaam was om naar te luisteren 
en dat de groep goed voorbereid leek.

Daarnaast zijn er ook enkele groeikansen zichtbaar. Vooral op vlak van interactie met het publiek, spreektempo en dynamiek 
kan nog verdere vooruitgang geboekt worden. Door nog bewuster in te zetten op contact met het publiek en een krachtige spreekstijl 
kan de presentatie nog professioneler en overtuigender worden.

Globaal toont deze presentatie een sterke basis met veel potentieel voor verdere groei.
"""

    return {
        "gemiddelde": avg,
        "positief": positieve_punten,
        "verbeter": verbeterpunten,
        "feedback": uitgebreide_feedback
    }

# =========================
# PDF EXPORT
# =========================

def maak_pdf(groep, scores, klas_scores, analyse):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=40,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    content = []

    labels = [
        "Presence",
        "Taal",
        "Contact",
        "Visual",
        "Vragen"
    ]

    # =========================
    # STYLES
    # =========================

    titel_style = ParagraphStyle(
        "Titel",
        parent=styles["Heading1"],
        fontSize=28,
        leading=34,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#16324F"),
        spaceAfter=10
    )

    groep_style = ParagraphStyle(
        "Groep",
        parent=styles["BodyText"],
        fontSize=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#5B6575"),
        leading=24
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=18,
        textColor=colors.HexColor("#16324F"),
        spaceAfter=16
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=11,
        leading=21,
        textColor=colors.HexColor("#2B2B2B")
    )

    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["BodyText"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.HexColor("#7D8793")
    )

    # =========================
    # HEADER
    # =========================

    datum = datetime.now().strftime("%d/%m/%Y")

    content.append(Spacer(1, 25))

    content.append(
        Paragraph(
            "Peer Feedback Rapport",
            titel_style
        )
    )

    content.append(
        Paragraph(
            f"{groep}<br/>{datum}",
            groep_style
        )
    )

    content.append(Spacer(1, 30))

    content.append(
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=colors.HexColor("#D6DCE5")
        )
    )

    content.append(Spacer(1, 25))

    # =========================
    # SCORE BADGE
    # =========================

    avg = analyse["gemiddelde"]

    score_table = Table(
        [[
            Paragraph(
                f"""
                <para align=center>
                <font size=12>Gemiddelde score</font><br/><br/>
                <font size=26><b>{avg}/7</b></font>
                </para>
                """,
                styles["BodyText"]
            )
        ]],
        colWidths=[190],
        rowHeights=[90]
    )

    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#16324F")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    content.append(score_table)

    content.append(Spacer(1, 30))

    # =========================
    # RADAR CHART
    # =========================

    chart = radar_pdf(
        scores,
        klas_scores,
        labels
    )

    img = Image(
        chart,
        width=390,
        height=390
    )

    chart_table = Table(
        [[img]],
        colWidths=[470]
    )

    chart_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D9E1EA")),
        ("TOPPADDING", (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING", (0, 0), (-1, -1), 18),
        ("RIGHTPADDING", (0, 0), (-1, -1), 18),
    ]))

    content.append(chart_table)

    content.append(Spacer(1, 35))

    # =========================
    # UITGEBREIDE FEEDBACK
    # =========================

    content.append(
        Paragraph(
            "Uitgebreide analyse",
            heading_style
        )
    )

    feedback_box = Table(
        [[
            Paragraph(
                analyse["feedback"],
                body_style
            )
        ]],
        colWidths=[470]
    )

    feedback_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#DCE3EB")),

        ("TOPPADDING", (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),

        ("LEFTPADDING", (0, 0), (-1, -1), 18),
        ("RIGHTPADDING", (0, 0), (-1, -1), 18),
    ]))

    content.append(feedback_box)

    content.append(Spacer(1, 30))

    # =========================
    # STERKE PUNTEN
    # =========================

    content.append(
        Paragraph(
            "Sterke punten",
            heading_style
        )
    )

    positieve_html = "<br/><br/>".join([
        f"• {punt}"
        for punt in analyse["positief"]
    ])

    positieve_box = Table(
        [[
            Paragraph(
                positieve_html,
                body_style
            )
        ]],
        colWidths=[470]
    )

    positieve_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4FBF5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D7E9DA")),

        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),

        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
    ]))

    content.append(positieve_box)

    content.append(Spacer(1, 25))

    # =========================
    # VERBETERPUNTEN
    # =========================

    content.append(
        Paragraph(
            "Verbeterpunten",
            heading_style
        )
    )

    verbeter_html = "<br/><br/>".join([
        f"• {punt}"
        for punt in analyse["verbeter"]
    ])

    verbeter_box = Table(
        [[
            Paragraph(
                verbeter_html,
                body_style
            )
        ]],
        colWidths=[470]
    )

    verbeter_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF8F5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#F0D7CC")),

        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),

        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
    ]))

    content.append(verbeter_box)

    content.append(Spacer(1, 35))

    # =========================
    # FOOTER
    # =========================

    content.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#D9DDE3")
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            "Automatisch gegenereerd rapport • Peer Feedback Tool",
            footer_style
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

    groep = st.selectbox(
        "Groep",
        GROEPEN
    )

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

            df2.to_csv(
                BESTAND,
                index=False
            )

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

        st.warning(
            "Nog geen feedback beschikbaar."
        )

        st.stop()

    groep_df = df[df["groep"] == groep]

    if groep_df.empty:

        st.warning(
            "Nog geen feedback voor deze groep."
        )

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

    labels = [
        "Presence",
        "Taal",
        "Contact",
        "Visual",
        "Vragen"
    ]

    st.plotly_chart(
        radar(scores, klas_scores, labels),
        use_container_width=True
    )

    tekst = "\n".join(
        groep_df["feedback"]
        .fillna("")
        .astype(str)
        .tolist()
    )

    analyse = genereer_ai_feedback(
        scores,
        tekst
    )

    st.markdown("## 📘 Uitgebreide analyse")
    st.markdown(analyse["feedback"])

    st.markdown("## ✅ Sterke punten")

    for punt in analyse["positief"]:
        st.markdown(f"- {punt}")

    st.markdown("## 🚀 Verbeterpunten")

    for punt in analyse["verbeter"]:
        st.markdown(f"- {punt}")

    pdf = maak_pdf(
        groep,
        scores,
        klas_scores,
        analyse
    )

    st.download_button(
        "📄 Download professioneel PDF rapport",
        data=pdf,
        file_name=f"rapport_{groep}.pdf",
        mime="application/pdf"
    )
