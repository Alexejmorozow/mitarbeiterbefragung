# app.py
import streamlit as st
import io
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Flowable
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm, cm

# --------------------------
# Farben (exakt wie ursprüngl.)
# --------------------------
COL_HEX = {
    "mint": "#A8D5BA",
    "dark_mint": "#4A7C59",
    "anthracite": "#2F4F4F",
    "light_gray": "#F8F9FA",
    "white": "#FFFFFF",
    "warning": "#E9B44C",
    "danger": "#D9534F"
}

# --------------------------
# Grunddaten
# --------------------------
PAGE_TITLE = "Mitarbeiterbefragung - Klinisch sauber"
LOGO_PATH = None  # falls du ein PNG-Logo willst, Pfad hierhin setzen

WG_OPTIONS = [
    "Spezialangebot",
    "WG Fliegenpilz",
    "WG Kristall",
    "WG Alphorn",
    "WG Steinbock",
    "WG Alpenblick"
]

DOMAINS = {
    1: "Arbeitsbelastung & Zeitdruck",
    2: "Einarbeitung & Personalentwicklung",
    3: "Zusammenarbeit & Teamklima",
    4: "Führung",
    5: "Gesundheit, körperliche & psychische Belastung",
    6: "Technische & organisatorische Entlastungssysteme",
    7: "Dienst- & Einsatzplanung",
    8: "Kommunikation & Informationsfluss"
}

SUBDOMAINS = {
    1: {1: "Zeit pro Bewohner", 2: "Unterbrechungen", 3: "Arbeitsverdichtung", 4: "Ausfallmanagement"},
    2: {1: "Onboarding-Qualität", 2: "Verfügbarkeit von Ansprechpartnern", 3: "Übergaben & Informationsfluss", 4: "Fort- und Weiterbildung"},
    3: {1: "Zusammenhalt", 2: "Verlässlichkeit", 3: "Rollen & Aufgaben", 4: "Umgang mit Spannungen"},
    4: {1: "Fachliche Führung", 2: "Soziale Führung", 3: "Verfügbarkeit", 4: "Klarheit von Erwartungen"},
    5: {1: "Physische Belastung", 2: "Psychische Erschöpfung", 3: "Pausenrealisierung", 4: "Gesundheitsangebote"},
    6: {1: "Technische Hilfsmittel", 2: "Digitale Dokumentation", 3: "Standardisierte Abläufe", 4: "Verfügbarkeit & Wartung"},
    7: {1: "Planbarkeit", 2: "Fairness", 3: "Umgang mit Ausfällen", 4: "Erholung"},
    8: {1: "Schichtübergaben", 2: "Austausch zwischen Berufsgruppen", 3: "Kommunikation mit Leitung", 4: "Digitale Kanäle"}
}

SCORE_MAP = {
    "Trifft voll zu": 5,
    "Trifft zu": 4,
    "Teils/teils": 3,
    "Trifft nicht zu": 2,
    "Trifft gar nicht zu": 1
}

# --------------------------
# Styles & Footer
# --------------------------
def build_styles(chapter_size=18):
    base = getSampleStyleSheet()
    base.add(ParagraphStyle("TitleCustom", parent=base["Title"],
                            fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=colors.HexColor(COL_HEX["anthracite"])))
    base.add(ParagraphStyle("Chapter", parent=base["Heading1"],
                            fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor(COL_HEX["anthracite"])))
    base.add(ParagraphStyle("Body", parent=base["BodyText"],
                            fontName="Helvetica", fontSize=11, leading=14, textColor=colors.HexColor(COL_HEX["anthracite"])))
    base.add(ParagraphStyle("Muted", parent=base["BodyText"],
                            fontName="Helvetica-Oblique", fontSize=9, leading=11, textColor=colors.HexColor("#666666")))
    return base

def footer(canvas_obj, doc):
    canvas_obj.saveState()
    w, h = A4
    canvas_obj.setFont("Helvetica", 8)
    footer_text = f"Erstellt: {datetime.now().strftime('%d.%m.%Y')}   |   Seite {doc.page}"
    canvas_obj.setFillColor(colors.HexColor(COL_HEX["anthracite"]))
    canvas_obj.drawRightString(w - 20*mm, 12*mm, footer_text)
    canvas_obj.restoreState()

