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
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

.cinematic-intro-wrapper {
    position: relative;
    width: 100%;
    min-height: 85vh;
    background: radial-gradient(circle at 50% 35%, #111827 0%, #0B1020 70%, #070A14 100%);
    border-radius: 12px;
    border: 1px solid #263247;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    font-family: 'Inter', sans-serif;
    padding: 50px 20px;
    margin-top: 10px;
}

/* Ambient glow lighting */
.intro-bg-glow {
    position: absolute;
    width: 120vw;
    height: 120vh;
    background: radial-gradient(circle at 50% 40%, rgba(59, 130, 246, 0.15) 0%, rgba(139, 92, 246, 0.08) 40%, transparent 70%);
    pointer-events: none;
}

.intro-grid {
    position: absolute;
    inset: 0;
    background-image: 
        linear-gradient(rgba(59, 130, 246, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59, 130, 246, 0.04) 1px, transparent 1px);
    background-size: 40px 40px;
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
    width: 150px;
    height: 150px;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: revealNeuralCore 0.45s cubic-bezier(0.16, 1, 0.3, 1) 0.05s forwards;
    will-change: transform, opacity;
    opacity: 0;
}

.neural-orb {
    width: 100px;
    height: 100px;
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 50%, #1D4ED8 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 40px rgba(59, 130, 246, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.3);
    position: relative;
    z-index: 5;
}

.orb-icon {
    font-size: 44px;
}

.orbit-ring {
    position: absolute;
    width: 155px;
    height: 155px;
    border: 2px dashed rgba(59, 130, 246, 0.4);
    border-radius: 50%;
    animation: spinRing 12s linear infinite;
    will-change: transform;
    pointer-events: none;
}

.orbit-ring-outer {
    position: absolute;
    width: 190px;
    height: 190px;
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 50%;
    animation: spinRingReverse 18s linear infinite;
    will-change: transform;
    pointer-events: none;
}

/* Floating feature badges */
.floating-features {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 24px;
    z-index: 15;
    opacity: 0;
    animation: revealFeatures 0.4s ease-out 0.2s forwards;
    will-change: transform, opacity;
}

.feature-pill {
    background: #172033;
    border: 1px solid #263247;
    border-radius: 999px;
    padding: 8px 18px;
    color: #CBD5E1;
    font-size: 13px;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    gap: 8px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.feature-pill:hover {
    transform: translateY(-2px);
    border-color: #3B82F6;
}

.feature-pill span {
    color: #3B82F6;
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
    color: #3B82F6;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 14px;
    padding: 5px 16px;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 999px;
}

.title-main {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(32px, 5vw, 48px);
    font-weight: 800;
    color: #F8FAFC;
    letter-spacing: 2px;
    line-height: 1.08;
    margin: 0;
}

.title-main span {
    background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle-main {
    font-family: 'Inter', sans-serif;
    font-size: clamp(13px, 2vw, 15px);
    font-weight: 600;
    color: #CBD5E1;
    letter-spacing: 1.5px;
    margin-top: 14px;
    opacity: 0;
    animation: revealSub 0.35s ease-out 0.25s forwards;
    will-change: transform, opacity;
}

/* Keyframe Animations */
@keyframes revealNeuralCore {
    0% { transform: scale(0.7); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
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

@keyframes revealText {
    0% { opacity: 0; transform: translateY(16px); }
    100% { opacity: 1; transform: translateY(0); }
}

@keyframes revealSub {
    0% { opacity: 0; transform: translateY(8px); }
    100% { opacity: 1; transform: translateY(0); }
}

div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%) !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 1px !important;
    border: 1px solid #3B82F6 !important;
    border-radius: 6px !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}

div[data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%) !important;
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45) !important;
    transform: translateY(-2px) !important;
}
</style>

<div class="cinematic-intro-wrapper">
<div class="intro-bg-glow"></div>
<div class="intro-grid"></div>

<div class="neural-stage">

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
<div style="font-size: 13px; color: #94A3B8; font-weight: 500; margin-top: 10px;">Resume Analysis • ATS Optimization • Job Matching • Career Growth</div>
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
