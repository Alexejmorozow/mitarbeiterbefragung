import streamlit as st
import pandas as pd
from datetime import datetime
import json
import io
import matplotlib.pyplot as plt
import numpy as np
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Flowable
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
import matplotlib
matplotlib.use('Agg')  # Für Streamlit Kompatibilität

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
    7: "Dienst- & Einsatzplaning",
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
        "Ich habe genügend Zeit, um Bewonner*innen professionell und in Ruhe zu betreuen.",
        "Ich schaffe die Dokumentation üblicherweise innerhalb der regulären Arbeitszeit."
    ],
    (1, 2): [
        "Ich kann meine Aufgaben meistens ohne häufige Unterbrechungen durchführen.",
        "Ungeplante Störungen hindern mich regelmässig an konzentrierter Arbeit."  # NEGATIV
    ],
    (1, 3): [
        "Die Aufgaben pro Schicht haben im Vergleich zum Vorjahr spürbar zugenommen.",  # NEGATIV
        "Anforderungen sind gestiegen, ohne dass Ressourcen angepasst wurden."  # NEGATIV
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

# Scoring-Mapping für positive Fragen (Standard)
SCORE_MAP_POSITIVE = {
    "Trifft voll zu": 5,
    "Trifft zu": 4,
    "Teils/teils": 3,
    "Trifft nicht zu": 2,
    "Trifft gar nicht zu": 1
}

# Scoring-Mapping für negative Fragen (umgekehrt)
SCORE_MAP_NEGATIVE = {
    "Trifft voll zu": 1,
    "Trifft zu": 2,
    "Teils/teils": 3,
    "Trifft nicht zu": 4,
    "Trifft gar nicht zu": 5
}

# Definition welche Fragen negativ sind (umgekehrte Skala)
# Format: (Domain, Subdomain): [Fragen-Indizes die negativ sind]
NEGATIVE_QUESTIONS = {
    (1, 2): [1],  # "Ungeplante Störungen hindern mich..."
    (1, 3): [0, 1],  # Beide Fragen in Arbeitsverdichtung sind negativ
    # Weitere negative Fragen können hier hinzugefügt werden
}

def get_score_for_question(domain, subdomain, question_index, answer):
    """Gibt den korrekten Score für eine Frage zurück (berücksichtigt negative Formulierungen)"""
    if (domain, subdomain) in NEGATIVE_QUESTIONS:
        if question_index in NEGATIVE_QUESTIONS[(domain, subdomain)]:
            return SCORE_MAP_NEGATIVE.get(answer, 3)  # Fallback: 3 Punkte
    return SCORE_MAP_POSITIVE.get(answer, 3)  # Standard: positive Skala

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

def get_interpretation_compact(score):
    """Gibt kompakte Interpretation zurück"""
    if score >= 4.2:
        return "Sehr gut"
    elif score >= 3.6:
        return "Gut"
    elif score >= 3.0:
        return "Mittel"
    else:
        return "Verb.Bedarf"

def pick_color_hex(score):
    """Gibt die Farbe für einen Score zurück"""
    if score >= 4.2:
        return "#1E6F5C"
    elif score >= 3.6:
        return "#2B8C69"
    elif score >= 3.0:
        return "#E9B44C"
    else:
        return "#D9534F"

def get_color_for_score(score):
    """Gibt Farbe für Score zurück"""
    if score >= 4.2:
        return colors.HexColor("#1E6F5C")  # Dunkelgrün
    elif score >= 3.6:
        return colors.HexColor("#2B8C69")  # Mittelgrün
    elif score >= 3.0:
        return colors.HexColor("#E9B44C")  # Gelb/Orange
    else:
        return colors.HexColor("#D9534F")  # Rot

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
            # Variierende Testdaten für realistischeres Radar-Diagramm
            answers = ["Trifft voll zu", "Trifft zu", "Teils/teils", "Trifft nicht zu", "Trifft gar nicht zu"]
            test_answers[(domain, subdomain)] = [
                answers[domain % 5],
                answers[(domain + 2) % 5]
            ]
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
        
        # Hinweis für negative Fragen
        is_negative = (domain, subdomain) in NEGATIVE_QUESTIONS and i in NEGATIVE_QUESTIONS[(domain, subdomain)]
        if is_negative:
            st.caption("🔄 Diese Frage ist negativ formuliert - 'Trifft voll zu' bedeutet hier eine schlechte Situation")
        
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
    """Berechnet die Scores aus den Antworten mit korrekter Behandlung negativer Fragen"""
    domain_scores = {}
    
    for (domain, subdomain), answers in st.session_state.answers.items():
        if domain not in domain_scores:
            domain_scores[domain] = []
        
        for i, answer in enumerate(answers):
            score = get_score_for_question(domain, subdomain, i, answer)
            domain_scores[domain].append(score)
    
    avg_scores = {}
    for domain, scores in domain_scores.items():
        if scores:
            avg_scores[domain] = sum(scores) / len(scores)
    
    return avg_scores

def calculate_scores_from_answers(answers):
    """Berechnet Scores aus Antworten (für PDF) mit negativen Fragen"""
    domain_scores = {}
    for (d, sd), resp in answers.items():
        scores = []
        for i, answer in enumerate(resp):
            score = get_score_for_question(d, sd, i, answer)
            scores.append(score)
        
        if scores:
            domain_scores.setdefault(d, []).extend(scores)
    
    avg = {d: (sum(vals)/len(vals)) for d, vals in domain_scores.items()}
    # ensure all domains present
    for d in DOMAINS.keys():
        avg.setdefault(d, 0.0)
    return avg

def get_subdomain_avg(answers, d, sd):
    """Berechnet Durchschnitt für Subdomain"""
    v = answers.get((d, sd))
    if not v:
        return None
    scores = []
    for i, answer in enumerate(v):
        score = get_score_for_question(d, sd, i, answer)
        scores.append(score)
    return (sum(scores)/len(scores)) if scores else None

def create_radar_chart(scores):
    """Erstellt ein Radar-Diagramm für die PDF"""
    # Daten vorbereiten
    categories = list(DOMAINS.values())
    values = [scores.get(i, 0) for i in range(1, 9)]
    
    # Anzahl Kategorien
    N = len(categories)
    
    # Winkel für jede Achse
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Schliesse den Kreis
    
    # Werte für den Plot (Kreis schliessen)
    values += values[:1]
    
    # Plot erstellen
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # Radar plotten
    ax.plot(angles, values, 'o-', linewidth=2, label='Bewertung', color=COLORS['dark_green'])
    ax.fill(angles, values, alpha=0.25, color=COLORS['mint'])
    
    # Achsen anpassen
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    # Kategorien hinzufügen
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=9)
    
    # Y-Achse anpassen
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'], fontsize=8)
    ax.grid(True)
    
    # Titel
    plt.title('Mitarbeiterbefragung - Profil der Arbeitsbereiche', 
              size=14, color=COLORS['anthrazit'], pad=20)
    
    # Diagramm als Bild speichern
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    img_buffer.seek(0)
    return img_buffer

