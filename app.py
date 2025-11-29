import streamlit as st
import time
import random
from streamlit.components.v1 import html

def apply_crazy_styles():
    """Jetzt wird's bunt und verrückt!"""
    st.markdown(f"""
    <style>
    /* 🔥 ANIMIERTER HINTERGRUND */
    .stApp {{
        background: linear-gradient(
            45deg,
            #ff0000, #ff8000, #ffff00, #80ff00,
            #00ff00, #00ff80, #00ffff, #0080ff,
            #0000ff, #8000ff, #ff00ff, #ff0080
        );
        background-size: 1200% 1200%;
        animation: rainbow 15s ease infinite;
    }}
    
    @keyframes rainbow {{
        0% {{ background-position: 0% 50% }}
        50% {{ background-position: 100% 50% }}
        100% {{ background-position: 0% 50% }}
    }}
    
    /* 🎪 WIGGLE ANIMATION FÜR BUTTONS */
    @keyframes wiggle {{
        0% {{ transform: rotate(0deg); }}
        25% {{ transform: rotate(5deg); }}
        50% {{ transform: rotate(-5deg); }}
        75% {{ transform: rotate(5deg); }}
        100% {{ transform: rotate(0deg); }}
    }}
    
    .stButton>button {{
        background: linear-gradient(45deg, #FF0000, #FF00FF, #0000FF) !important;
        color: white !important;
        border: 3px dashed yellow !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        font-size: 20px !important;
        animation: wiggle 2s infinite !important;
        box-shadow: 0 0 20px rgba(255,255,0,0.8) !important;
    }}
    
    /* ✨ FUNKELNDE FRAGEN */
    .stRadio > div {{
        background: linear-gradient(135deg, #ff00cc, #3333ff) !important;
        border: 2px solid #00ff00 !important;
        border-radius: 15px !important;
        margin: 10px 0 !important;
        padding: 15px !important;
        animation: pulse 3s infinite !important;
    }}
    
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 10px #00ff00; }}
        50% {{ box-shadow: 0 0 30px #ff00ff; }}
        100% {{ box-shadow: 0 0 10px #00ff00; }}
    }}
    
    /* 🚀 FLIEGENDE EMOJIS */
    .floating {{
        animation: float 6s ease-in-out infinite;
        font-size: 30px;
        position: fixed;
    }}
    
    @keyframes float {{
        0% {{ transform: translateY(0px) rotate(0deg); }}
        50% {{ transform: translateY(-20px) rotate(180deg); }}
        100% {{ transform: translateY(0px) rotate(360deg); }}
    }}
    
    /* 💥 EXPLODIERENDE TEXTE */
    @keyframes explode {{
        0% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.5); opacity: 0.7; }}
        100% {{ transform: scale(1); opacity: 1; }}
    }}
    
    .exploding-text {{
        animation: explode 2s infinite;
        color: #ffff00 !important;
        text-shadow: 0 0 10px #ff0000;
    }}
    </style>
    
    <script>
    // 🎵 SOUND EFFECTS (theoretisch)
    function playSound() {{
        // Hier würden wir Soundeffekte einbauen
        console.log("BOOM! 💥");
    }}
    
    // 🎭 RANDOM EMOJI ANIMATIONEN
    function createFloatingEmojis() {{
        const emojis = ['🚀', '💥', '🎪', '🌈', '🔥', '⭐', '🎭', '💃'];
        for(let i = 0; i < 10; i++) {{
            setTimeout(() => {{
                const emoji = document.createElement('div');
                emoji.className = 'floating';
                emoji.innerHTML = emojis[Math.floor(Math.random() * emojis.length)];
                emoji.style.left = Math.random() * 100 + 'vw';
                emoji.style.top = Math.random() * 100 + 'vh';
                document.body.appendChild(emoji);
            }}, i * 500);
        }}
    }}
    
    // Starte die Emoji-Party!
    setTimeout(createFloatingEmojis, 1000);
    </script>
    """, unsafe_allow_html=True)

