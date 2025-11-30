

import streamlit as st
import time
import random
import numpy as np
from datetime import datetime
import io
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import json

# 🔥 ERWEITERTE KONFIGURATION MIT WAHNSINNS-OPTIONEN
WG_OPTIONS = [
    "🎪 SPEZIALANGEBOT - DER ZIRKUS BEGINNT!",
    "🤡 WG FLIEGENPILZ - CLOWN ALARM!",
    "💫 WG KRISTALL - MAGISCHE MOMENTE", 
    "🎸 WG ALPHORN - ROCKT DIE BÜHNE!",
    "🏔️ WG STEINBOCK - ABENTEUER GARANTIERT!",
    "🌄 WG ALPENBLICK - AUSSICHTEN DELUXE!"
]

# 🔥 FLIEGENDE BUTTONS IMPLEMENTIEREN
def apply_insane_styles():
    """STYLES FÜR DAS VOLLKOMMENE CHAOS"""
    st.markdown(f"""
    <style>
    /* 🌈 WAHNSINNS-HINTERGRUND */
    .stApp {{
        background: linear-gradient(
            45deg,
            #ff0000, #ff8000, #ffff00, #80ff00,
            #00ff00, #00ff80, #00ffff, #0080ff,
            #0000ff, #8000ff, #ff00ff, #ff0080
        );
        background-size: 1200% 1200%;
        animation: rainbow 8s ease infinite;
    }}
    
    @keyframes rainbow {{
        0% {{ background-position: 0% 50% }}
        50% {{ background-position: 100% 50% }}
        100% {{ background-position: 0% 50% }}
    }}
    
    /* 🚀 FLIEGENDE BUTTONS - DAS HAUPTPROBLEM! */
    .stButton>button {{
        position: relative;
        transition: all 0.1s ease !important;
        background: linear-gradient(45deg, #FF0000, #FF00FF, #0000FF) !important;
        color: white !important;
        border: 3px dashed yellow !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        font-size: 18px !important;
        box-shadow: 0 0 20px rgba(255,255,0,0.8) !important;
        cursor: pointer !important;
    }}
    
    .stButton>button:hover {{
        animation: escape 0.5s forwards !important;
    }}
    
    @keyframes escape {{
        0% {{ 
            transform: translate(0, 0) rotate(0deg);
            opacity: 1;
        }}
        25% {{
            transform: translate(100px, -50px) rotate(90deg);
        }}
        50% {{
            transform: translate(-150px, 80px) rotate(180deg);
        }}
        75% {{
            transform: translate(200px, 120px) rotate(270deg);
        }}
        100% {{
            transform: translate(300px, -200px) rotate(360deg);
            opacity: 0;
        }}
    }}
    
    /* 🎯 BUTTONS DIE SICH BEWEGEN BEVOR MAN SIE ANKLICKT */
    .stButton>button:not(:hover) {{
        animation: floatAround 8s infinite ease-in-out !important;
    }}
    
    @keyframes floatAround {{
        0% {{ transform: translate(0, 0) rotate(0deg); }}
        25% {{ transform: translate(20px, 15px) rotate(5deg); }}
        50% {{ transform: translate(-15px, 25px) rotate(-5deg); }}
        75% {{ transform: translate(25px, -10px) rotate(3deg); }}
        100% {{ transform: translate(0, 0) rotate(0deg); }}
    }}
    
    /* 💫 RADIO BUTTONS DIE WEGLAUFEN */
    .stRadio > div {{
        position: relative;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #ff00cc, #3333ff) !important;
        border: 2px solid #00ff00 !important;
        border-radius: 15px !important;
        margin: 10px 0 !important;
        padding: 15px !important;
        animation: pulseGlow 3s infinite !important;
    }}
    
    .stRadio > div:hover {{
        animation: radioEscape 0.8s forwards !important;
    }}
    
    @keyframes radioEscape {{
        0% {{ 
            transform: translateX(0) scale(1);
            opacity: 1;
        }}
        50% {{
            transform: translateX(400px) scale(1.2);
            opacity: 0.7;
        }}
        100% {{
            transform: translateX(800px) scale(0.5);
            opacity: 0;
        }}
    }}
    
    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 0 10px #00ff00; }}
        33% {{ box-shadow: 0 0 30px #ff00ff; }}
        66% {{ box-shadow: 0 0 20px #ffff00; }}
        100% {{ box-shadow: 0 0 10px #00ff00; }}
    }}
    
    /* 🎪 WIGGLE ANIMATION FÜR ALLES */
    @keyframes crazyWiggle {{
        0%, 7% {{ transform: rotateZ(0); }}
        15% {{ transform: rotateZ(-15deg); }}
        20% {{ transform: rotateZ(10deg); }}
        25% {{ transform: rotateZ(-10deg); }}
        30% {{ transform: rotateZ(6deg); }}
        35% {{ transform: rotateZ(-4deg); }}
        40%, 100% {{ transform: rotateZ(0); }}
    }}
    
    /* ✨ FLIEGENDE EMOJIS IM HINTERGRUND */
    .floating-emoji {{
        position: fixed;
        font-size: 30px;
        z-index: 9999;
        pointer-events: none;
        animation: floatRandom 15s linear infinite;
    }}
    
    @keyframes floatRandom {{
        0% {{
            transform: translate(0, 100vh) rotate(0deg);
            opacity: 1;
        }}
        100% {{
            transform: translate(calc(100vw * var(--random-x)), -100px) rotate(360deg);
            opacity: 0;
        }}
    }}
    
    /* 💥 EXPLODIERENDE TEXTE */
    .exploding-text {{
        animation: textExplosion 2s infinite;
        color: #ffff00 !important;
        text-shadow: 0 0 10px #ff0000, 0 0 20px #ff00ff;
        font-weight: bold;
    }}
    
    @keyframes textExplosion {{
        0% {{ 
            transform: scale(1);
            text-shadow: 0 0 10px #ff0000;
        }}
        50% {{ 
            transform: scale(1.3);
            text-shadow: 0 0 30px #ffff00, 0 0 40px #ff00ff;
        }}
        100% {{ 
            transform: scale(1);
            text-shadow: 0 0 10px #ff0000;
        }}
    }}
    
    /* 🎰 SELECTBOX CHAOS */
    .stSelectbox > div > div {{
        background: linear-gradient(45deg, #00ff00, #ff00ff) !important;
        border: 3px dotted yellow !important;
        border-radius: 10px !important;
        animation: selectDance 4s infinite !important;
    }}
    
    @keyframes selectDance {{
        0% {{ transform: translateX(0px) rotate(0deg); }}
        25% {{ transform: translateX(10px) rotate(2deg); }}
        50% {{ transform: translateX(-10px) rotate(-2deg); }}
        75% {{ transform: translateX(5px) rotate(1deg); }}
        100% {{ transform: translateX(0px) rotate(0deg); }}
    }}
    </style>
    
    <script>
    // 🎭 EMOJI REGEN ERZEUGEN
    function createEmojiRain() {{
        const emojis = ['🚀', '💥', '🎪', '🌈', '🔥', '⭐', '🎭', '💃', '🤡', '👻', '🎃', '🦄', '🐲', '🌪️'];
        const container = document.createElement('div');
        container.style.position = 'fixed';
        container.style.top = '0';
        container.style.left = '0';
        container.style.width = '100%';
        container.style.height = '100%';
        container.style.pointerEvents = 'none';
        container.style.zIndex = '9998';
        document.body.appendChild(container);
        
        setInterval(() => {{
            if(Math.random() > 0.7) {{
                const emoji = document.createElement('div');
                emoji.className = 'floating-emoji';
                emoji.innerHTML = emojis[Math.floor(Math.random() * emojis.length)];
                emoji.style.left = Math.random() * 100 + 'vw';
                emoji.style.setProperty('--random-x', Math.random());
                emoji.style.animationDuration = (10 + Math.random() * 20) + 's';
                emoji.style.fontSize = (20 + Math.random() * 40) + 'px';
                container.appendChild(emoji);
                
                // Emoji nach Animation entfernen
                setTimeout(() => {{
                    if(emoji.parentNode) {{
                        emoji.parentNode.removeChild(emoji);
                    }}
                }}, 25000);
            }}
        }}, 500);
    }}
    
    // 🎪 BUTTON ESCAPE HELPER
    function makeButtonsEscape() {{
        const buttons = document.querySelectorAll('.stButton button');
        buttons.forEach(button => {{
            button.addEventListener('mouseenter', function(e) {{
                // Zufällige Escape-Richtung
                if(Math.random() > 0.3) {{
                    this.style.animation = 'escape 0.5s forwards';
                    // Nach dem Entfliehen neuen Button erstellen
                    setTimeout(() => {{
                        if(this.parentNode) {{
                            this.parentNode.removeChild(this);
                        }}
                    }}, 500);
                }}
            }});
        }});
    }}
    
    // 🚀 INITIALISIERE DEN WAHNSINN
    setTimeout(() => {{
        createEmojiRain();
        setInterval(makeButtonsEscape, 1000);
    }}, 1000);
    
    // 💫 ZUFÄLLIGE SEITEN-SCHÜTTELN
    setInterval(() => {{
        if(Math.random() > 0.8) {{
            document.body.style.animation = 'shake 0.5s';
            setTimeout(() => {{
                document.body.style.animation = '';
            }}, 500);
        }}
    }}, 3000);
    </script>
    
    <style>
    @keyframes shake {{
        0% {{ transform: translate(1px, 1px) rotate(0deg); }}
        10% {{ transform: translate(-1px, -2px) rotate(-1deg); }}
        20% {{ transform: translate(-3px, 0px) rotate(1deg); }}
        30% {{ transform: translate(3px, 2px) rotate(0deg); }}
        40% {{ transform: translate(1px, -1px) rotate(1deg); }}
        50% {{ transform: translate(-1px, 2px) rotate(-1deg); }}
        60% {{ transform: translate(-3px, 1px) rotate(0deg); }}
        70% {{ transform: translate(3px, 1px) rotate(-1deg); }}
        80% {{ transform: translate(-1px, -1px) rotate(1deg); }}
        90% {{ transform: translate(1px, 2px) rotate(0deg); }}
        100% {{ transform: translate(1px, -2px) rotate(-1deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def render_insane_wg_selection():
    """WG AUSWAHL WIRD ZUM UNMÖGLICHEN SPIEL"""
    
    # 💥 EXPLODIERENDER HEADER
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: rgba(0,0,0,0.8); border-radius: 20px; border: 5px dotted #ff00ff;'>
        <h1 class='exploding-text'>🎪 WILLKOMMEN BEI DER UNMÖGLICHEN BEFRAGUNG! 🎪</h1>
        <h3 style='color: #00ff00; animation: pulseGlow 2s infinite;'>
            ⚠️ WARNUNG: BUTTONS KÖNNEN FLIEGEN! ⚠️
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 🎰 CHAOTISCHE AUSWAHL
    st.markdown("""
    <div style='background: rgba(255,255,255,0.9); padding: 20px; border-radius: 15px; margin: 20px 0; border: 3px dashed red;'>
        <h2 style='color: #ff00ff; text-align: center; animation: crazyWiggle 4s infinite;'>
            🎰 WÄHLE DEINE ABTEILUNG (WENN DU KANNST!) 🎰
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 🔥 SELECTBOX MIT EIGENEM WILLEN
    selected_wg = st.selectbox(
        "👇 VERSUCHE MICH ZU KLICKEN! ICH BEWEGE MICH! 👇",
        WG_OPTIONS,
        key="insane_wg_select"
    )
    
    # 🚀 BUTTONS DIE WEGFLIEGEN
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        # ERSTER VERSUCHS-BUTTON
        if st.button("🎯 STARTE BEFRAGUNG (Versuch 1)", key="button_attempt_1"):
            st.success("😱 UNGLAUBLICH! Du hast mich erwischt!")
            time.sleep(1)
            st.session_state.wg_selected = selected_wg
            st.session_state.current_step = 'survey'
            st.rerun()
        
        # ZWEITER BUTTON FÜR DEN FALL DER FÄLLE
        if st.button("🚀 STARTE BEFRAGUNG (Versuch 2)", key="button_attempt_2"):
            st.balloons()
            st.success("🎉 WAHNSINN! ZWEITER TREFFER!")
            time.sleep(1)
            st.session_state.wg_selected = selected_wg
            st.session_state.current_step = 'survey'
            st.rerun()
        
        # DRITTER BUTTON - JUST IN CASE
        if st.button("💥 STARTE BEFRAGUNG (Versuch 3)", key="button_attempt_3"):
            st.snow()
            st.success("🤯 DREIFACH-TREFFER! LEGENDE!")
            time.sleep(1)
            st.session_state.wg_selected = selected_wg
            st.session_state.current_step = 'survey'
            st.rerun()

def render_insane_survey():
    """DIE BEFRAGUNG WIRD ZUR BEWÄHRUNGSPROBE"""
    
    st.markdown("""
    <div style='background: linear-gradient(45deg, #ff0000, #00ff00); padding: 15px; border-radius: 15px; margin-bottom: 20px;'>
        <h1 style='color: white; text-align: center; animation: textExplosion 1.5s infinite;'>
            🎯 BEFRAGUNG - JETZT MIT FLIEGENDEN BUTTONS! 🎯
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Hier würde der normale Survey-Code kommen, aber mit fliegenden Buttons!
    # ... (der Rest des Codes)

def main():
    """DIE ULTIMATIVE WAHNSINNS-APP"""
    st.set_page_config(
        page_title="🎪 ABSOLUT CRAZY BEFRAGUNG 🎪",
        page_icon="🤡",
        layout="wide", 
        initial_sidebar_state="collapsed"
    )
    
    apply_insane_styles()
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'wg_selection'
    if 'wg_selected' not in st.session_state:
        st.session_state.wg_selected = None
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    
    if st.session_state.current_step == 'wg_selection':
        render_insane_wg_selection()
    elif st.session_state.current_step == 'survey':
        render_insane_survey()
    else:
        st.title("🎉 GESCHAFFT! 🎉")
        st.balloons()
        st.snow()

if __name__ == "__main__":
    main()
