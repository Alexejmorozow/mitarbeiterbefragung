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

# -------------------------
# Config / copyable values
# -------------------------
PAGE_TITLE = "Mitarbeiterbefragung - Klinisch sauber"
LOGO_PATH = None  # set path to a PNG if you want a logo in title page

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

# clinical color theme (white + mint + grey)
COL_HEX = {
    "mint": "#A8D5BA",
    "dark_mint": "#4A7C59",
    "anthracite": "#2F4F4F",
    "light_gray": "#F8F9FA",
    "white": "#FFFFFF",
    "warning": "#E9B44C",
    "danger": "#D9534F"
}

# scoring map
SCORE_MAP = {
    "Trifft voll zu": 5,
    "Trifft zu": 4,
    "Teils/teils": 3,
    "Trifft nicht zu": 2,
    "Trifft gar nicht zu": 1
}

# -------------------------
# Helpers: styles, footer
# -------------------------
def build_styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle("TitleCustom", parent=base["Title"],
                            fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=colors.HexColor(COL_HEX["anthracite"])))
    base.add(ParagraphStyle("H1", parent=base["Heading1"],
                            fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.HexColor(COL_HEX["anthracite"])))
    base.add(ParagraphStyle("Body", parent=base["BodyText"],
                            fontName="Helvetica", fontSize=10, leading=13, textColor=colors.HexColor(COL_HEX["anthracite"])))
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
    def __init__(self, width=160*mm, thickness=1):
        super().__init__()
        self.width = width
        self.thickness = thickness
    def draw(self):
        self.canv.setLineWidth(self.thickness)
        self.canv.setStrokeColor(colors.HexColor(COL_HEX["dark_mint"]))
        self.canv.line(0, 0, self.width, 0)

# -------------------------
# Scoring logic
# -------------------------
def calculate_scores_from_answers(answers):
    """
    answers: dict keyed by (domain, subdomain) -> list of textual answers
    returns: domain_avg_scores: dict domain -> float (1..5)
    """
    domain_scores = {}
    for (domain, subdomain), resp_list in answers.items():
        vals = [SCORE_MAP.get(r, None) for r in resp_list]
        vals = [v for v in vals if v is not None]
        if vals:
            domain_scores.setdefault(domain, []).extend(vals)
    domain_avg = {d: (sum(vs)/len(vs)) for d, vs in domain_scores.items()}
    # ensure all domains present
    for d in DOMAINS.keys():
        domain_avg.setdefault(d, 0.0)
    return domain_avg

# -------------------------
# Chart creation
# -------------------------
def create_radar_png(domain_scores):
    labels = [DOMAINS[i] for i in range(1, 9)]
    values = [domain_scores.get(i, 0.0) for i in range(1, 9)]
    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]
    vals = values + values[:1]

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.plot(angles, vals, linewidth=2, linestyle='solid', color=COL_HEX["dark_mint"])
    ax.fill(angles, vals, color=COL_HEX["mint"], alpha=0.25)
    ax.set_ylim(0, 5)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_yticks([1,2,3,4,5])
    ax.set_title("Profil der Arbeitsbereiche", pad=12, fontsize=12, color=COL_HEX["anthracite"])
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

def create_bar_png(domain_scores):
    labels = [DOMAINS[i] for i in range(1, 9)]
    values = [domain_scores.get(i, 0.0) for i in range(1, 9)]

    fig, ax = plt.subplots(figsize=(8, 3))
    bars = ax.barh(range(len(labels)), values, color=COL_HEX["mint"], edgecolor=COL_HEX["dark_mint"])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(0,5)
    ax.invert_yaxis()
    ax.set_xlabel("Score (1-5)")
    ax.grid(axis='x', linestyle=':', linewidth=0.5)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

