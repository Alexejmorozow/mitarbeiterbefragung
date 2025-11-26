import streamlit as st
import pandas as pd
from datetime import datetime
import json
import io
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Flowable
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm, cm

# Konfiguration
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
    1: {
        1: "Zeit pro Bewohner",
        2: "Unterbrechungen", 
        3: "Arbeitsverdichtung",
        4: "Ausfallmanagement"
    },
    2: {
        1: "Onboarding-Qualität",
        2: "Verfügbarkeit von Ansprechpartnern",
        3: "Übergaben & Informationsfluss", 
        4: "Fort- und Weiterbildung"
    },
    3: {
        1: "Zusammenhalt",
        2: "Verlässlichkeit",
        3: "Rollen & Aufgaben", 
        4: "Umgang mit Spannungen"
    },
    4: {
        1: "Fachliche Führung",
        2: "Soziale Führung",
        3: "Verfügbarkeit", 
        4: "Klarheit von Erwartungen"
    },
    5: {
        1: "Physische Belastung",
        2: "Psychische Erschöpfung",
        3: "Pausenrealisierung", 
        4: "Gesundheitsangebote"
    },
    6: {
        1: "Technische Hilfsmittel",
        2: "Digitale Dokumentation",
        3: "Standardisierte Abläufe", 
        4: "Verfügbarkeit & Wartung"
    },
    7: {
        1: "Planbarkeit",
        2: "Fairness",
        3: "Umgang mit Ausfällen", 
        4: "Erholung"
    },
    8: {
        1: "Schichtübergaben",
        2: "Austausch zwischen Berufsgruppen",
        3: "Kommunikation mit Leitung", 
        4: "Digitale Kanäle"
    }
}