class HRLine(Flowable):
    def __init__(self, width=170*mm, thickness=1):
        super().__init__()
        self.width = width
        self.thickness = thickness
    def draw(self):
        self.canv.setLineWidth(self.thickness)
        self.canv.setStrokeColor(colors.HexColor(COL_HEX["dark_mint"]))
        self.canv.line(0, 0, self.width, 0)

# --------------------------
# Scoring & helpers
# --------------------------
def calculate_scores_from_answers(answers):
    domain_scores = {}
    for (d, sd), resp in answers.items():
        nums = [SCORE_MAP.get(x) for x in resp if SCORE_MAP.get(x) is not None]
        if nums:
            domain_scores.setdefault(d, []).extend(nums)
    avg = {d: (sum(vals)/len(vals)) for d, vals in domain_scores.items()}
    # ensure all domains present
    for d in DOMAINS.keys():
        avg.setdefault(d, 0.0)
    return avg

def interpret_label(score):
    if score >= 4.2:
        return "Sehr gut"
    if score >= 3.6:
        return "Gut"
    if score >= 3.0:
        return "Mittel"
    return "Verbesserungsbedarf"

def pick_color_hex(score):
    if score >= 4.2:
        return "#1E6F5C"
    if score >= 3.6:
        return "#2B8C69"
    if score >= 3.0:
        return "#E9B44C"
    return "#D9534F"

def get_subdomain_avg(answers, d, sd):
    v = answers.get((d, sd))
    if not v:
        return None
    nums = [SCORE_MAP.get(x) for x in v if SCORE_MAP.get(x) is not None]
    return (sum(nums)/len(nums)) if nums else None

# --------------------------
# Charts (nur Balken gewünscht)
# --------------------------
def create_bar_png(domain_scores):
    labels = [DOMAINS[i] for i in range(1, 9)]
    values = [domain_scores.get(i, 0.0) for i in range(1, 9)]
    fig, ax = plt.subplots(figsize=(8, 3))
    bars = ax.barh(range(len(labels)), values, color=COL_HEX["mint"], edgecolor=COL_HEX["dark_mint"])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(0,5)
    ax.invert_yaxis()
    ax.set_xlabel("Score (1–5)")
    ax.grid(axis='x', linestyle=':', linewidth=0.5)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