# -------------------------
# PDF assembly
# -------------------------
def make_pdf_buffer(wg_name, answers, include_charts=True, logo_path=None):
    domain_scores = calculate_scores_from_answers(answers)
    overall = sum(domain_scores.values()) / len(domain_scores) if domain_scores else 0.0

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=25*mm)
    styles = build_styles()
    story = []

    # Title page
    if logo_path:
        try:
            story.append(Image(logo_path, width=40*mm, height=40*mm))
            story.append(Spacer(1,4*mm))
        except Exception:
            pass
    story.append(Paragraph(PAGE_TITLE, styles["TitleCustom"]))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(f"<b>Abteilung:</b> {wg_name}", styles["Body"]))
    story.append(Paragraph(f"<b>Erstellt:</b> {datetime.now().strftime('%d.%m.%Y')}", styles["Body"]))
    story.append(Spacer(1, 6*mm))
    story.append(HRLine(width=170*mm))
    story.append(Spacer(1, 8*mm))

    # Executive summary
    story.append(Paragraph("Kurz: Executive summary", styles["H1"]))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(f"Gesamtindex: <b>{overall:.2f}</b> (Skala 1..5)", styles["Body"]))
    strengths = [DOMAINS[d] for d, s in domain_scores.items() if s >= 4.2]
    to_improve = [DOMAINS[d] for d, s in domain_scores.items() if s < 3.0]
    if strengths:
        story.append(Paragraph("Stärken: " + ", ".join(strengths), styles["Body"]))
    if to_improve:
        story.append(Paragraph("Entwicklungsbereiche: " + ", ".join(to_improve), styles["Body"]))
    story.append(Spacer(1, 6*mm))
    story.append(PageBreak())

    # Charts
    if include_charts:
        story.append(Paragraph("Profilübersicht", styles["H1"]))
        story.append(Spacer(1, 4*mm))
        radar_buf = create_radar_png(domain_scores)
        story.append(Image(radar_buf, width=140*mm, height=140*mm))
        story.append(Spacer(1, 6*mm))
        bar_buf = create_bar_png(domain_scores)
        story.append(Image(bar_buf, width=160*mm, height=60*mm))
        story.append(PageBreak())

    # Detailed per domain (box + short note + subdomain table)
    for d in range(1, 9):
        s = domain_scores.get(d, 0.0)
        label = interpret_label(s)
        story.append(Paragraph(DOMAINS[d], styles["H1"]))
        story.append(Spacer(1, 2*mm))

        # coloured label: implement as tiny 1-cell table
        tbl = Table([[f"{label} — {s:.2f}/5"]], colWidths=[160*mm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor(pick_color_hex(s))),
            ("TEXTCOLOR", (0,0), (-1,-1), colors.white if s < 3.6 or s >= 3.6 else colors.white),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 3*mm))

        # subdomain table (if answers exist, compute subdomain averages)
        sub_rows = [["Thema", "Score"]]
        for sd_idx, sd_title in SUBDOMAINS[d].items():
            val = get_subdomain_avg(answers, d, sd_idx)
            sub_rows.append([sd_title, f"{val:.2f}" if val is not None else "–"])
        t = Table(sub_rows, colWidths=[110*mm, 30*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor(COL_HEX["mint"])),
            ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor(COL_HEX["anthracite"])),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,0), 9),
            ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#DDDDDD")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(t)
        story.append(Spacer(1, 6*mm))

    # Summary table of all domains
    story.append(PageBreak())
    story.append(Paragraph("Uebersicht: Alle Bereiche", styles["H1"]))
    table_data = [["Nr", "Bereich", "Score", "Interpretation"]]
    for d in range(1, 9):
        s = domain_scores.get(d, 0.0)
        table_data.append([str(d), DOMAINS[d], f"{s:.2f}", interpret_label(s)])
    sum_table = Table(table_data, colWidths=[15*mm, 85*mm, 25*mm, 45*mm])
    sum_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor(COL_HEX["mint"])),
        ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor(COL_HEX["anthracite"])),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#DDDDDD")),
        ("ALIGN", (2,1), (2,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    # color interpretation cell
    for i in range(1, len(table_data)):
        lab = table_data[i][3]
        hexc = pick_color_hex_from_label(lab)
        sum_table.setStyle(TableStyle([
            ("BACKGROUND", (3,i), (3,i), colors.HexColor(hexc)),
            ("TEXTCOLOR", (3,i), (3,i), colors.white if lab != "Mittel" else colors.black),
            ("FONTNAME", (3,i), (3,i), "Helvetica-Bold"),
        ]))
    story.append(sum_table)
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("Legende: 4.2-5.0 Sehr gut | 3.6-4.1 Gut | 3.0-3.5 Mittel | <3.0 Verbesserungsbedarf", styles["Muted"]))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    buf.seek(0)
    return buf

# -------------------------
# small helper functions
# -------------------------
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

def pick_color_hex_from_label(label):
    if label == "Sehr gut":
        return "#1E6F5C"
    if label == "Gut":
        return "#2B8C69"
    if label == "Mittel":
        return "#E9B44C"
    return "#D9534F"

def get_subdomain_avg(answers, domain, subdomain):
    v = answers.get((domain, subdomain))
    if not v:
        return None
    nums = [SCORE_MAP.get(x) for x in v if SCORE_MAP.get(x) is not None]
    return (sum(nums)/len(nums)) if nums else None

# -------------------------
# Streamlit UI
# -------------------------
def create_test_answers():
    # create realistic variation
    pool = ["Trifft voll zu", "Trifft zu", "Teils/teils", "Trifft nicht zu", "Trifft gar nicht zu"]
    out = {}
    for d in range(1,9):
        for sd in range(1,5):
            # generate two answers per subdomain
            out[(d, sd)] = [pool[(d + sd) % len(pool)], pool[(d*2 + sd) % len(pool)]]
    return out

def render_selection():
    st.title(PAGE_TITLE)
    st.write("Klinisch clean theme (white + mint + grey).")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Schnelltest: Testdaten"):
            st.session_state.answers = create_test_answers()
            st.session_state.wg = "WG Fliegenpilz"
            st.session_state.step = "results"
            st.experimental_rerun()
    with col2:
        if st.button("📋 Start echte Befragung"):
            st.session_state.step = "survey"
            st.experimental_rerun()
    st.write("---")
    st.selectbox("Wähle Abteilung", WG_OPTIONS, key="wg_select")
    if st.button("Weiter"):
        st.session_state.wg = st.session_state.wg_select
        st.session_state.step = "survey"
        st.experimental_rerun()

def render_survey():
    st.header("Fragen")
    st.write("Kurz: beantworte pro Block die Items.")
    current_key = None
    for d in range(1,9):
        for sd in range(1,5):
            if (d, sd) not in st.session_state.get("answers", {}):
                current_key = (d, sd)
                break
        if current_key:
            break
    if not current_key:
        st.session_state.step = "results"
        st.experimental_rerun()
        return
    d, sd = current_key
    st.subheader(f"{DOMAINS[d]} — {SUBDOMAINS[d][sd]}")
    opts = ["Trifft voll zu", "Trifft zu", "Teils/teils", "Trifft nicht zu", "Trifft gar nicht zu"]
    a1 = st.radio("Item 1", opts, key=f"q_{d}_{sd}_0")
    a2 = st.radio("Item 2", opts, key=f"q_{d}_{sd}_1")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Zurück"):
            if st.session_state.get("answers"):
                keys = list(st.session_state.answers.keys())
                if keys:
                    st.session_state.answers.pop(keys[-1], None)
                    st.experimental_rerun()
    with col2:
        if a1 and a2:
            if st.button("Weiter →"):
                st.session_state.answers = st.session_state.get("answers", {})
                st.session_state.answers[(d, sd)] = [a1, a2]
                st.experimental_rerun()

def render_results():
    st.header("Resultate")
    if st.session_state.get("test_mode"):
        st.warning("Testdaten aktiv")
    answers = st.session_state.get("answers", {})
    domain_scores = calculate_scores_from_answers(answers)
    for d in range(1,9):
        sc = domain_scores.get(d, 0.0)
        st.subheader(DOMAINS[d])
        st.write(f"Score: {sc:.2f} — {interpret_label(sc)}")
        st.progress(sc / 5.0 if sc > 0 else 0.0)
    pdf_buf = make_pdf_buffer(st.session_state.get("wg", "n.a."), answers, include_charts=True, logo_path=LOGO_PATH)
    st.download_button("📄 PDF Bericht herunterladen", data=pdf_buf, file_name=f"Befragung_{st.session_state.get('wg','n.a.')}_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf")

# -------------------------
# Boot
# -------------------------
def init_session_defaults():
    if "step" not in st.session_state:
        st.session_state.step = "selection"
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "wg" not in st.session_state:
        st.session_state.wg = None
    if "test_mode" not in st.session_state:
        st.session_state.test_mode = False

def main():
    st.set_page_config(page_title=PAGE_TITLE, layout="centered", initial_sidebar_state="collapsed")
    init_session_defaults()
    st.markdown(f"<style> .reportview-container .main .block-container{{background-color: {COL_HEX['white']};}}</style>", unsafe_allow_html=True)

    if st.session_state.step == "selection":
        render_selection()
    elif st.session_state.step == "survey":
        render_survey()
    elif st.session_state.step == "results":
        render_results()

if __name__ == "__main__":
    main()