# Vollständiger Fragenkatalog
QUESTIONS = {
    # DOMÄNE 1 – Arbeitsbelastung & Zeitdruck
    (1, 1): [
        "Ich habe genügend Zeit, um Bewohner*innen professionell und in Ruhe zu betreuen.",
        "Ich schaffe die Dokumentation üblicherweise innerhalb der regulären Arbeitszeit."
    ],
    (1, 2): [
        "Ich kann meine Aufgaben meistens ohne häufige Unterbrechungen durchführen.",
        "Ungeplante Störungen hindern mich regelmässig an konzentrierter Arbeit."
    ],
    (1, 3): [
        "Die Aufgaben pro Schicht haben im Vergleich zum Vorjahr spürbar zugenommen.",
        "Anforderungen sind gestiegen, ohne dass Ressourcen angepasst wurden."
    ],
    (1, 4): [
        "Bei Personalausfällen wird schnell und professionell reagiert.",
        "Ich habe das Gefühl, dass bei Ausfällen fair reagiert wird."
    ],
    
    # DOMÄNE 2 – Einarbeitung & Personalentwicklung
    (2, 1): [
        "Die Einarbeitung neuer Mitarbeitender folgt einem klaren Plan.",
        "Neue Kolleg*innen wissen früh, was von ihnen erwartet wird."
    ],
    (2, 2): [
        "Neue Mitarbeitende haben feste Personen, die sie begleiten.",
        "Bei Unsicherheiten ist verlässlich jemand ansprechbar."
    ],
    (2, 3): [
        "Schichtübergaben sind vollständig und verständlich.",
        "Wichtige Infos gehen zwischen Früh-, Mittel- und Spätdienst nicht verloren."
    ],
    (2, 4): [
        "Ich habe ausreichend Möglichkeiten zur Weiterentwicklung.",
        "Fortbildungen sind praxisrelevant und hilfreich."
    ],
    
    # DOMÄNE 3 – Zusammenarbeit & Teamklima
    (3, 1): [
        "In meinem Team besteht echter Zusammenhalt, auch bei Stress.",
        "Wir unterstützen uns gegenseitig."
    ],
    (3, 2): [
        "Kolleg*innen halten sich an Absprachen.",
        "Ich kann mich auf mein Team verlassen."
    ],
    (3, 3): [
        "Zuständigkeiten und Verantwortungen sind klar geregelt.",
        "Jeder weiss, was zu tun ist."
    ],
    (3, 4): [
        "Konflikte werden offen angesprochen.",
        "Kritik ist möglich, ohne negative Folgen befürchten zu müssen."
    ],
    
    # DOMÄNE 4 – Führung
    (4, 1): [
        "Meine Leitung trifft fachlich fundierte Entscheidungen.",
        "Die Führungskraft verfügt über hohe fachliche Kompetenz."
    ],
    (4, 2): [
        "Ich werde respektvoll und wertschätzend behandelt.",
        "Meine Führungskraft interessiert sich dafür, wie es mir geht."
    ],
    (4, 3): [
        "Die Leitung ist erreichbar, wenn ich Unterstützung brauche.",
        "Auch in schwierigen Situationen habe ich Rückhalt."
    ],
    (4, 4): [
        "Ziele und Prioritäten sind klar kommuniziert.",
        "Entscheidungen sind transparent begründet."
    ],
    
    # DOMÄNE 5 – Gesundheit, körperliche & psychische Belastung
    (5, 1): [
        "Die körperliche Belastung ist langfristig tragbar.",
        "Ich kann meinen Körper im Alltag schonen, ohne Qualität zu verlieren."
    ],
    (5, 2): [
        "Ich kann nach der Arbeit gut abschalten.",
        "Emotionale Belastungen wirken nicht lange nach."
    ],
    (5, 3): [
        "Ich kann Pausen meistens wie geplant einhalten.",
        "Ich habe ausreichend Möglichkeiten zum kurzen Auftanken."
    ],
    (5, 4): [
        "Gesundheitsangebote (Fitnessraum, Obst, Schulungen, Gesundheitsmanagement etc.) sind vorhanden und realistisch nutzbar.",
        "Gesundheitsprävention gehört sichtbar zum Arbeitsalltag."
    ],
    
    # DOMÄNE 6 – Technische & organisatorische Entlastungssysteme
    (6, 1): [
        "Transfer- und Hebehilfen sind funktionsfähig und verfügbar.",
        "Ich kann technische Hilfsmittel jederzeit nutzen."
    ],
    (6, 2): [
        "Digitale Dokumentation spart Zeit.",
        "Systeme sind logisch und intuitiv bedienbar."
    ],
    (6, 3): [
        "Es bestehen klare und verständliche Checklisten oder Arbeitsabläufe, die jederzeit leicht auffindbar sind.",
        "Standards werden im Alltag angewendet."
    ],
    (6, 4): [
        "Material und Hilfsmittel sind ausreichend vorhanden.",
        "Defekte Geräte werden schnell repariert oder ersetzt."
    ],
    
    # DOMÄNE 7 – Dienst- & Einsatzplanung
    (7, 1): [
        "Dienstpläne sind früh und zuverlässig verfügbar.",
        "Kurzfristige Änderungen sind die Ausnahme."
    ],
    (7, 2): [
        "Wochenend- und Spätdienste sind fair verteilt.",
        "Die Belastung ist im Team ausgewogen."
    ],
    (7, 3): [
        "Bei Ausfällen wird kompetent reagiert.",
        "Ich werde dabei nicht dauerhaft überlastet."
    ],
    (7, 4): [
        "Ich habe ausreichend Erholungszeit zwischen Diensten.",
        "Dienstfolgen (z. B. Spät–Früh) sind nicht dauerhaft belastend."
    ],
    
    # DOMÄNE 8 – Kommunikation & Informationsfluss
    (8, 1): [
        "Übergaben sind vollständig und strukturiert.",
        "Ich weiss zu Schichtbeginn, was mich erwartet."
    ],
    (8, 2): [
        "Zusammenarbeit zwischen Pflege, Agogik, Therapie, Küche, Hauswirtschaft etc. läuft reibungslos.",
        "Informationen werden konsistent weitergegeben."
    ],
    (8, 3): [
        "Entscheidungen werden erklärt und begründet.",
        "Ich fühle mich ausreichend informiert."
    ],
    (8, 4): [
        "Digitale Kommunikationswege sind klar geregelt.",
        "Es gibt kein Durcheinander mehrerer widersprüchlicher Kanäle."
    ]
}