# ---- OPTIMIERTE 1-SEITEN PDF-FUNKTION ----
def create_compact_pdf_report(answers, wg_selected, test_data_created=False):
    """
    Erstellt einen extrem kompakten 1-seitigen PDF-Report für die Mitarbeiterbefragung
    """
    
    # Berechne Scores
    domain_scores = calculate_scores_from_answers(answers)
    overall_score = sum(domain_scores.values()) / len(domain_scores) if domain_scores else 0.0
    
    # Buffer für PDF
    buffer = io.BytesIO()
    
    # Dokument mit optimierten Rändern
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=12*mm,
        leftMargin=12*mm,
        topMargin=10*mm,
        bottomMargin=10*mm
    )
    
    # Styles definieren
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CompactTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        spaceAfter=6,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name='CompactHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        spaceAfter=3
    ))
    
    story = []
    
    # KOMPLETT AUF EINER SEITE
    # ========================
    
    # Titel und Metadaten
    story.append(Paragraph("MITARBEITERBEFRAGUNG - HAUSVERBUND A", styles['CompactTitle']))
    story.append(Spacer(1, 3*mm))
    
    # Metadaten kompakt
    meta_data = [
        [f"Abteilung: {wg_selected}", f"Datum: {datetime.now().strftime('%d.%m.%Y')}"],
        ["Testdaten" if test_data_created else "Anonyme Befragung", ""]
    ]
    
    meta_table = Table(meta_data, colWidths=[85*mm, 85*mm])
    meta_table.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'Helvetica', 7),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 4*mm))
    
    # Gesamtindex kompakt
    overall_interpretation = get_interpretation_compact(overall_score)
    overall_data = [
        ["GESAMTINDEX", f"{overall_score:.2f}/5.0", overall_interpretation]
    ]
    
    overall_table = Table(overall_data, colWidths=[80*mm, 40*mm, 50*mm])
    overall_table.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'Helvetica-Bold', 10),
        ('BACKGROUND', (0,0), (-1,-1), get_color_for_score(overall_score)),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(overall_table)
    story.append(Spacer(1, 4*mm))
    
    # Domänen Übersichtstabelle - kompakter
    domains_header = ["BEREICH", "SCORE", "BEWERTUNG"]
    domains_data = [domains_header]
    
    for domain in range(1, 9):
        score = domain_scores.get(domain, 0.0)
        interpretation = get_interpretation_compact(score)
        # Kürze lange Domain-Namen
        domain_name = DOMAINS[domain]
        if len(domain_name) > 35:
            domain_name = domain_name[:32] + "..."
        domains_data.append([
            domain_name,
            f"{score:.2f}",
            interpretation
        ])
    
    domains_table = Table(domains_data, colWidths=[95*mm, 25*mm, 40*mm])
    domains_table.setStyle(TableStyle([
        # Header
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 8),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2F4F4F")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 3),
        ('TOPPADDING', (0,0), (-1,0), 2),
        # Daten
        ('FONT', (0,1), (-1,-1), 'Helvetica', 7),
        ('ALIGN', (0,1), (-1,-1), 'LEFT'),
        ('ALIGN', (1,1), (1,-1), 'CENTER'),
        ('ALIGN', (2,1), (2,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,1), (-1,-1), 1),
        ('BOTTOMPADDING', (0,1), (-1,-1), 1),
    ]))
    
    # Bedingte Formatierung für Bewertungsspalte
    for i in range(1, len(domains_data)):
        score = float(domains_data[i][1])
        domains_table.setStyle(TableStyle([
            ('BACKGROUND', (2,i), (2,i), get_color_for_score(score)),
            ('TEXTCOLOR', (2,i), (2,i), colors.white),
            ('FONT', (2,i), (2,i), 'Helvetica-Bold', 7),
        ]))
    
    story.append(domains_table)
    story.append(Spacer(1, 3*mm))
    
    # Kompakte Legende
    legend_data = [
        ["LEGENDE:", "4.2-5.0 Sehr gut", "3.6-4.1 Gut", "3.0-3.5 Mittel", "<3.0 Verb.Bedarf"]
    ]
    
    legend_table = Table(legend_data, colWidths=[18*mm, 30*mm, 25*mm, 25*mm, 32*mm])
    legend_table.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'Helvetica', 6),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0F0F0")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ]))
    story.append(legend_table)
    
    # Trennlinie vor Detailübersicht
    story.append(Spacer(1, 3*mm))
    story.append(HRDivider(width=160))
    story.append(Spacer(1, 3*mm))
    
    # Detailübersicht - Subthemen Matrix
    story.append(Paragraph("DETAILÜBERSICHT - ALLE SUBTHEMEN", styles['CompactHeader']))
    story.append(Spacer(1, 2*mm))
    
    # Subthemen Matrix Header
    subthemen_header = ["BEREICH", "1", "2", "3", "4"]
    subthemen_data = [subthemen_header]
    
    # Daten für alle Domänen und Subdomänen
    for domain in range(1, 9):
        # Kürze Bereichsnamen weiter für Detailtabelle
        domain_name = DOMAINS[domain]
        if len(domain_name) > 25:
            domain_name = domain_name[:23] + "..."
        domain_row = [domain_name]
        
        for subdomain in range(1, 5):
            score = get_subdomain_avg(answers, domain, subdomain)
            domain_row.append(f"{score:.1f}" if score is not None else "–")
        
        subthemen_data.append(domain_row)
    
    # Subthemen Tabelle - extrem kompakt
    subthemen_table = Table(subthemen_data, colWidths=[70*mm, 20*mm, 20*mm, 20*mm, 20*mm])
    
    subthemen_table.setStyle(TableStyle([
        # Header
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 7),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2F4F4F")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 2),
        ('TOPPADDING', (0,0), (-1,0), 1),
        # Bereichsnamen
        ('FONT', (0,1), (0,-1), 'Helvetica-Bold', 6),
        ('BACKGROUND', (0,1), (0,-1), colors.HexColor("#F0F0F0")),
        ('ALIGN', (0,1), (0,-1), 'LEFT'),
        ('LEFTPADDING', (0,1), (0,-1), 1),
        # Score-Zellen
        ('FONT', (1,1), (-1,-1), 'Helvetica', 6),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        # Grid
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('ROWBACKGROUNDS', (1,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")]),
        ('TOPPADDING', (0,1), (-1,-1), 0.5),
        ('BOTTOMPADDING', (0,1), (-1,-1), 0.5),
    ]))
    
    # Farbformatierung für Score-Zellen
    for row in range(1, len(subthemen_data)):
        for col in range(1, 5):
            score_str = subthemen_data[row][col]
            if score_str != '–':
                score = float(score_str)
                subthemen_table.setStyle(TableStyle([
                    ('BACKGROUND', (col, row), (col, row), get_color_for_score(score)),
                    ('TEXTCOLOR', (col, row), (col, row), colors.white),
                    ('FONT', (col, row), (col, row), 'Helvetica-Bold', 6),
                ]))
    
    story.append(subthemen_table)
    story.append(Spacer(1, 2*mm))
    
    # Ultra-kompakte Legende
    story.append(Paragraph("Subthemen-Legende (1-4 pro Bereich):", styles['CompactHeader']))
    
    # Noch kompaktere Legende - nur die Nummern mit extrem kurzen Beschreibungen
    legende_data = []
    for domain in range(1, 9):
        row = [f"{domain}."]
        for subdomain in range(1, 5):
            sub_name = SUBDOMAINS[domain][subdomain]
            # Extrem kurze Namen
            short_name = ""
            words = sub_name.split()
            if words:
                # Nimm nur das erste Wort oder kürze stark
                short_name = words[0][:8]
            row.append(short_name)
        legende_data.append(row)
    
    legende_table = Table(legende_data, colWidths=[8*mm, 38*mm, 38*mm, 38*mm, 38*mm])
    legende_table.setStyle(TableStyle([
        ('FONT', (0,0), (-1,-1), 'Helvetica', 5),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8F9FA")),
        ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor("#DDDDDD")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 0.3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0.3),
    ]))
    
    story.append(legende_table)
    
    # PDF erstellen
    doc.build(story)
    buffer.seek(0)
    return buffer

