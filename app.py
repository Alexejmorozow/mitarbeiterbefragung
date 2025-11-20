import streamlit as st
import pandas as pd
from datetime import datetime
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import ssl

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
        "Ich habe das Gefühl, dass Ausfälle nicht ungefiltert auf mich abgewälzt werden."
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
        "Wichtige Infos gehen zwischen Früh-, Spät- und Nachtdienst nicht verloren."
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
        "Gesundheitsangebote sind vorhanden und realistisch nutzbar.",
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
        "Wochenend- und Nachtdienste sind fair verteilt.",
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
        "Ich weiß zu Schichtbeginn, was mich erwartet."
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

# Email Konfiguration - WEB.DE
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "alexejsworkflow@gmail.com",
    "sender_password": "dvunswfyuiwxamhg",
}

# Email-Adressen der Abteilungsleitungen pro Wohngruppe
WG_LEADER_EMAILS = {
    "Spezialangebot": "leiter.spezialangebot@domain.ch",
    "WG Fliegenpilz": "leiter.fliegenpilz@domain.ch", 
    "WG Kristall": "leiter.kristall@domain.ch",
    "WG Alphorn": "leiter.alphorn@domain.ch",
    "WG Steinbock": "leiter.steinbock@domain.ch",
    "WG Alpenblick": "leiter.alpenblick@domain.ch"
}

# Für den Test: Alle Emails an deine Adresse umleiten
TEST_MODE = True
TEST_EMAIL = "schwarzetanne@hotmail.com"

# Neues Farbschema: Matteres Grün, Anthrazit, Weiss
COLORS = {
    "mint": "#A8D5BA",      # Matteres Minzgrün (nicht mehr giftig)
    "anthrazit": "#2F4F4F", # Anthrazit
    "white": "#FFFFFF",     # Weiss
    "light_gray": "#F8F9FA", # Hellgrau für Hintergründe
    "dark_green": "#4A7C59", # Dunkleres Grün für Akzente
    "light_mint": "#D4EDDA"  # Sehr helles Minzgrün
}

def get_interpretation(score):
    """Gibt die Interpretation eines Scores zurück"""
    if score >= 4.2:
        return "Sehr gut", colors.HexColor("#1E6F5C")  # Dunkles Grün
    elif score >= 3.6:
        return "Gut", colors.HexColor("#2B8C69")       # Mittelgrün
    elif score >= 3.0:
        return "Mittel", colors.HexColor("#E9B44C")    # Gelb
    else:
        return "Verbesserungsbedarf", colors.HexColor("#D9534F")  # Rot

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
    """Erstellt Test-Daten für schnelles Testen der Email-Funktion"""
    # Simuliert ausgefüllte Antworten für alle Fragen
    test_answers = {}
    for domain in range(1, 9):
        for subdomain in range(1, 5):
            # Zufällige Antworten für Testzwecke
            test_answers[(domain, subdomain)] = ["Trifft zu", "Teils/teils"]
    
    return test_answers