# Farbschema: Matteres Grün, Anthrazit, Weiss
COLORS = {
    "mint": "#A8D5BA",
    "anthrazit": "#2F4F4F",
    "white": "#FFFFFF",
    "light_gray": "#F8F9FA",
    "dark_green": "#4A7C59",
    "light_mint": "#D4EDDA"
}

def get_interpretation(score):
    """Gibt die Interpretation eines Scores zurück"""
    if score >= 4.2:
        return "Sehr gut", colors.HexColor("#1E6F5C")
    elif score >= 3.6:
        return "Gut", colors.HexColor("#2B8C69")
    elif score >= 3.0:
        return "Mittel", colors.HexColor("#E9B44C")
    else:
        return "Verbesserungsbedarf", colors.HexColor("#D9534F")

def initialize_session():
    """Initialisiert die Session State Variablen"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'wg_selection'
    if 'wg_selected' not in st.session_state:
        st.session_state.wg_selected = None
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'test_data_created' not in st.session_state:
        st.session_state.test_data_created = False

def create_test_data():
    """Erstellt Test-Daten für schnelles Testen"""
    test_answers = {}
    for domain in range(1, 9):
        for subdomain in range(1, 5):
            test_answers[(domain, subdomain)] = ["Trifft zu", "Teils/teils"]
    return test_answers

def apply_custom_styles():
    """Wendet das benutzerdefinierte Farbschema an"""
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {COLORS['mint']};
    }}
    .main .block-container {{
        background-color: {COLORS['white']};
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 1rem;
        margin-bottom: 1rem;
    }}
    .css-1d391kg {{
        background-color: {COLORS['light_mint']};
    }}
    [data-testid="stProgress"] > div > div > div:first-child {{
        background-color: {COLORS['light_gray']} !important;
        border-radius: 10px;
        height: 20px;
    }}
    [data-testid="stProgress"] div[data-testid="stProgressBar"] {{
        background-color: {COLORS['dark_green']} !important;
        border-radius: 10px;
        height: 20px;
    }}
    .stRadio > div {{
        background-color: {COLORS['dark_green']};
        color: {COLORS['white']};
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid {COLORS['mint']};
    }}
    .stRadio label {{
        color: {COLORS['white']} !important;
        font-weight: 500;
    }}
    .stRadio [data-testid="stMarkdownContainer"] p {{
        color: {COLORS['white']} !important;
    }}
    .stSelectbox > div > div {{
        background-color: {COLORS['white']};
        border: 1px solid {COLORS['anthrazit']};
        border-radius: 6px;
    }}
    .stButton>button {{
        background-color: {COLORS['dark_green']};
        color: {COLORS['white']};
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
    }}
    .stButton>button:hover {{
        background-color: {COLORS['anthrazit']};
        color: {COLORS['white']};
    }}
    .main-header {{
        color: {COLORS['anthrazit']};
        border-bottom: 2px solid {COLORS['dark_green']};
        padding-bottom: 10px;
    }}
    .stSuccess {{
        background-color: {COLORS['dark_green']} !important;
        color: {COLORS['white']} !important;
        border: 1px solid {COLORS['dark_green']};
        border-radius: 8px;
        padding: 15px;
    }}
    .stInfo {{
        background-color: {COLORS['dark_green']} !important;
        color: {COLORS['white']} !important;
        border: 1px solid {COLORS['dark_green']};
        border-radius: 8px;
        border-left: 4px solid {COLORS['mint']};
        padding: 15px;
    }}
    .stWarning {{
        background-color: {COLORS['dark_green']} !important;
        color: {COLORS['white']} !important;
        border: 1px solid {COLORS['dark_green']};
        border-radius: 8px;
        padding: 15px;
    }}
    .stError {{
        background-color: #D9534F;
        color: {COLORS['white']} !important;
        border: 1px solid #D9534F;
        border-radius: 8px;
        padding: 15px;
    }}
    .streamlit-expanderHeader {{
        background-color: {COLORS['dark_green']};
        color: {COLORS['white']} !important;
        border: 1px solid {COLORS['mint']};
        border-radius: 8px;
    }}
    .streamlit-expanderContent {{
        background-color: {COLORS['light_gray']};
        border-radius: 0 0 8px 8px;
    }}
    .stSuccess svg, .stInfo svg, .stWarning svg {{
        fill: {COLORS['white']} !important;
        color: {COLORS['white']} !important;
    }}
    .stSuccess [data-testid="stMarkdownContainer"] p,
    .stInfo [data-testid="stMarkdownContainer"] p,
    .stWarning [data-testid="stMarkdownContainer"] p {{
        color: {COLORS['white']} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

def render_wg_selection():
    """WG Auswahl Schritt"""
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🏠 Mitarbeiterbefragung Hausverbund A")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Im Mai 2025 fand die kantonale Personalbefragung der Institutionen für Menschen mit Behinderungen statt. 
    Die Ergebnisse für unseren Bereich waren insgesamt erfreulich und haben sowohl Stärken als auch Entwicklungsbereiche aufgezeigt.

    **Um diese Ergebnisse besser zu verstehen**, führen wir nun eine vertiefte Befragung in unserem **Hausverbund A** durch. 
    Wir möchten genauer nachvollziehen:
    - Was hinter den positiven Rückmeldungen steht  
    - Wo die Ursachen für kritischere Bewertungen liegen

    **Wichtig:** Es geht nicht um die Beurteilung Einzelner, sondern um eine strukturierte Analyse der 
    Arbeitsbedingungen, Belastungen und Teamstärken **in unserem Hausverbund A**.

    **Deine Teilnahme ist wertvoll**, denn nur durch eine breite Beteiligung entsteht ein realistisches Bild 
    unserer Situation **im Hausverbund A**. Je genauer die Rückmeldungen, desto besser können wir verstehen, 
    was im Alltag gut funktioniert und wo Verbesserungen sinnvoll sind.

    Vielen Dank für deine Mitarbeit und die investierte Zeit!
    """)
    
    # TEST-BUTTON FÜR SCHNELLEN TEST
    st.write("---")
    st.subheader("🛠️ Testbereich")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Schnelltest: Mit Testdaten füllen", type="secondary"):
            st.session_state.answers = create_test_data()
            st.session_state.wg_selected = "WG Fliegenpilz"
            st.session_state.current_step = 'results'
            st.session_state.test_data_created = True
            st.rerun()
    
    with col2:
        if st.button("📋 Normale Befragung starten", type="primary"):
            st.session_state.current_step = 'survey'
            st.rerun()
    
    if st.session_state.get('test_data_created', False):
        st.success("✅ Test-Daten wurden erstellt! Du wirst zur Ergebnis-Seite weitergeleitet...")
    
    st.subheader("Bitte wähle deine Abteilung aus")
    
    selected_wg = st.selectbox(
        "Abteilung:",
        WG_OPTIONS,
        key="wg_select"
    )
    
    st.info("💡 Die Befragung ist komplett anonym. Deine Antworten können nicht dir persönlich zugeordnet werden.")
    
    if st.button("Befragung starten"):
        st.session_state.wg_selected = selected_wg
        st.session_state.current_step = 'survey'
        st.rerun()

