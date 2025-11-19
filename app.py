import streamlit as st
import pandas as pd
from datetime import datetime
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

# Konfiguration
WG_OPTIONS = [
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
        "Ungeplante Störungen hindern mich regelmäßig an konzentrierter Arbeit."
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
        "Jeder weiß, was zu tun ist."
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
        "Es existieren klare SOPs und Checklisten.",
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

def initialize_session():
    """Initialisiert die Session State Variablen"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'wg_selection'
    if 'wg_selected' not in st.session_state:
        st.session_state.wg_selected = None
    if 'answers' not in st.session_state:
        st.session_state.answers = {}

def render_wg_selection():
    """WG Auswahl Schritt"""
    st.title("🏠 Mitarbeiterbefragung")
    st.subheader("Bitte wählen Sie Ihre Wohngruppe aus")
    
    selected_wg = st.selectbox(
        "Wohngruppe:",
        WG_OPTIONS,
        key="wg_select"
    )
    
    st.info("💡 Die Befragung ist komplett anonym. Ihre Antworten können nicht Ihnen persönlich zugeordnet werden.")
    
    if st.button("Befragung starten"):
        st.session_state.wg_selected = selected_wg
        st.session_state.current_step = 'survey'
        st.rerun()

def render_survey():
    """Haupt-Befragung mit allen Fragen"""
    st.title("📝 Mitarbeiterbefragung")
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
    
    # Frage anzeigen
    st.subheader(f"Domäne {domain}: {DOMAINS[domain]}")
    st.write(f"**{SUBDOMAINS[domain][subdomain]}**")
    
    answers = []
    for i, question in enumerate(questions):
        st.write(f"**{question}**")
        answer = st.radio(
            f"Antwort:",
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
                # Antworten speichern
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
    """Erstellt einen PDF-Report mit den Ergebnissen"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Titel
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Mitarbeiterbefragung - Ergebnisbericht")
    
    # Metadaten
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Wohngruppe: {st.session_state.wg_selected}")
    c.drawString(50, height - 100, f"Datum: {datetime.now().strftime('%d.%m.%Y')}")
    c.drawString(50, height - 120, "Hinweis: Diese Befragung wurde anonym durchgeführt.")
    
    # Ergebnisse
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 160, "Ergebnisse nach Domänen:")
    
    y_position = height - 190
    scores = calculate_scores()
    
    for domain in range(1, 9):
        if y_position < 100:
            c.showPage()
            y_position = height - 50
            c.setFont("Helvetica", 10)
        
        domain_name = DOMAINS[domain]
        score = scores.get(domain, 0)
        
        c.drawString(70, y_position, f"Domäne {domain}: {domain_name}")
        c.drawString(400, y_position, f"{score:.2f}/5")
        
        # Visualisierung
        bar_width = 200
        bar_height = 8
        fill_width = (score / 5) * bar_width
        c.rect(200, y_position - 5, bar_width, bar_height)
        c.rect(200, y_position - 5, fill_width, bar_height, fill=1)
        
        y_position -= 25
    
    # Gesamtscore
    if scores:
        total_avg = sum(scores.values()) / len(scores) if scores else 0
        c.setFont("Helvetica-Bold", 12)
        c.drawString(70, y_position - 30, f"Gesamtdurchschnitt: {total_avg:.2f}/5")
    
    c.save()
    buffer.seek(0)
    return buffer

def render_results():
    """Zeigt die Ergebnisse und PDF-Download an"""
    st.title("✅ Befragung abgeschlossen!")
    st.success("Vielen Dank für Ihre Teilnahme an der Befragung!")
    
    st.subheader("Zusammenfassung Ihrer Antworten")
    
    scores = calculate_scores()
    for domain in range(1, 9):
        score = scores.get(domain, 0)
        st.write(f"**{DOMAINS[domain]}:** {score:.2f}/5 Punkte")
        st.progress(score / 5)
    
    # PDF Download
    st.subheader("PDF-Bericht")
    st.write("Sie können hier eine Zusammenfassung Ihrer Antworten als PDF herunterladen:")
    
    pdf_buffer = create_pdf_report()
    
    st.download_button(
        label="📄 PDF Bericht herunterladen",
        data=pdf_buffer,
        file_name=f"Befragung_{st.session_state.wg_selected}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )
    
    # Neue Befragung starten
    st.write("---")
    if st.button("🏠 Neue Befragung starten"):
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
