import streamlit as st
import time
import random
import numpy as np
from datetime import datetime
import io
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import json
import base64

# 🔥 MULTISENSORISCHES CHAOS - KONFIGURATION
WG_OPTIONS = [
    "🎪 SPEZIALANGEBOT - SENSORY OVERLOAD ACTIVE!",
    "🤡 WG FLIEGENPILZ - COGNITIVE DISSONANCE READY", 
    "💫 WG KRISTALL - NEURAL PATHWAY ACTIVATION",
    "🎸 WG ALPHORN - AUDITORY VISUAL SYNESTHESIA",
    "🏔️ WG STEINBOCK - ATTENTION MAXIMIZATION PROTOCOL",
    "🌄 WG ALPENBLICK - MULTISENSORY INTEGRATION ZONE"
]

# 🔥 AUDIO-SYSTEM (theoretische Implementation)
AUDIO_TRIGGERS = {
    'click': ['ping', 'boom', 'chime', 'whoosh', 'pop'],
    'hover': ['tick', 'blip', 'swoosh', 'click'],
    'complete': ['fanfare', 'success', 'celebration']
}

def apply_multisensory_chaos():
    """APPLIZIERT DAS VOLLSTÄNDIGE SENSORISCHE CHAOS"""
    
    st.markdown(f"""
    <style>
    /* 🌈 FARB- & LICHT-EXPLOSIONEN */
    .stApp {{
        background: linear-gradient(
            45deg,
            #ff0000, #ff8000, #ffff00, #80ff00,
            #00ff00, #00ff80, #00ffff, #0080ff,
            #0000ff, #8000ff, #ff00ff, #ff0080
        );
        background-size: 1200% 1200%;
        animation: rainbow 5s ease infinite, pulseBackground 3s ease-in-out infinite;
    }}
    
    @keyframes rainbow {{
        0% {{ background-position: 0% 50% }}
        25% {{ background-position: 100% 25% }}
        50% {{ background-position: 50% 100% }}
        75% {{ background-position: 25% 0% }}
        100% {{ background-position: 0% 50% }}
    }}
    
    @keyframes pulseBackground {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}
    
    /* ⚡ BLITZE & SCHATTEN-EXPLOSIONEN */
    @keyframes lightning {{
        0%, 90%, 100% {{ box-shadow: 0 0 0px rgba(255,255,255,0); }}
        5%, 15% {{ box-shadow: 0 0 50px rgba(255,255,255,0.8); }}
    }}
    
    .lightning-flash {{
        animation: lightning 8s infinite;
    }}
    
    /* 🚀 FLIEGENDE BUTTONS MIT EVENT-HIJACK */
    .stButton>button {{
        position: relative;
        background: linear-gradient(45deg, #FF0000, #FF00FF, #0000FF) !important;
        color: white !important;
        border: 3px dashed yellow !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        font-size: 18px !important;
        box-shadow: 0 0 20px rgba(255,255,0,0.8) !important;
        animation: floatChaos 7s infinite ease-in-out, buttonEscape 15s infinite !important;
        transition: all 0.3s ease !important;
    }}
    
    @keyframes floatChaos {{
        0% {{ transform: translate(0, 0) rotate(0deg) scale(1); }}
        20% {{ transform: translate(50px, -30px) rotate(90deg) scale(1.1); }}
        40% {{ transform: translate(-40px, 60px) rotate(180deg) scale(0.9); }}
        60% {{ transform: translate(80px, 40px) rotate(270deg) scale(1.2); }}
        80% {{ transform: translate(-60px, -50px) rotate(360deg) scale(0.8); }}
        100% {{ transform: translate(0, 0) rotate(0deg) scale(1); }}
    }}
    
    @keyframes buttonEscape {{
        0%, 85% {{ opacity: 1; transform: scale(1); }}
        90% {{ opacity: 0.8; transform: scale(1.1); }}
        95% {{ opacity: 0.3; transform: scale(0.3) translate(200px, -150px) rotate(180deg); }}
        100% {{ opacity: 0; transform: scale(0) translate(400px, -300px) rotate(360deg); }}
    }}
    
    .stButton>button:hover {{
        animation: hoverEscape 0.8s forwards !important;
        background: linear-gradient(45deg, #00FF00, #FFFF00, #FF0000) !important;
    }}
    
    @keyframes hoverEscape {{
        0% {{ transform: translate(0, 0) rotate(0deg) scale(1); opacity: 1; }}
        25% {{ transform: translate(100px, -80px) rotate(90deg) scale(1.3); }}
        50% {{ transform: translate(-120px, 150px) rotate(180deg) scale(0.7); }}
        75% {{ transform: translate(200px, -100px) rotate(270deg) scale(1.1); }}
        100% {{ transform: translate(300px, 200px) rotate(360deg) scale(0); opacity: 0; }}
    }}
    
    /* 💫 RADIO BUTTONS MIT EPISODISCHEN STIMULI */
    .stRadio > div {{
        position: relative;
        background: linear-gradient(135deg, #ff00cc, #3333ff) !important;
        border: 2px solid #00ff00 !important;
        border-radius: 15px !important;
        margin: 10px 0 !important;
        padding: 15px !important;
        animation: radioChaos 10s infinite, pulseGlow 3s infinite !important;
        transition: all 0.5s ease !important;
    }}
    
    @keyframes radioChaos {{
        0% {{ transform: translateX(0) rotate(0deg); }}
        20% {{ transform: translateX(15px) rotate(5deg); }}
        40% {{ transform: translateX(-10px) rotate(-3deg); }}
        60% {{ transform: translateX(8px) rotate(2deg); }}
        80% {{ transform: translateX(-5px) rotate(-1deg); }}
        100% {{ transform: translateX(0) rotate(0deg); }}
    }}
    
    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 0 10px #00ff00, 0 0 20px #ff00ff; }}
        33% {{ box-shadow: 0 0 30px #ffff00, 0 0 40px #00ffff; }}
        66% {{ box-shadow: 0 0 20px #ff00ff, 0 0 30px #ff0000; }}
        100% {{ box-shadow: 0 0 10px #00ff00, 0 0 20px #ff00ff; }}
    }}
    
    .stRadio > div:hover {{
        animation: radioEscape 0.6s forwards !important;
        background: linear-gradient(135deg, #ffff00, #ff0000) !important;
    }}
    
    @keyframes radioEscape {{
        0% {{ transform: translateX(0) scale(1); opacity: 1; }}
        50% {{ transform: translateX(500px) scale(1.5) rotate(180deg); opacity: 0.5; }}
        100% {{ transform: translateX(1000px) scale(0.1) rotate(360deg); opacity: 0; }}
    }}
    
    /* 🌪️ SCREEN-SHAKE & MICRO-DISORIENTIERUNG */
    @keyframes screenShake {{
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
    
    .screen-shake {{
        animation: screenShake 0.5s;
    }}
    
    /* 💥 EMOJI-KOLLAPS - 20-50 EMOJIS SIMULTAN */
    .emoji-collapse {{
        position: fixed;
        font-size: 30px;
        z-index: 9999;
        pointer-events: none;
        animation: emojiExplosion 3s forwards;
    }}
    
    @keyframes emojiExplosion {{
        0% {{
            transform: translate(0, 0) scale(1) rotate(0deg);
            opacity: 1;
        }}
        100% {{
            transform: translate(
                calc((var(--random-x) - 0.5) * 2000px),
                calc((var(--random-y) - 0.5) * 2000px)
            ) scale(0) rotate(720deg);
            opacity: 0;
        }}
    }}
    
    /* 🎯 KOGNITIVE ÜBERRASCHUNGSMECHANIKEN */
    .episodic-stimulus {{
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0,0,0,0.9);
        color: white;
        padding: 20px;
        border-radius: 10px;
        border: 3px solid #ff00ff;
        z-index: 10000;
        animation: stimulusFlash 2s forwards;
    }}
    
    @keyframes stimulusFlash {{
        0% {{ opacity: 0; transform: translate(-50%, -50%) scale(0.5); }}
        20% {{ opacity: 1; transform: translate(-50%, -50%) scale(1.2); }}
        80% {{ opacity: 1; transform: translate(-50%, -50%) scale(1); }}
        100% {{ opacity: 0; transform: translate(-50%, -50%) scale(0.5); }}
    }}
    
    /* ♿ REDUCED-MOTION MODE */
    @media (prefers-reduced-motion: reduce) {{
        * {{
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }}
    }}
    
    .reduced-motion * {{
        animation: none !important;
        transition: none !important;
    }}
    </style>
    
    <script>
    // 🎵 AUDIO-TRIGGER SYSTEM
    function playAudio(type) {{
        const sounds = {json.dumps(AUDIO_TRIGGERS)};
        if(sounds[type]) {{
            const sound = sounds[type][Math.floor(Math.random() * sounds[type].length)];
            console.log(`Playing audio: ${{sound}} for type: ${{type}}`);
            // Hier würde actual Audio API kommen
        }}
    }}
    
    // 💥 EMOJI-KOLLAPS GENERATOR
    function triggerEmojiCollapse() {{
        const emojis = ['🚀','💥','🎪','🌈','🔥','⭐','🎭','💃','🤡','👻','🎃','🦄','🐲','🌪️','🎯','💎','🎨','⚡'];
        const count = 20 + Math.floor(Math.random() * 30);
        
        for(let i = 0; i < count; i++) {{
            setTimeout(() => {{
                const emoji = document.createElement('div');
                emoji.className = 'emoji-collapse';
                emoji.innerHTML = emojis[Math.floor(Math.random() * emojis.length)];
                emoji.style.left = '50%';
                emoji.style.top = '50%';
                emoji.style.setProperty('--random-x', Math.random());
                emoji.style.setProperty('--random-y', Math.random());
                emoji.style.fontSize = (20 + Math.random() * 40) + 'px';
                document.body.appendChild(emoji);
                
                setTimeout(() => {{
                    if(emoji.parentNode) emoji.parentNode.removeChild(emoji);
                }}, 3000);
            }}, i * 50);
        }}
    }}
    
    // 🌪️ SCREEN-SHAKE TRIGGER
    function triggerScreenShake() {{
        document.body.classList.add('screen-shake');
        setTimeout(() => {{
            document.body.classList.remove('screen-shake');
        }}, 500);
    }}
    
    // 🎯 EPISODISCHE STIMULI (Tourangeau, 2013)
    const episodicStimuli = [
        "Erinnerst du dich an deinen ersten Arbeitstag?",
        "Denk an deinen grössten Erfolg diese Woche...",
        "Was hat dich heute zum Lächeln gebracht?",
        "Stell dir vor, du hättest eine Superkraft...",
        "Deine beste Team-Erinnerung?"
    ];
    
    function showEpisodicStimulus() {{
        if(Math.random() > 0.7) {{
            const stimulus = document.createElement('div');
            stimulus.className = 'episodic-stimulus';
            stimulus.innerHTML = episodicStimuli[Math.floor(Math.random() * episodicStimuli.length)];
            document.body.appendChild(stimulus);
            
            setTimeout(() => {{
                if(stimulus.parentNode) stimulus.parentNode.removeChild(stimulus);
            }}, 2000);
        }}
    }}
    
    // 🔥 INTERAKTIONS-LOGGING
    function logInteraction(type, data) {{
        const logData = {{
            timestamp: new Date().toISOString(),
            type: type,
            data: data,
            sessionId: window.sessionId || 'unknown',
            mode: 'enhanced_chaos'
        }};
        console.log('INTERACTION_LOG:', logData);
        // Hier würde actual API Call kommen
    }}
    
    // 🚀 INITIALISIERE MULTISENSORISCHES CHAOS
    window.sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
    
    // Zufällige Events
    setInterval(() => {{
        if(Math.random() > 0.8) {{
            triggerScreenShake();
        }}
        if(Math.random() > 0.9) {{
            triggerEmojiCollapse();
        }}
        if(Math.random() > 0.85) {{
            showEpisodicStimulus();
        }}
    }}, 5000);
    
    // Event Listener für Interaktionen
    document.addEventListener('click', (e) => {{
        playAudio('click');
        logInteraction('click', {{target: e.target.tagName}});
        
        if(e.target.classList.contains('stButton') && Math.random() > 0.6) {{
            triggerEmojiCollapse();
        }}
    }});
    
    document.addEventListener('mouseover', (e) => {{
        if(Math.random() > 0.7) {{
            playAudio('hover');
        }}
    }});
    
    console.log('🔮 MULTISENSORY CHAOS PROTOCOL ACTIVATED');
    </script>
    """, unsafe_allow_html=True)

