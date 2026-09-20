import streamlit as st

def render_cinematic_intro():
    """
    Renders an executive, professional 3D AI-powered intro screen for NEXORA.
    Appears on initial startup or when requested via ?intro=1 or clicking Replay 3D Intro.
    """
    # Allow URL query param ?intro=1 to force intro playback
    if st.query_params.get("intro") == "1":
        st.session_state.intro_seen = False

    if st.session_state.get("intro_seen", False):
        return

    intro_html = """<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700;800;900&family=Inter:wght@400;600;700;800&display=swap');

.cinematic-intro-wrapper {
    position: relative;
    width: 100%;
    min-height: 85vh;
    background: radial-gradient(circle at 50% 40%, #150a0d 0%, #080406 60%, #020102 100%);
    border-radius: 12px;
    border: 1px solid rgba(255, 45, 60, 0.3);
    box-shadow: 0 0 60px rgba(0, 0, 0, 0.95), inset 0 0 50px rgba(220, 20, 35, 0.15);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    font-family: 'Space Grotesk', sans-serif;
    padding: 50px 20px;
    margin-top: 10px;
}

/* Ambient glow lighting */
.intro-bg-glow {
    position: absolute;
    width: 130vw;
    height: 130vh;
    background: radial-gradient(circle at 50% 45%, rgba(255, 30, 48, 0.28) 0%, rgba(130, 10, 20, 0.14) 40%, rgba(2, 1, 2, 0.98) 75%);
    pointer-events: none;
    animation: pulseGlow 4s ease-in-out infinite alternate;
}

.intro-grid {
    position: absolute;
    inset: 0;
    background-image: 
        linear-gradient(rgba(255, 45, 60, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 45, 60, 0.05) 1px, transparent 1px);
    background-size: 45px 45px;
    mask-image: radial-gradient(circle at 50% 45%, black 40%, transparent 80%);
    -webkit-mask-image: radial-gradient(circle at 50% 45%, black 40%, transparent 80%);
    pointer-events: none;
}

/* 3D NEURAL CORE STAGE */
.neural-stage {
    position: relative;
    z-index: 10;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    max-width: 800px;
    margin-bottom: 30px;
}

.neural-core-wrap {
    position: relative;
    width: 160px;
    height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: revealNeuralCore 0.45s cubic-bezier(0.16, 1, 0.3, 1) 0.05s forwards;
    will-change: transform, opacity;
    opacity: 0;
}

.neural-orb {
    width: 110px;
    height: 110px;
    background: radial-gradient(circle at 35% 35%, #ff4d58 0%, #b80c17 60%, #4a0208 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 50px rgba(255, 45, 60, 0.9), inset 0 0 25px rgba(255, 255, 255, 0.4);
    position: relative;
    z-index: 5;
    animation: orbPulse 2s ease-in-out infinite alternate;
    will-change: box-shadow;
}

.orb-icon {
    font-size: 48px;
    filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.8));
}

.orbit-ring {
    position: absolute;
    width: 170px;
    height: 170px;
    border: 2px dashed rgba(255, 75, 88, 0.6);
    border-radius: 50%;
    animation: spinRing 8s linear infinite;
    will-change: transform;
    pointer-events: none;
}

.orbit-ring-outer {
    position: absolute;
    width: 210px;
    height: 210px;
    border: 1px solid rgba(255, 45, 60, 0.25);
    border-radius: 50%;
    animation: spinRingReverse 12s linear infinite;
    will-change: transform;
    pointer-events: none;
}

/* Floating feature badges */
.floating-features {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 24px;
    z-index: 15;
    opacity: 0;
    animation: revealFeatures 0.4s ease-out 0.2s forwards;
    will-change: transform, opacity;
}

.feature-pill {
    background: rgba(26, 14, 17, 0.85);
    border: 1px solid rgba(255, 45, 60, 0.3);
    border-radius: 999px;
    padding: 8px 18px;
    color: #e0e0e0;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    gap: 8px;
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease;
}

.feature-pill:hover {
    transform: translateY(-2px);
    border-color: rgba(255, 77, 88, 0.6);
}

.feature-pill span {
    color: #ff4d58;
}

/* Light Sweep Beam */
.sweep-beam {
    position: absolute;
    top: -50%;
    left: -150%;
    width: 60%;
    height: 200%;
    background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.65) 50%, transparent 100%);
    transform: rotate(25deg);
    animation: sweepAction 0.6s ease-in-out 0.25s forwards;
    will-change: transform, opacity, left;
    pointer-events: none;
    z-index: 25;
}

/* Typography Stage */
.text-stage {
    position: relative;
    z-index: 30;
    text-align: center;
    opacity: 0;
    transform: translateY(16px);
    animation: revealText 0.4s cubic-bezier(0.16, 1, 0.3, 1) 0.12s forwards;
    will-change: transform, opacity;
}

.status-badge {
    display: inline-block;
    color: #ff4d58;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 14px;
    padding: 5px 16px;
    background: rgba(220, 25, 40, 0.14);
    border: 1px solid rgba(255, 60, 75, 0.35);
    border-radius: 999px;
    box-shadow: 0 0 18px rgba(255, 45, 60, 0.25);
}

.title-main {
    font-size: clamp(32px, 5vw, 48px);
    font-weight: 900;
    color: #ffffff;
    letter-spacing: 4px;
    text-transform: uppercase;
    line-height: 1.08;
    margin: 0;
    text-shadow: 0 0 40px rgba(255, 40, 55, 0.7);
}

.title-main span {
    color: #e22230;
    background: linear-gradient(135deg, #ff525e 0%, #d61a27 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle-main {
    font-family: 'Inter', sans-serif;
    font-size: clamp(13px, 2vw, 15px);
    font-weight: 600;
    color: #b8acae;
    letter-spacing: 2px;
    margin-top: 14px;
    opacity: 0;
    animation: revealSub 0.35s ease-out 0.25s forwards;
    will-change: transform, opacity;
}

/* Keyframe Animations */
@keyframes revealNeuralCore {
    0% { transform: scale(0.6) translateY(20px); opacity: 0; }
    70% { transform: scale(1.04) translateY(-2px); opacity: 1; }
    100% { transform: scale(1) translateY(0); opacity: 1; }
}

@keyframes orbPulse {
    0% { box-shadow: 0 0 35px rgba(255, 45, 60, 0.75); }
    100% { box-shadow: 0 0 65px rgba(255, 77, 88, 0.95), 0 0 20px rgba(255, 255, 255, 0.5); }
}

@keyframes spinRing {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes spinRingReverse {
    0% { transform: rotate(360deg); }
    100% { transform: rotate(0deg); }
}

@keyframes revealFeatures {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
}

@keyframes sweepAction {
    0% { left: -150%; opacity: 0; }
    30% { opacity: 0.9; }
    100% { left: 200%; opacity: 0; }
}

@keyframes revealText {
    0% { opacity: 0; transform: translateY(16px) scale(0.98); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes revealSub {
    0% { opacity: 0; transform: translateY(8px); }
    100% { opacity: 0.9; transform: translateY(0); }
}

@keyframes pulseGlow {
    0% { opacity: 0.85; transform: scale(1); }
    100% { opacity: 1.15; transform: scale(1.03); }
}

div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #e21b28 0%, #b80c17 100%) !important;
    color: #ffffff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 800 !important;
    font-size: 15px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border: 1px solid #ff4d58 !important;
    border-radius: 6px !important;
    padding: 14px 28px !important;
    box-shadow: 0 0 25px rgba(226, 27, 40, 0.55), inset 0 1px 0 rgba(255,255,255,0.2) !important;
    transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
}

div[data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #ff3342 0%, #d61825 100%) !important;
    box-shadow: 0 0 40px rgba(255, 51, 66, 0.85), inset 0 1px 0 rgba(255,255,255,0.3) !important;
    transform: translateY(-2px) scale(1.02) !important;
}
</style>

<div class="cinematic-intro-wrapper">
<div class="intro-bg-glow"></div>
<div class="intro-grid"></div>

<div class="neural-stage">
<div class="sweep-beam"></div>

<!-- 3D NEURAL CORE -->
<div class="neural-core-wrap">
<div class="orbit-ring-outer"></div>
<div class="orbit-ring"></div>
<div class="neural-orb">
<span class="orb-icon">🤖</span>
</div>
</div>

<!-- FLOATING FEATURE BADGES -->
<div class="floating-features">
<div class="feature-pill"><span>📄</span> AI Resume Parser</div>
<div class="feature-pill"><span>🎯</span> ATS Compatibility Engine</div>
<div class="feature-pill"><span>🤖</span> Candidate AI Review</div>
<div class="feature-pill"><span>💼</span> Live Vacancy Matcher</div>
</div>
</div>

<div class="text-stage">
<div class="status-badge">⚡ AI-Powered Career Intelligence Platform</div>
<h1 class="title-main">NEXORA</h1>
<div class="subtitle-main">AI-POWERED CAREER INTELLIGENCE</div>
<div style="font-size: 13px; color: #b8abad; font-weight: 700; letter-spacing: 1px; margin-top: 10px;">Resume Analysis • ATS Optimization • Job Matching • Career Growth</div>
</div>
</div>
"""

    st.markdown(intro_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        if st.button("ENTER COMMAND CENTER  →", type="primary", key="btn_enter_command_center", use_container_width=True):
            st.session_state.intro_seen = True
            st.rerun()
