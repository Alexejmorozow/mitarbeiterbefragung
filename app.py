import streamlit as st
import pandas as pd
from datetime import datetime
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import io

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
    what im Alltag gut funktioniert und wo Verbesserungen sinnvoll sind.

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

def create_visual_score_bar(score, width=200, height=20):
    """Erstellt einen visuellen Score-Balken für die PDF"""
    # Farben basierend auf Score
    if score >= 4.2:
        color = colors.HexColor("#1E6F5C")  # Sehr gut
    elif score >= 3.6:
        color = colors.HexColor("#2B8C69")   # Gut
    elif score >= 3.0:
        color = colors.HexColor("#E9B44C")   # Mittel
    else:
        color = colors.HexColor("#D9534F")   # Verbesserungsbedarf
    
    return color, score / 5.0  # Rückgabe Farbe und Prozentsatz

def create_pdf_report():
    """Erstellt einen verbesserten PDF-Report mit professionellem Design"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              topMargin=2*cm, 
                              bottomMargin=2*cm,
                              leftMargin=1.5*cm,
                              rightMargin=1.5*cm)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Titel
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor(COLORS['anthrazit']),
            spaceAfter=30,
            alignment=1  # Zentriert
        )
        title = Paragraph("Mitarbeiterbefragung - Ergebnisbericht", title_style)
        story.append(title)
        
        # Untertitel
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor(COLORS['anthrazit']),
            spaceAfter=20,
            alignment=1
        )
        subtitle = Paragraph(f"Abteilung: {st.session_state.wg_selected}", subtitle_style)
        story.append(subtitle)
        
        # Metadaten
        meta_style = ParagraphStyle(
            'MetaStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
            alignment=1,
            spaceAfter=30
        )
        meta_text = f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M')} | "
        if st.session_state.get('test_data_created', False):
            meta_text += "Testbericht mit simulierten Daten"
        else:
            meta_text += "Anonyme Befragung"
        
        story.append(Paragraph(meta_text, meta_style))
        story.append(Spacer(1, 20))
        
        # Gesamtergebnis-Box
        scores = calculate_scores()
        if scores:
            total_avg = sum(scores.values()) / len(scores)
            overall_interpretation, overall_color = get_interpretation(total_avg)
            
            # Gesamtergebnis Container
            overall_style = ParagraphStyle(
                'OverallStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.white,
                backColor=overall_color,
                borderPadding=10,
                spaceAfter=20,
                alignment=1
            )
            
            overall_text = f"<b>Gesamtergebnis: {total_avg:.2f}/5 Punkte - {overall_interpretation}</b>"
            story.append(Paragraph(overall_text, overall_style))
            story.append(Spacer(1, 10))
        
        # Legende
        legend_style = ParagraphStyle(
            'LegendStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=1,
            spaceAfter=15
        )
        legend_text = "Skala: 1 = Trifft gar nicht zu | 3 = Teils/teils | 5 = Trifft voll zu"
        story.append(Paragraph(legend_text, legend_style))
        story.append(Spacer(1, 20))
        
        # Detailtabelle mit verbesserter Visualisierung
        table_data = []
        
        # Tabellenkopf
        header_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['dark_green'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor(COLORS['light_gray'])]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]
        
        table_data.append(['Bereich', 'Themenbereich', 'Score', 'Bewertung', 'Visualisierung'])
        
        for domain in range(1, 9):
            score = scores.get(domain, 0)
            interpretation, color = get_interpretation(score)
            bar_color, percentage = create_visual_score_bar(score)
            
            # Score-Text mit Farbe
            score_text = f"{score:.2f}/5"
            
            # Visuelle Darstellung als Text-Balken
            filled_chars = int(percentage * 10)  # 10 Zeichen für den Balken
            visual_bar = "█" * filled_chars + "░" * (10 - filled_chars)
            
            table_data.append([
                f"Bereich {domain}",
                DOMAINS[domain],
                score_text,
                interpretation,
                visual_bar
            ])
            
            # Farbe für die Bewertungsspalte
            header_style.append(('BACKGROUND', (3, domain), (3, domain), color))
            header_style.append(('TEXTCOLOR', (3, domain), (3, domain), colors.white))
            header_style.append(('FONTNAME', (3, domain), (3, domain), 'Helvetica-Bold'))
            
            # Farbe für die Visualisierungsspalte
            header_style.append(('TEXTCOLOR', (4, domain), (4, domain), bar_color))
            header_style.append(('FONTNAME', (4, domain), (4, domain), 'Courier-Bold'))
        
        # Tabelle erstellen
        domain_table = Table(table_data, colWidths=[50, 180, 50, 80, 80])
        domain_table.setStyle(TableStyle(header_style))
        story.append(domain_table)
        story.append(Spacer(1, 30))
        
        # Stärken und Entwicklungsbereiche
        if scores:
            strengths = [(d, s) for d, s in scores.items() if s >= 4.0]
            weaknesses = [(d, s) for d, s in scores.items() if s < 3.0]
            
            col1, col2 = [], []
            
            # Stärken
            if strengths:
                strengths_style = ParagraphStyle(
                    'StrengthsStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.HexColor("#1E6F5C"),
                    leftIndent=10,
                    spaceAfter=5
                )
                col1.append(Paragraph("<b>✅ Stärken</b>", strengths_style))
                for domain, score in sorted(strengths, key=lambda x: x[1], reverse=True):
                    col1.append(Paragraph(f"• {DOMAINS[domain]} ({score:.2f}/5)", strengths_style))
            else:
                col1.append(Paragraph("<b>✅ Stärken</b>", strengths_style))
                col1.append(Paragraph("Keine besonderen Stärken identifiziert", strengths_style))
            
            # Entwicklungsbereiche
            if weaknesses:
                weaknesses_style = ParagraphStyle(
                    'WeaknessesStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.HexColor("#D9534F"),
                    leftIndent=10,
                    spaceAfter=5
                )
                col2.append(Paragraph("<b>📈 Entwicklungsbereiche</b>", weaknesses_style))
                for domain, score in sorted(weaknesses, key=lambda x: x[1]):
                    col2.append(Paragraph(f"• {DOMAINS[domain]} ({score:.2f}/5)", weaknesses_style))
            else:
                col2.append(Paragraph("<b>📈 Entwicklungsbereiche</b>", weaknesses_style))
                col2.append(Paragraph("Keine kritischen Bereiche", weaknesses_style))
            
            # Zwei-Spalten-Layout für Analyse
            from reportlab.platypus import KeepInFrame
            
            analysis_table_data = [
                [KeepInFrame(200, 100, col1), KeepInFrame(200, 100, col2)]
            ]
            
            analysis_table = Table(analysis_table_data, colWidths=[250, 250])
            analysis_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            story.append(Paragraph("<b>Analyse</b>", styles['Heading2']))
            story.append(Spacer(1, 10))
            story.append(analysis_table)
            story.append(Spacer(1, 20))
        
        # Interpretationstabelle
        interpretation_data = [
            ['Bewertung', 'Score-Bereich', 'Beschreibung'],
            ['Sehr gut', '4.2 - 5.0', 'Ausgezeichnete Ergebnisse, die beibehalten werden sollten'],
            ['Gut', '3.6 - 4.1', 'Positive Ergebnisse mit geringem Verbesserungspotential'],
            ['Mittel', '3.0 - 3.5', 'Akzeptable Ergebnisse mit Entwicklungsmöglichkeiten'],
            ['Verbesserungsbedarf', '1.0 - 2.9', 'Kritische Bereiche, die prioritär angegangen werden sollten']
        ]
        
        interpretation_table = Table(interpretation_data, colWidths=[80, 60, 260])
        interpretation_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['anthrazit'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (0, 1), colors.HexColor("#1E6F5C")),
            ('BACKGROUND', (0, 2), (0, 2), colors.HexColor("#2B8C69")),
            ('BACKGROUND', (0, 3), (0, 3), colors.HexColor("#E9B44C")),
            ('BACKGROUND', (0, 4), (0, 4), colors.HexColor("#D9534F")),
            ('TEXTCOLOR', (0, 1), (0, 4), colors.white),
            ('FONTNAME', (0, 1), (0, 4), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(Paragraph("<b>Interpretationshilfe</b>", styles['Heading2']))
        story.append(Spacer(1, 10))
        story.append(interpretation_table)
        
        # Fusszeile
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=1
        )
        footer = Paragraph("Dieser Bericht wurde automatisch generiert. Die Daten wurden anonym erhoben.", footer_style)
        story.append(footer)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        st.error(f"Fehler beim Erstellen des PDFs: {e}")
        return None

def render_results():
    """Zeigt die Ergebnisse und PDF-Download an - UNVERÄNDERT vom Original"""
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