def render_crazy_wg_selection():
    """WG Auswahl wird zum Erlebnis!"""
    
    # 🎪 EXPLODIERENDER HEADER
    st.markdown("""
    <div style='text-align: center;'>
        <h1 class='exploding-text'>🎪 WILLKOMMEN IM ZIRKUS DER BEFRAGUNG! 🎪</h1>
        <h3 style='color: #00ff00; text-shadow: 0 0 10px #ff00ff;'>Hausverbund A - JETZT MIT 200% MEHR ENERGY! ⚡</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 🎰 SLOT-MACHINE STYLE AUSWAHL
    st.markdown("""
    <div style='
        background: rgba(0,0,0,0.7); 
        padding: 30px; 
        border-radius: 20px; 
        border: 5px dotted #00ff00;
        margin: 20px 0;
    '>
        <h2 style='color: yellow; text-align: center;'>🎰 DREH AM GLÜCKSRAD - WÄHLE DEINE ABTEILUNG! 🎰</h2>
    </div>
    """, unsafe_allow_html=True)
    
    selected_wg = st.selectbox(
        "👇 HIER DRÜCKEN FÜR DIE WAHNSINNS-AUSWAHL 👇",
        WG_OPTIONS,
        key="crazy_wg_select"
    )
    
    # 🔥 WAHNSINNS-BUTTON
    if st.button("🎭 JETZT GEHT'S LOS - BEFRAGUNG STARTEN! 💥", use_container_width=True):
        if selected_wg:
            # Mini-Animationseffekt
            with st.spinner('🚀 Starte Countdown... 3... 2... 1... LIFT OFF!'):
                time.sleep(2)
            st.session_state.wg_selected = selected_wg
            st.session_state.current_step = 'survey'
            st.rerun()
        else:
            st.error("🚨 ALARM! Du musst eine Abteilung wählen! 🔔")

def render_crazy_survey():
    """Befragung wird zum Abenteuer!"""
    
    # 🎯 AKTUELLE DOMÄNE MIT FLASH-EFFEKT
    current_key = None
    for domain in range(1, 9):
        for subdomain in range(1, 5):
            if (domain, subdomain) not in st.session_state.answers:
                current_key = (domain, subdomain)
                break
        if current_key:
            break
    
    if current_key:
        domain, subdomain = current_key
        questions = get_questions_for_wg(domain, subdomain, st.session_state.wg_selected)
        
        # 🌟 ANIMIERTER HEADER
        st.markdown(f"""
        <div style='
            background: linear-gradient(45deg, #ff00cc, #00ff00);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        '>
            <h1 style='color: white; text-align: center; margin: 0;'>
                🎯 BEREICH {domain}: {DOMAINS[domain].upper()} 🎯
            </h1>
        </div>
        """, unsafe_allow_html=True)
        
        # 💫 ANIMIERTE FRAGEN
        for i, question in enumerate(questions):
            st.markdown(f"""
            <div style='
                background: rgba(255,255,255,0.9);
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 5px solid #{random.randint(100000, 999999)};
                animation: fadeIn 1s;
            '>
                <h4 style='color: #333;'>❓ {question}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            answer = st.radio(
                f"Antwort {i+1}:",
                options=["Trifft voll zu", "Trifft zu", "Teils/teils", "Trifft nicht zu", "Trifft gar nicht zu"],
                key=f"crazy_q_{domain}_{subdomain}_{i}",
                index=None
            )
    
    # 🎮 GAMIFIED NAVIGATION
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.answers:
            if st.button("↩️ ZURÜCK ZUM CHAOS"):
                last_key = list(st.session_state.answers.keys())[-1]
                del st.session_state.answers[last_key]
                st.rerun()
    
    with col2:
        st.write("")  # Platzhalter
    
    with col3:
        all_answered = all(answers) if 'answers' in locals() else False
        if all_answered:
            if st.button("WEITER → INS UNBEKANNTE 🚀"):
                st.session_state.answers[current_key] = answers
                # 🎉 CONFETTI EFFEKT (theoretisch)
                st.balloons()
                st.rerun()
        else:
            st.button("⏳ WARTE AUF ANTWORTEN...", disabled=True)

# 🔥 MAIN FUNKTION ANPASSEN
def main():
    """HAUPTFUNKTION - JETZT MIT EXTRA ENERGY!"""
    st.set_page_config(
        page_title="🎪 CRAZY BEFRAGUNG 🎪",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    apply_crazy_styles()
    initialize_session()
    
    if st.session_state.current_step == 'wg_selection':
        render_crazy_wg_selection()
    elif st.session_state.current_step == 'survey':
        render_crazy_survey()
    elif st.session_state.current_step == 'results':
        # Auch die Ergebnisse können wir aufpeppen!
        render_results()