def render_survey():
    """Haupt-Befragung mit allen Fragen"""
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("📝 Mitarbeiterbefragung")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write(f"**Abteilung:** {st.session_state.wg_selected}")
    
    # Aktuelle unbeantwortete Frage finden
    current_key = None
    for domain in range(1, 9):
        for subdomain in range(1, 5):
            if (domain, subdomain) not in st.session_state.answers:
                current_key = (domain, subdomain)
                break
        if current_key:
            break
    
    if not current_key:
        st.session_state.current_step = 'results'
        st.rerun()
        return
    
    domain, subdomain = current_key
    questions = QUESTIONS.get(current_key, [])
    
    # Fortschrittsberechnung
    total_questions = len(QUESTIONS)
    completed_questions = len(st.session_state.answers)
    progress = completed_questions / total_questions
    
    st.progress(progress)
    st.write(f"Fortschritt: {completed_questions + 1} von {total_questions} Fragen")
    
    # Frage anzeigen
    st.subheader("Bitte beantworte die folgenden Fragen:")
    
    answers = []
    for i, question in enumerate(questions):
        st.write(f"**{question}**")
        answer = st.radio(
            f"Deine Antwort:",
            options=["Trifft voll zu", "Trifft zu", "Teils/teils", "Trifft nicht zu", "Trifft gar nicht zu"],
            key=f"q_{domain}_{subdomain}_{i}",
            index=None
        )
        answers.append(answer)
    
    # Navigation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.answers:
            if st.button("← Zurück"):
                last_key = list(st.session_state.answers.keys())[-1]
                del st.session_state.answers[last_key]
                st.rerun()
    
    with col2:
        all_answered = all(answers) and len(answers) > 0
        if all_answered:
            if st.button("Weiter →"):
                st.session_state.answers[current_key] = answers
                st.rerun()
        else:
            st.button("Weiter →", disabled=True)

