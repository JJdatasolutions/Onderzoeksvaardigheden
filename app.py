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
# VERBETERDE AI ANALYSE
# =========================

def genereer_ai_feedback(scores, tekst):

    avg = round(sum(scores) / len(scores), 1)

    tekst_lower = tekst.lower()

    positieve_zinnen = []
    verbeter_zinnen = []

    # POSITIEVE ANALYSE

    if any(w in tekst_lower for w in ["duidelijk", "helder", "structuur"]):
        positieve_zinnen.append(
            "De presentatie werd als duidelijk en goed gestructureerd ervaren."
        )

    if any(w in tekst_lower for w in ["zelfzeker", "rustig", "vlot"]):
        positieve_zinnen.append(
            "De groep kwam zelfzeker en vlot over tijdens het presenteren."
        )

    if any(w in tekst_lower for w in ["mooi", "visual", "slides", "afbeelding"]):
        positieve_zinnen.append(
            "De visuele ondersteuning droeg positief bij aan de presentatie."
        )

    if any(w in tekst_lower for w in ["interessant", "boeiend", "enthousiast"]):
        positieve_zinnen.append(
            "Het publiek bleef betrokken dankzij een enthousiaste presentatieaanpak."
        )

    # VERBETERPUNTEN

    if any(w in tekst_lower for w in ["zachter", "luider", "volume"]):
        verbeter_zinnen.append(
            "Werk verder aan stemvolume en verstaanbaarheid."
        )

    if any(w in tekst_lower for w in ["sneller", "traag", "tempo"]):
        verbeter_zinnen.append(
            "Meer controle over spreektempo kan de presentatie nog sterker maken."
        )

    if any(w in tekst_lower for w in ["meer", "vragen", "interactie"]):
        verbeter_zinnen.append(
            "Meer interactie met het publiek zou de betrokkenheid verhogen."
        )

    if any(w in tekst_lower for w in ["onduidelijk", "verwarrend"]):
        verbeter_zinnen.append(
            "Sommige onderdelen mogen nog duidelijker uitgewerkt worden."
        )

    # FALLBACKS

    if len(positieve_zinnen) == 0:
        positieve_zinnen.append(
            "De groep bracht een verzorgde en degelijke presentatie."
        )

    if len(verbeter_zinnen) == 0:
        verbeter_zinnen.append(
            "De presentatie heeft een sterke basis en kan verder verfijnd worden."
        )

    return {
        "gemiddelde": avg,
        "positief": positieve_zinnen,
        "verbeter": verbeter_zinnen
    }

# =========================
# EXTRA DESIGN ELEMENTEN
# =========================

from reportlab.platypus import (
    KeepTogether
)

# =========================
# NIEUWE PDF EXPORT
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

    styles = maak_styles()

    content = []

    labels = ["Presence", "Taal", "Contact", "Visual", "Vragen"]

    # =========================
    # COVER HEADER
    # =========================

    titel_style = ParagraphStyle(
        "Titel",
        parent=styles["title"],
        fontSize=28,
        leading=34,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#16324F")
    )

    groep_style = ParagraphStyle(
        "Groep",
        parent=styles["body"],
        fontSize=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#5B6575"),
        leading=24
    )

    datum = datetime.now().strftime("%d/%m/%Y")

    content.append(Spacer(1, 25))

    content.append(
        Paragraph(
            "Peer Feedback Rapport",
            titel_style
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"{groep}<br/>{datum}",
            groep_style
        )
    )

    content.append(Spacer(1, 30))

    # STRAKKE LIJN

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
        [[f"Gemiddelde score\n{avg}/7"]],
        colWidths=[180],
        rowHeights=[75]
    )

    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#16324F")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 20),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [12, 12, 12, 12]),
    ]))

    content.append(score_table)

    content.append(Spacer(1, 30))

    # =========================
    # RADAR CHART IN CARD
    # =========================

    chart = radar_pdf(scores, labels)

    img = Image(
        chart,
        width=360,
        height=360
    )

    chart_table = Table(
        [[img]],
        colWidths=[470]
    )

    chart_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D9E1EA")),
        ("ROUNDEDCORNERS", [12, 12, 12, 12]),
        ("TOPPADDING", (0, 0), (-1, -1), 15),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
    ]))

    content.append(chart_table)

    content.append(Spacer(1, 30))

    # =========================
    # VERGELIJKINGSTABEL
    # =========================

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["heading"],
        fontSize=18,
        textColor=colors.HexColor("#16324F"),
        spaceAfter=16
    )

    content.append(
        Paragraph(
            "Vergelijking met klasgemiddelde",
            heading_style
        )
    )

    tabel_data = [
        ["Onderdeel", "Groep", "Klas"]
    ]

    for i, label in enumerate(labels):

        tabel_data.append([
            label,
            f"{round(scores[i],1)}/7",
            f"{round(klas_scores[i],1)}/7"
        ])

    vergelijking = Table(
        tabel_data,
        colWidths=[220, 100, 100]
    )

    vergelijking.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16324F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),

        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DCE3EB")),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),

        ("ALIGN", (1, 1), (-1, -1), "CENTER"),

    ]))

    content.append(vergelijking)

    content.append(Spacer(1, 35))

    # =========================
    # FEEDBACK BLOKKEN
    # =========================

    box_title = ParagraphStyle(
        "BoxTitle",
        parent=styles["body"],
        fontSize=15,
        textColor=colors.white,
        leading=18,
        alignment=TA_LEFT
    )

    box_text = ParagraphStyle(
        "BoxText",
        parent=styles["body"],
        fontSize=11,
        leading=20,
        textColor=colors.HexColor("#2B2B2B")
    )

    # GOEDE PUNTEN

    positieve_html = "<br/><br/>".join([
        f"• {punt}" for punt in analyse["positief"]
    ])

    positief_blok = Table(
        [[
            Paragraph(
                "<b>Sterke punten</b>",
                box_title
            )
        ],
        [
            Paragraph(
                positieve_html,
                box_text
            )
        ]],
        colWidths=[470]
    )

    positief_blok.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F6B3B")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F4FBF5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D7E9DA")),
        ("ROUNDEDCORNERS", [12, 12, 12, 12]),

        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

        ("TOPPADDING", (0, 1), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
    ]))

    content.append(positief_blok)

    content.append(Spacer(1, 20))

    # VERBETERPUNTEN

    verbeter_html = "<br/><br/>".join([
        f"• {punt}" for punt in analyse["verbeter"]
    ])

    verbeter_blok = Table(
        [[
            Paragraph(
                "<b>Verbeterpunten</b>",
                box_title
            )
        ],
        [
            Paragraph(
                verbeter_html,
                box_text
            )
        ]],
        colWidths=[470]
    )

    verbeter_blok.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#A14B2A")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFF8F5")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#F0D7CC")),
        ("ROUNDEDCORNERS", [12, 12, 12, 12]),

        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),

        ("TOPPADDING", (0, 1), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
    ]))

    content.append(verbeter_blok)

    content.append(Spacer(1, 35))

    # =========================
    # FOOTER
    # =========================

    footer = ParagraphStyle(
        "Footer",
        parent=styles["body"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.HexColor("#7D8793")
    )

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
            footer
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