def apply_custom_styles():
    """Wendet das benutzerdefinierte Farbschema an"""
    st.markdown(f"""
    <style>
    /* Haupt-Hintergrund */
    .stApp {{
        background-color: {COLORS['mint']};
    }}
    
    /* Container-Hintergründe anpassen */
    .main .block-container {{
        background-color: {COLORS['white']};
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 1rem;
        margin-bottom: 1rem;
    }}
    
    /* Sidebar Hintergrund */
    .css-1d391kg {{
        background-color: {COLORS['light_mint']};
    }}
    
    /* Progress Bar - Korrigiert für moderne Streamlit-Versionen */
    /* Hintergrund der Progressbar */
    [data-testid="stProgress"] > div > div > div:first-child {{
        background-color: {COLORS['light_gray']} !important;
        border-radius: 10px;
        height: 20px;
    }}

    /* Füllung */
    [data-testid="stProgress"] div[data-testid="stProgressBar"] {{
        background-color: {COLORS['dark_green']} !important;
        border-radius: 10px;
        height: 20px;
    }}
    
    /* Radio Buttons und andere Container */
    .stRadio > div {{
        background-color: {COLORS['dark_green']};
        color: {COLORS['white']};
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid {COLORS['mint']};
    }}
    
    /* Radio Button Labels - Weiss */
    .stRadio label {{
        color: {COLORS['white']} !important;
        font-weight: 500;
    }}
    
    /* Radio Button Punkte */
    .stRadio [data-testid="stMarkdownContainer"] p {{
        color: {COLORS['white']} !important;
    }}
    
    /* Selectbox */
    .stSelectbox > div > div {{
        background-color: {COLORS['white']};
        border: 1px solid {COLORS['anthrazit']};
        border-radius: 6px;
    }}
    
    /* Buttons */
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
    
    /* Hauptfarben */
    .main-header {{
        color: {COLORS['anthrazit']};
        border-bottom: 2px solid {COLORS['dark_green']};
        padding-bottom: 10px;
    }}
    
    /* Erfolgsmeldung - Dunkelgrün mit weisser Schrift */
    .stSuccess {{
        background-color: {COLORS['dark_green']} !important;
        color: {COLORS['white']} !important;
        border: 1px solid {COLORS['dark_green']};
        border-radius: 8px;
        padding: 15px;
    }}
    
    /* Info Box - Dunkelgrün mit weisser Schrift */
    .stInfo {{
        background-color: {COLORS['dark_green']} !important;
        color: {COLORS['white']} !important;
        border: 1px solid {COLORS['dark_green']};
        border-radius: 8px;
        border-left: 4px solid {COLORS['mint']};
        padding: 15px;
    }}
    
    /* Warning Box - Dunkelgrün mit weisser Schrift */
    .stWarning {{
        background-color: {COLORS['dark_green']} !important;
        color: {COLORS['white']} !important;
        border: 1px solid {COLORS['dark_green']};
        border-radius: 8px;
        padding: 15px;
    }}
    
    /* Error Box - Rot für Fehler beibehalten */
    .stError {{
        background-color: #D9534F;
        color: {COLORS['white']} !important;
        border: 1px solid #D9534F;
        border-radius: 8px;
        padding: 15px;
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {COLORS['dark_green']};
        color: {COLORS['white']} !important;
        border: 1px solid {COLORS['mint']};
        border-radius: 8px;
    }}
    
    /* Expander Content */
    .streamlit-expanderContent {{
        background-color: {COLORS['light_gray']};
        border-radius: 0 0 8px 8px;
    }}
    
    /* Icons in den Boxen weiss färben */
    .stSuccess svg, .stInfo svg, .stWarning svg {{
        fill: {COLORS['white']} !important;
        color: {COLORS['white']} !important;
    }}
    
    /* Markdown Text in den Boxen weiss färben */
    .stSuccess [data-testid="stMarkdownContainer"] p,
    .stInfo [data-testid="stMarkdownContainer"] p,
    .stWarning [data-testid="stMarkdownContainer"] p {{
        color: {COLORS['white']} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

def get_recipient_email(wg_name):
    """Gibt die Empfänger-Email basierend auf der Wohngruppe zurück"""
    if TEST_MODE:
        return TEST_EMAIL
    else:
        return WG_LEADER_EMAILS.get(wg_name, TEST_EMAIL)

def send_email_with_pdf(pdf_buffer, wg_name):
    """Sendet den PDF-Bericht per Email an die entsprechende Abteilungsleitung"""
    try:
        recipient_email = get_recipient_email(wg_name)
        
        # Email-Nachricht erstellen
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG["sender_email"]
        msg['To'] = recipient_email
        msg['Subject'] = f"Mitarbeiterbefragung Abschluss - {wg_name}"
        
        # Email-Text
        body = f"""
        Sehr geehrte Abteilungsleitung,
        
        soeben wurde eine Mitarbeiterbefragung für Ihre Wohngruppe abgeschlossen.
        
        Details:
        - Wohngruppe: {wg_name}
        - Datum: {datetime.now().strftime('%d.%m.%Y %H:%M')}
        - Diese Email wurde automatisch generiert.
        
        Der ausgefüllte Fragebogen ist als PDF angehängt. Die Ergebnisse können zur weiteren Analyse und für Massnahmenplanungen verwendet werden.
        
        Mit freundlichen Grüßen
        Ihr Befragungssystem Hausverbund A
        """
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # PDF als Attachment
        pdf_attachment = MIMEBase('application', 'octet-stream')
        pdf_buffer.seek(0)
        pdf_attachment.set_payload(pdf_buffer.read())
        encoders.encode_base64(pdf_attachment)
        pdf_attachment.add_header(
            'Content-Disposition',
            f'attachment; filename="Befragung_{wg_name}_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf"'
        )
        msg.attach(pdf_attachment)
        
        # Email senden mit WEB.DE
        context = ssl.create_default_context()
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls(context=context)
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
            server.send_message(msg)
            
        return True, f"Email erfolgreich an {recipient_email} versendet!"
        
    except Exception as e:
        return False, f"Fehler beim Senden der Email: {str(e)}"

def render_wg_selection():
    """WG Auswahl Schritt mit Test-Button"""
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
    
    # TEST-BUTTON FÜR SCHNELLEN EMAIL-TEST
    st.write("---")
    st.subheader("🛠️ Entwickler-Testbereich")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Schnelltest: Email-Funktion prüfen", type="secondary"):
            # Test-Daten erstellen und direkt zur Ergebnis-Seite springen
            st.session_state.answers = create_test_data()
            st.session_state.wg_selected = "WG Fliegenpilz"  # Beispiel-WG
            st.session_state.current_step = 'results'
            st.session_state.test_data_created = True
            st.rerun()
    
    with col2:
        if st.button("📋 Normale Befragung starten", type="primary"):
            st.session_state.current_step = 'survey'
            st.rerun()
    
    if st.session_state.get('test_data_created', False):
        st.success("✅ Test-Daten wurden erstellt! Du wirst zur Ergebnis-Seite weitergeleitet...")
    
    st.subheader("Bitte wähle deine Wohngruppe aus")
    
    selected_wg = st.selectbox(
        "Wohngruppe:",
        WG_OPTIONS,
        key="wg_select"
    )
    
    st.info("💡 Die Befragung ist komplett anonym. Deine Antworten können nicht dir persönlich zugeordnet werden.")
    
    if st.button("Befragung starten"):
        st.session_state.wg_selected = selected_wg
        st.session_state.current_step = 'survey'
        st.rerun()

def render_survey():
    """Haupt-Befragung mit allen Fragen - OHNE Domänen-Namen"""
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("📝 Mitarbeiterbefragung")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write(f"**Wohngruppe:** {st.session_state.wg_selected}")
    
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
        # Alle Fragen beantwortet
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
    
    # Frage anzeigen - OHNE Domänen-Informationen
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
        if st.session_state.answers:  # Nur zurück wenn schon Antworten existieren
            if st.button("← Zurück"):
                # Letzte Antwort entfernen um zurückzugehen
                last_key = list(st.session_state.answers.keys())[-1]
                del st.session_state.answers[last_key]
                st.rerun()
    
    with col2:
        all_answered = all(answers) and len(answers) > 0
        if all_answered:
            if st.button("Weiter →"):
                # Antworten speichern (mit Domänen-Info für spätere Auswertung)
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
    
    # Durchschnitt pro Domäne berechnen
    avg_scores = {}
    for domain, scores in domain_scores.items():
        if scores:
            avg_scores[domain] = sum(scores) / len(scores)
    
    return avg_scores

def create_pdf_report():
    """Erstellt einen PDF-Report mit Tabellen und Interpretationen"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Titel mit neuem Farbschema
    c.setFillColor(colors.HexColor(COLORS['anthrazit']))
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 60, "Mitarbeiterbefragung - Ergebnisbericht")
    
    # Metadaten
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 90, f"Wohngruppe: {st.session_state.wg_selected}")
    c.drawString(50, height - 110, f"Datum: {datetime.now().strftime('%d.%m.%Y')}")
    
    # Hinweis für Test-Daten
    if st.session_state.get('test_data_created', False):
        c.drawString(50, height - 130, "Hinweis: Dies ist ein Testbericht mit simulierten Daten")
    else:
        c.drawString(50, height - 130, "Hinweis: Diese Befragung wurde anonym durchgeführt.")
    
    # Abstand
    y_position = height - 170
    
    # Überschrift für Ergebnisse
    c.setFillColor(colors.HexColor(COLORS['anthrazit']))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y_position, "Ergebnisse nach Themenbereichen:")
    y_position -= 40
    
    scores = calculate_scores()
    
    # Tabellendaten vorbereiten
    table_data = [['Bereich', 'Thema', 'Score', 'Interpretation']]
    
    for domain in range(1, 9):
        domain_name = DOMAINS[domain]
        score = scores.get(domain, 0)
        interpretation, color = get_interpretation(score)
        
        # Bereich aufteilen falls zu lang
        if len(domain_name) > 40:
            words = domain_name.split()
            domain_line1 = " ".join(words[:len(words)//2])
            domain_line2 = " ".join(words[len(words)//2:])
            table_data.append([f"Bereich {domain}", domain_line1, f"{score:.2f}/5", interpretation])
            table_data.append(["", domain_line2, "", ""])
        else:
            table_data.append([f"Bereich {domain}", domain_name, f"{score:.2f}/5", interpretation])
    
    # Tabelle erstellen
    table = Table(table_data, colWidths=[80, 220, 80, 100])
    
    # Tabellen-Stil
    table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['mint'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(COLORS['anthrazit'])),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Zellen
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        
        # Rahmen
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(COLORS['anthrazit'])),
        
        # Zeilen-Hintergrund
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
            colors.HexColor(COLORS['light_gray']), 
            colors.white
        ]),
    ]))
    
    # Interpretationen einfärben
    for i in range(1, len(table_data)):
        interpretation = table_data[i][3]
        if interpretation == "Sehr gut":
            bg_color = colors.HexColor("#1E6F5C")
            text_color = colors.white
        elif interpretation == "Gut":
            bg_color = colors.HexColor("#2B8C69") 
            text_color = colors.white
        elif interpretation == "Mittel":
            bg_color = colors.HexColor("#E9B44C")
            text_color = colors.black
        else:  # Verbesserungsbedarf
            bg_color = colors.HexColor("#D9534F")
            text_color = colors.white
            
        table.setStyle(TableStyle([
            ('BACKGROUND', (3, i), (3, i), bg_color),
            ('TEXTCOLOR', (3, i), (3, i), text_color),
            ('FONTNAME', (3, i), (3, i), 'Helvetica-Bold'),
        ]))
    
    # Tabelle zeichnen
    table.wrapOn(c, width, height)
    table.drawOn(c, 50, y_position - (len(table_data) * 20))
    
    # Gesamtscore - NUR numerisch, ohne Interpretation
    y_position_summary = y_position - (len(table_data) * 20) - 60
    
    if scores:
        total_avg = sum(scores.values()) / len(scores) if scores else 0
        
        c.setFillColor(colors.HexColor(COLORS['anthrazit']))
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y_position_summary, "Zusammenfassung:")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position_summary - 30, f"Gesamtdurchschnitt: {total_avg:.2f}/5")
        
        # Legende
        c.setFont("Helvetica", 9)
        c.drawString(50, y_position_summary - 60, "Interpretation: ≥4.2 = Sehr gut | ≥3.6 = Gut | ≥3.0 = Mittel | <3.0 = Verbesserungsbedarf")
        c.drawString(50, y_position_summary - 75, "Skala: 1 = Trifft gar nicht zu | 3 = Teils/teils | 5 = Trifft voll zu")
    
    c.save()
    buffer.seek(0)
    return buffer