# ---- ENTFERNT: Ausführlicher PDF-Report ----

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
    
    # Radar Chart in Streamlit anzeigen
    st.subheader("📊 Profilübersicht - Radar-Diagramm")
    
    # Daten für das Radar-Diagramm
    categories = list(DOMAINS.values())
    values = [scores.get(i, 0) for i in range(1, 9)]
    
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))
    
    # Anzahl Kategorien und Winkel
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    values += values[:1]
    
    # Plot
    ax.plot(angles, values, 'o-', linewidth=2, label='Bewertung', color=COLORS['dark_green'])
    ax.fill(angles, values, alpha=0.25, color=COLORS['mint'])
    
    # Achsen anpassen
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'])
    ax.grid(True)
    ax.set_title('Profil der Arbeitsbereiche', size=14, pad=20)
    
    st.pyplot(fig)
    plt.close()
    
    # Detailtabelle
    st.subheader("📋 Detaillierte Auswertung")
    
    for domain in range(1, 9):
        score = scores.get(domain, 0)
        interpretation, color = get_interpretation(score)
        st.write(f"**{DOMAINS[domain]}:** {score:.2f}/5 Punkte - *{interpretation}*")
        st.progress(score / 5)
    
    # PDF Download mit Anleitung
    st.subheader("📄 PDF Bericht herunterladen")
    
    # Wichtiger Hinweis
    st.info("""
    **📋 So geht's weiter:**
    1. **Lade jetzt den PDF Bericht herunter** (Button unten)
    2. **Drucke ihn aus** 
    3. **Lege ihn deiner/m Vorgesetzten in ihr Fach**
    
    Der Bericht enthält alle wichtigen Ergebnisse auf einer Seite - perfekt für den schnellen Überblick!
    """)
    
    # PDF Download Button
    try:
        pdf_buffer = create_compact_pdf_report(
            st.session_state.answers,
            st.session_state.wg_selected,
            st.session_state.get('test_data_created', False)
        )
        
        st.download_button(
            label="📄 PDF Bericht herunterladen (1 Seite)",
            data=pdf_buffer,
            file_name=f"Befragung_{st.session_state.wg_selected}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
        
        st.caption("✅ Extrem kompakter 1-Seiten-Report - ideal für Vorgesetzte")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Erstellen des PDFs: {str(e)}")
        st.info("Bitte versuche es erneut oder kontaktiere den Administrator.")
    
    # Neue Befragung starten
    st.write("---")
    st.subheader("Neue Befragung starten")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Neue Test-Befragung", use_container_width=True):
            st.session_state.answers = create_test_data()
            st.session_state.test_data_created = True
            st.rerun()
    
    with col2:
        if st.button("🏠 Neue echte Befragung", use_container_width=True):
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