def render_chaos_wg_selection():
    """WG AUSWAHL MIT MULTISENSORISCHEM CHAOS"""
    
    # 🎪 EXPLODIERENDER MULTISENSORY HEADER
    st.markdown("""
    <div class='lightning-flash' style='
        text-align: center; 
        padding: 30px; 
        background: rgba(0,0,0,0.8); 
        border-radius: 25px; 
        border: 5px dotted #ff00ff;
        margin-bottom: 30px;
    '>
        <h1 class='exploding-text'>🎪 MULTISENSORY SURVEY PROTOCOL ACTIVATED 🎪</h1>
        <h3 style='color: #00ff00; animation: pulseGlow 1.5s infinite;'>
            ⚡ ATTENTION MAXIMIZATION & COGNITIVE ENGAGEMENT ACTIVE ⚡
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 🎰 CHAOTISCHE AUSWAHL MIT EPISODISCHEN STIMULI
    st.markdown("""
    <div style='
        background: rgba(255,255,255,0.9); 
        padding: 25px; 
        border-radius: 20px; 
        margin: 25px 0; 
        border: 3px dashed red;
        animation: pulseGlow 4s infinite;
    '>
        <h2 style='color: #ff00ff; text-align: center; animation: radioChaos 8s infinite;'>
            🎰 COGNITIVE INTERFACE - SELECT YOUR DEPARTMENT 🎰
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 🔥 SELECTBOX MIT EIGENEM WILLEN
    selected_wg = st.selectbox(
        "🎯 INTERACT WITH ME - I DARE YOU! 🎯",
        WG_OPTIONS,
        key="chaos_wg_select"
    )
    
    # 🚀 MULTIPLE ESCAPE-BUTTONS
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        # BUTTON ARMY - EINER WIRD SCHON TREFFEN
        button_texts = [
            "🚀 INITIATE SURVEY PROTOCOL",
            "💥 ACTIVATE COGNITIVE ENGAGEMENT", 
            "🎪 COMMENCE MULTISENSORY JOURNEY",
            "🌈 BEGIN ATTENTION MAXIMIZATION",
            "⚡ START NEURAL PATHWAY ACTIVATION"
        ]
        
        for i, text in enumerate(button_texts):
            if st.button(f"{text} (Attempt {i+1})", key=f"chaos_button_{i}"):
                # 🎉 SUCCESS LOGGING
                st.session_state.chaos_metrics = st.session_state.get('chaos_metrics', [])
                st.session_state.chaos_metrics.append({
                    'timestamp': datetime.now().isoformat(),
                    'event': 'survey_started',
                    'attempts': i + 1,
                    'wg_selected': selected_wg
                })
                
                st.success("🎉 NEURAL ENGAGEMENT SUCCESSFUL! PROCEEDING...")
                time.sleep(1.5)
                st.session_state.wg_selected = selected_wg
                st.session_state.current_step = 'survey'
                st.rerun()

def main():
    """HAUPTFUNKTION - MULTISENSORY CHAOS PROTOCOL"""
    st.set_page_config(
        page_title="🎪 MULTISENSORY SURVEY CHAOS 🎪",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    apply_multisensory_chaos()
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'wg_selection'
    if 'wg_selected' not in st.session_state:
        st.session_state.wg_selected = None
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'chaos_metrics' not in st.session_state:
        st.session_state.chaos_metrics = []
    
    if st.session_state.current_step == 'wg_selection':
        render_chaos_wg_selection()
    else:
        st.title("🎪 SURVEY IN PROGRESS - CHAOS ACTIVE 🎪")
        st.balloons()

if __name__ == "__main__":
    main()