def render_results():
    """Zeigt die Ergebnisse und PDF-Download/Email-Versand an"""
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("✅ Befragung abgeschlossen!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Hinweis für Test-Daten
    if st.session_state.get('test_data_created', False):
        st.warning("🛠️ **Testmodus** - Dies sind simulierte Daten für den Email-Test")
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
    
    st.subheader("Bericht versenden")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # PDF Download Button
        st.write("**PDF herunterladen:**")
        st.download_button(
            label="📄 PDF Bericht herunterladen",
            data=pdf_buffer,
            file_name=f"Befragung_{st.session_state.wg_selected}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
    
    with col2:
        # Email Versand Button
        st.write("**Per Email senden:**")
        
        # Anzeige, an wen gesendet wird
        recipient_email = get_recipient_email(st.session_state.wg_selected)
        st.info(f"📧 Wird gesendet an: **{recipient_email}**")
        
        if TEST_MODE:
            st.warning("🛠️ **Testmodus aktiv** - Alle Emails gehen an deine Test-Adresse")
        
        if st.button("📧 Bericht an Abteilungsleitung senden", type="primary"):
            with st.spinner("Sende Email..."):
                success, message = send_email_with_pdf(pdf_buffer, st.session_state.wg_selected)
                
                if success:
                    st.success(message)
                    # Erfolgs-Icon anzeigen
                    st.balloons()
                else:
                    st.error(message)
                    st.info("""
                    **Troubleshooting für WEB.DE:**
                    - Prüfe ob POP3/IMAP in den WEB.DE Einstellungen aktiviert ist
                    - Stelle sicher, dass du dich kürzlich im WEB.DE Webinterface eingeloggt hast
                    - Prüfe dein Passwort
                    - Die erste Email könnte im Spam-Ordner landen
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
    
    # Custom Styles anwenden
    apply_custom_styles()
    
    initialize_session()
    
    # Routing zwischen den Schritten
    if st.session_state.current_step == 'wg_selection':
        render_wg_selection()
    elif st.session_state.current_step == 'survey':
        render_survey()
    elif st.session_state.current_step == 'results':
        render_results()

if __name__ == "__main__":
    main()