def calculate_scores():
    """Berechnet die Scores aus den Antworten"""
    scoring = {
        "Trifft voll zu": 5,
        "Trifft zu": 4,
        "Teils/teils": 3, 
        "Trifft nicht zu": 2,
        "Trifft gar nicht zu": 1
    }
    
    domain_scores = {}
    for (domain, subdomain), answers in st.session_state.answers.items():
        if domain not in domain_scores:
            domain_scores[domain] = []
        
        for answer in answers:
            if answer in scoring:
                domain_scores[domain].append(scoring[answer])
    
    avg_scores = {}
    for domain, scores in domain_scores.items():
        if scores:
            avg_scores[domain] = sum(scores) / len(scores)
    
    return avg_scores

# ---- PDF Aufbau mit platypus ----

class HRDivider(Flowable):
    """einfache Linie als Trenner"""
    def __init__(self, width=160):
        Flowable.__init__(self)
        self.width = width

    def draw(self):
        self.canv.setLineWidth(1)
        self.canv.setStrokeColor(colors.HexColor(COLORS["dark_green"]))
        x = 0
        y = 0
        self.canv.line(x, y, self.width, y)

def _build_styles():
    base = getSampleStyleSheet()
    base.add(ParagraphStyle(
        name="TitleCustom",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        spaceAfter=12,
        textColor=colors.HexColor(COLORS["anthrazit"])
    ))
    base.add(ParagraphStyle(
        name="H1",
        parent=base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor(COLORS["anthrazit"]),
        spaceAfter=8
    ))
    base.add(ParagraphStyle(
        name="Body",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        spaceAfter=6
    ))
    base.add(ParagraphStyle(
        name="TableHeader",
        parent=base["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        alignment=1,  # zentriert
    ))
    base.add(ParagraphStyle(
        name="SmallMuted",
        parent=base["BodyText"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10,
        textColor=colors.gray
    ))
    return base

def _footer(canvas_obj, doc):
    canvas_obj.saveState()
    width, height = A4
    footer_text = f"Erstellt: {datetime.now().strftime('%d.%m.%Y')}   |   Seite {doc.page}"
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(colors.HexColor(COLORS["anthrazit"]))
    canvas_obj.drawRightString(width - 20*mm, 15*mm, footer_text)
    canvas_obj.restoreState()

def create_pdf_report():
    """Erstellt einen PDF-Report mit verbesserter Struktur"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=25*mm
    )
    styles = _build_styles()
    story = []

    # Titelblatt
    story.append(Paragraph("Mitarbeiterbefragung - Ergebnisbericht", styles["TitleCustom"]))
    story.append(Spacer(1, 6*mm))
    meta = [
        f"<b>Abteilung:</b> {st.session_state.wg_selected or 'n.a.'}",
        f"<b>Datum:</b> {datetime.now().strftime('%d.%m.%Y')}"
    ]
    if st.session_state.get("test_data_created", False):
        meta.append("<b>Hinweis:</b> Testdaten (simuliert)")
    else:
        meta.append("<b>Hinweis:</b> Befragung anonym")
    for m in meta:
        story.append(Paragraph(m, styles["Body"]))
    story.append(Spacer(1, 8*mm))
    story.append(HRDivider(width=160))
    story.append(Spacer(1, 10*mm))

    # Executive Summary
    story.append(Paragraph("Kurze Zusammenfassung", styles["H1"]))
    scores = calculate_scores()
    if scores:
        total_avg = sum(scores.values()) / len(scores)
        story.append(Paragraph(f"Gesamtdurchschnitt: <b>{total_avg:.2f}/5</b>", styles["Body"]))
    else:
        story.append(Paragraph("Keine Daten vorhanden.", styles["Body"]))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph(
        "Diese Auswertung gibt kompakt einen Überblick pro Themenbereich. Farben deuten die Dringlichkeit an.",
        styles["Body"]
    ))
    story.append(PageBreak())

    # Ergebnisse pro Bereich als Karte
    for domain in range(1, 9):
        domain_title = DOMAINS.get(domain, f"Bereich {domain}")
        score = scores.get(domain, 0.0)
        label, col = get_interpretation(score)

        story.append(Paragraph(domain_title, styles["H1"]))
        story.append(Spacer(1, 2*mm))

        # farbige Box: einfache Darstellung via Tabelle mit 1 Zelle
        box_data = [[f"{label}  —  {score:.2f}/5" ]]
        box = Table(box_data, colWidths=[160*mm])
        box.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), col),
            ("TEXTCOLOR", (0,0), (-1,-1), colors.white),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 10),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(box)
        story.append(Spacer(1, 4*mm))

        # kurze Hinweise / Interpretationstext
        if score >= 4.2:
            note = "Stabile Lage. Erhaltende Massnahmen empfohlen."
        elif score >= 3.6:
            note = "Gute Lage. Punktuelle Optimierungen möglich."
        elif score >= 3.0:
            note = "Mittel. Gezielte Massnahmen sollen priorisiert werden."
        else:
            note = "Verbesserungsbedarf. Handlungsbedarf hoch."

        story.append(Paragraph(note, styles["Body"]))
        story.append(Spacer(1, 4*mm))

        # Tabelle mit Subdomain-Informationen
        tdata = [["Teilbereich", "Score"]]
        # Hier könnten bei Bedarf Subdomain-Scores eingefügt werden
        tdata.append(["Gesamtbewertung", f"{score:.2f}/5"])
        t = Table(tdata, colWidths=[110*mm, 40*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor(COLORS["mint"])),
            ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor(COLORS["anthrazit"])),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ALIGN", (1,1), (1,-1), "CENTER"),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor(COLORS["anthrazit"])),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 8*mm))
        story.append(HRDivider(width=160))
        story.append(Spacer(1, 8*mm))

    # Detailtabelle: Übersicht aller Bereiche
    story.append(PageBreak())
    story.append(Paragraph("Übersicht aller Bereiche", styles["H1"]))
    table_data = [["Nr", "Bereich", "Score", "Interpretation"]]
    for d in range(1,9):
        s = scores.get(d, 0.0)
        label, _ = get_interpretation(s)
        table_data.append([str(d), DOMAINS.get(d, ""), f"{s:.2f}/5", label])

    table = Table(table_data, colWidths=[20*mm, 90*mm, 30*mm, 40*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor(COLORS["mint"])),
        ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor(COLORS["anthrazit"])),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor(COLORS["anthrazit"])),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (2,1), (2,-1), "CENTER"),
        ("ALIGN", (0,1), (0,-1), "CENTER"),
    ]))

    # bedingte Färbung für Interpretation
    for i in range(1, len(table_data)):
        interp = table_data[i][3]
        if interp == "Sehr gut":
            bg = colors.HexColor("#1E6F5C")
        elif interp == "Gut":
            bg = colors.HexColor("#2B8C69")
        elif interp == "Mittel":
            bg = colors.HexColor("#E9B44C")
        else:
            bg = colors.HexColor("#D9534F")
        table.setStyle(TableStyle([
            ("BACKGROUND", (3,i), (3,i), bg),
            ("TEXTCOLOR", (3,i), (3,i), colors.white if interp != "Mittel" else colors.black),
            ("FONTNAME", (3,i), (3,i), "Helvetica-Bold"),
        ]))

    story.append(table)
    story.append(Spacer(1, 8*mm))

    # Hinweise & Next steps
    story.append(Paragraph("Nächste Schritte", styles["H1"]))
    story.append(Paragraph("1) Bericht intern teilen. 2) Fokusgruppen planen. 3) Massnahmen priorisieren.", styles["Body"]))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("Produziert mit internem Tool.", styles["SmallMuted"]))

    # Build
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    buffer.seek(0)
    return buffer

def render_results():
    """Zeigt die Ergebnisse und PDF-Download an"""
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("✅ Befragung abgeschlossen!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.get('test_data_created', False):
        st.warning("🛠️ **Testmodus** - Dies sind simulierte Daten")
    else:
        st.success("Vielen Dank für deine Teilnahme an der Befragung!")
    
    st.subheader("Zusammenfassung deiner Antworten")
    
    scores = calculate_scores()
    for domain in range(1, 9):
        score = scores.get(domain, 0)
        interpretation, color = get_interpretation(score)
        st.write(f"**{DOMAINS[domain]}:** {score:.2f}/5 Punkte - *{interpretation}*")
        st.progress(score / 5)
    
    # PDF erstellen
    pdf_buffer = create_pdf_report()
    
    st.subheader("📊 Bericht herunterladen")
    
    st.download_button(
        label="📄 PDF Bericht herunterladen",
        data=pdf_buffer,
        file_name=f"Befragung_{st.session_state.wg_selected}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        type="primary"
    )
    
    st.info("""
    **📋 Nächste Schritte:**
    - Lade den PDF-Bericht herunter
    - Drucke ihn aus
    - Leg ihn deiner/m Vorgesetzten in sein/ihr Fach
    """)
    
    # Neue Befragung starten
    st.write("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Neue Test-Befragung"):
            st.session_state.answers = create_test_data()
            st.session_state.test_data_created = True
            st.rerun()
    
    with col2:
        if st.button("🏠 Neue echte Befragung"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def main():
    """Hauptfunktion der Anwendung"""
    st.set_page_config(
        page_title="Mitarbeiterbefragung",
        page_icon="📊",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    apply_custom_styles()
    initialize_session()
    
    if st.session_state.current_step == 'wg_selection':
        render_wg_selection()
    elif st.session_state.current_step == 'survey':
        render_survey()
    elif st.session_state.current_step == 'results':
        render_results()

if __name__ == "__main__":
    main()