# --------------------------
# PDF: Titelblatt, Inhaltsverzeichnis, Kapitelüberschriften 18pt, breite Tabellen
# --------------------------
def make_pdf_buffer(wg_name, answers, logo_path=None):
    domain_scores = calculate_scores_from_answers(answers)
    overall = sum(domain_scores.values()) / len(domain_scores) if domain_scores else 0.0

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=20*mm, bottomMargin=22*mm)
    styles = build_styles(chapter_size=18)
    story = []

    # Titelblatt
    if logo_path:
        try:
            story.append(Image(logo_path, width=40*mm, height=40*mm))
            story.append(Spacer(1, 4*mm))
        except Exception:
            pass
    story.append(Paragraph(PAGE_TITLE, styles["TitleCustom"]))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(f"<b>Abteilung:</b> {wg_name}", styles["Body"]))
    story.append(Paragraph(f"<b>Datum:</b> {datetime.now().strftime('%d.%m.%Y')}", styles["Body"]))
    story.append(Spacer(1, 6*mm))
    story.append(HRLine())
    story.append(Spacer(1, 10*mm))

    # Inhaltsverzeichnis (einfacher TOC)
    story.append(Paragraph("Inhaltsverzeichnis", styles["Chapter"]))
    story.append(Spacer(1, 2*mm))
    toc_lines = [
        "1 Executive Summary",
        "2 Profilübersicht (Balken)",
        "3 Detaillierte Bereiche",
        "4 Übersichtstabelle"
    ]
    for line in toc_lines:
        story.append(Paragraph(line, styles["Body"]))
    story.append(PageBreak())

    # Kapitel 1 - Executive Summary
    story.append(Paragraph("1 Executive Summary", styles["Chapter"]))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(f"Gesamtindex: <b>{overall:.2f}</b> (Skala 1..5)", styles["Body"]))
    strengths = [DOMAINS[d] for d, s in domain_scores.items() if s >= 4.2]
    to_improve = [DOMAINS[d] for d, s in domain_scores.items() if s < 3.0]
    if strengths:
        story.append(Paragraph("Stärken: " + ", ".join(strengths), styles["Body"]))
    if to_improve:
        story.append(Paragraph("Entwicklungsbereiche: " + ", ".join(to_improve), styles["Body"]))
    story.append(PageBreak())

    # Kapitel 2 - Profil (Balkendiagramm)
    story.append(Paragraph("2 Profilübersicht (Balken)", styles["Chapter"]))
    story.append(Spacer(1, 4*mm))
    bar_buf = create_bar_png(domain_scores)
    story.append(Image(bar_buf, width=175*mm, height=80*mm))
    story.append(PageBreak())

    # Kapitel 3 - Detaillierte Bereiche (Kapitelüberschriften 18pt)
    for d in range(1, 9):
        story.append(Paragraph(f"3.{d} {DOMAINS[d]}", styles["Chapter"]))
        story.append(Spacer(1, 2*mm))
        s = domain_scores.get(d, 0.0)
        label = interpret_label(s)
        # farbige kleine Box via 1-cell table
        box = Table([[f"{label} — {s:.2f}/5"]], colWidths=[170*mm])
        box.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor(pick_color_hex(s))),
            ("TEXTCOLOR", (0,0), (-1,-1), colors.white),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(box)
        story.append(Spacer(1, 3*mm))

        # Breite Tabelle mit Subdomains (Breitformat)
        sub_rows = [["Thema", "Score"]]
        for sd_idx, sd_title in SUBDOMAINS[d].items():
            val = get_subdomain_avg(answers, d, sd_idx)
            sub_rows.append([sd_title, f"{val:.2f}" if val is not None else "–"])
        tbl = Table(sub_rows, colWidths=[130*mm, 30*mm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor(COL_HEX["mint"])),
            ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor(COL_HEX["anthracite"])),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#DDDDDD")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 6*mm))

    # Kapitel 4 - Übersichtstabelle (breit)
    story.append(PageBreak())
    story.append(Paragraph("4 Übersichtstabelle", styles["Chapter"]))
    table_data = [["Nr", "Bereich", "Score", "Interpretation"]]
    for d in range(1, 9):
        s = domain_scores.get(d, 0.0)
        table_data.append([str(d), DOMAINS[d], f"{s:.2f}", interpret_label(s)])
    sum_table = Table(table_data, colWidths=[15*mm, 95*mm, 25*mm, 35*mm])
    sum_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor(COL_HEX["mint"])),
        ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor(COL_HEX["anthracite"])),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#DDDDDD")),
        ("ALIGN", (2,1), (2,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    for i in range(1, len(table_data)):
        lab = table_data[i][3]
        hexc = pick_color_hex(float(table_data[i][2])) if False else pick_color_hex_from_label(lab)
        sum_table.setStyle(TableStyle([
            ("BACKGROUND", (3,i), (3,i), colors.HexColor(hexc)),
            ("TEXTCOLOR", (3,i), (3,i), colors.white if lab != "Mittel" else colors.black),
            ("FONTNAME", (3,i), (3,i), "Helvetica-Bold"),
        ]))
    story.append(sum_table)
    story.append(Spacer(1, 6*mm))

    # Legende
    story.append(Paragraph("Legende: 4.2–5.0 Sehr gut | 3.6–4.1 Gut | 3.0–3.5 Mittel | <3.0 Verbesserungsbedarf", styles["Muted"]))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    buf.seek(0)
    return buf

def pick_color_hex_from_label(label):
    if label == "Sehr gut":
        return "#1E6F5C"
    if label == "Gut":
        return "#2B8C69"
    if label == "Mittel":
        return "#E9B44C"
    return "#D9534F"

# --------------------------
# Streamlit UI (stabil)
# --------------------------
def init_session():
    if "step" not in st.session_state:
        st.session_state.step = "selection"
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "wg" not in st.session_state:
        st.session_state.wg = None
    if "wg_select" not in st.session_state:
        st.session_state.wg_select = WG_OPTIONS[0]

def create_test_answers():
    pool = ["Trifft voll zu", "Trifft zu", "Teils/teils", "Trifft nicht zu", "Trifft gar nicht zu"]
    out = {}
    for d in range(1,9):
        for sd in range(1,5):
            out[(d, sd)] = [pool[(d+sd) % len(pool)], pool[(d*2 + sd) % len(pool)]]
    return out

# Callback-Handler: benutzen on_click statt experiment_rerun
def start_test():
    st.session_state.answers = create_test_answers()
    st.session_state.wg = "WG Fliegenpilz"
    st.session_state.step = "results"

def start_real():
    st.session_state.step = "survey"

def go_to_results():
    st.session_state.step = "results"

def reset_all():
    st.session_state.clear()
    init_session()

def render_selection():
    st.title(PAGE_TITLE)
    st.markdown("Klinisch clean theme (white + mint + grey).")
    col1, col2 = st.columns(2)
    with col1:
        st.button("🚀 Schnelltest: Testdaten", on_click=start_test)
    with col2:
        st.button("📋 Start echte Befragung", on_click=start_real)

    st.write("---")
    st.selectbox("Wähle Abteilung", WG_OPTIONS, key="wg_select")
    if st.button("Weiter"):
        st.session_state.wg = st.session_state.wg_select
        start_real()
    st.write("")  # Platzhalter

def render_survey():
    st.header("Fragebogen")
    # finde erstes unbeantwortetes Item
    current_key = None
    for d in range(1,9):
        for sd in range(1,5):
            if (d, sd) not in st.session_state.answers:
                current_key = (d, sd)
                break
        if current_key:
            break
    if not current_key:
        go_to_results()
        return
    d, sd = current_key
    st.subheader(f"{DOMAINS[d]} — {SUBDOMAINS[d][sd]}")
    opts = ["Trifft voll zu", "Trifft zu", "Teils/teils", "Trifft nicht zu", "Trifft gar nicht zu"]
    a1 = st.radio("Item 1", opts, key=f"q_{d}_{sd}_0")
    a2 = st.radio("Item 2", opts, key=f"q_{d}_{sd}_1")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("← Zurück"):
            # entferne letztes key
            if st.session_state.answers:
                k = list(st.session_state.answers.keys())[-1]
                st.session_state.answers.pop(k, None)
    with col2:
        if a1 and a2:
            if st.button("Weiter →"):
                st.session_state.answers = st.session_state.get("answers", {})
                st.session_state.answers[(d, sd)] = [a1, a2]

def render_results():
    st.header("Resultate")
    answers = st.session_state.get("answers", {})
    domain_scores = calculate_scores_from_answers(answers)
    for d in range(1,9):
        sc = domain_scores.get(d, 0.0)
        st.subheader(DOMAINS[d])
        st.write(f"Score: {sc:.2f} — {interpret_label(sc)}")
        st.progress(sc / 5.0 if sc > 0 else 0.0)

    pdf_buf = make_pdf_buffer(st.session_state.get("wg", "n.a."), answers, logo_path=LOGO_PATH)
    st.download_button("📄 PDF Bericht herunterladen", data=pdf_buf,
                       file_name=f"Befragung_{st.session_state.get('wg','n.a.')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                       mime="application/pdf")
    if st.button("Neue Befragung (Reset)"):
        reset_all()

def main():
    st.set_page_config(page_title=PAGE_TITLE, layout="centered")
    init_session()
    # minimal CSS, keep background white
    st.markdown(f"<style>.main .block-container{{background-color: {COL_HEX['white']};}}</style>", unsafe_allow_html=True)

    if st.session_state.step == "selection":
        render_selection()
    elif st.session_state.step == "survey":
        render_survey()
    elif st.session_state.step == "results":
        render_results()

if __name__ == "__main__":
    main()
