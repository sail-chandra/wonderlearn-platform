import streamlit as st
import json
import os
import base64
import tempfile
from pathlib import Path
from utils.content_loader import load_chapter, load_scenes

st.set_page_config(
    page_title="WonderLearn",
    page_icon="🌟",
    layout="wide"
)

# ─── TTS Helper ───────────────────────────────────────────────────────────────

@st.cache_data
def generate_tts_audio(text, scene_id):
    """Generate TTS audio for narration text and return base64 encoded audio."""
    try:
        from gtts import gTTS
        import io
        tts = gTTS(text=text, lang='en', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.getvalue()
    except Exception:
        return None


def render_audio_player(narration_text, scene_id):
    """Render a play narration button with TTS."""
    audio_data = generate_tts_audio(narration_text, scene_id)
    if audio_data:
        st.audio(audio_data, format="audio/mp3")


# ─── CSS Animations & Styling ─────────────────────────────────────────────────

st.markdown("""
<style>

/* ─── Base Layout ─────────────────────────────────────────────────────────── */

.story-container {
    background: white;
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    margin-top: 15px;
    margin-bottom: 15px;
}

.dialogue-box {
    background: #F0FDF4;
    border-left: 6px solid #22C55E;
    padding: 20px;
    border-radius: 15px;
    font-size: 18px;
    margin-top: 15px;
    animation: slideInLeft 0.6s ease-out;
}

.speaker {
    font-size: 20px;
    font-weight: bold;
    color: #2563EB;
}

.fun-fact-box {
    background: #FEF9C3;
    border-left: 6px solid #EAB308;
    padding: 15px;
    border-radius: 10px;
    font-size: 16px;
    margin-top: 15px;
    animation: fadeIn 0.8s ease-out;
}

.hotspot-card {
    background: #F8FAFC;
    border: 2px solid #E2E8F0;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
}

.badge-container {
    text-align: center;
    padding: 40px;
    background: linear-gradient(135deg, #FEF9C3, #FDE68A);
    border-radius: 20px;
    margin: 20px 0;
    animation: badgePop 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.badge-icon {
    font-size: 80px;
    animation: bounce 1s ease infinite;
}

.summary-card {
    background: #F0F9FF;
    border-left: 4px solid #3B82F6;
    padding: 15px;
    border-radius: 10px;
    margin: 8px 0;
    animation: slideInLeft 0.5s ease-out;
}

.xp-gain {
    background: #ECFDF5;
    border: 2px solid #22C55E;
    border-radius: 10px;
    padding: 10px 15px;
    text-align: center;
    font-weight: bold;
    color: #16A34A;
}

.quiz-correct {
    background: #DCFCE7;
    border-left: 4px solid #22C55E;
    padding: 10px 15px;
    border-radius: 8px;
    margin-top: 8px;
}

.quiz-wrong {
    background: #FEE2E2;
    border-left: 4px solid #EF4444;
    padding: 10px 15px;
    border-radius: 8px;
    margin-top: 8px;
}

.step-card {
    background: #F8FAFC;
    border-radius: 12px;
    padding: 15px;
    margin: 8px 0;
    border-left: 4px solid #8B5CF6;
    animation: slideInLeft 0.5s ease-out;
}

/* ─── Animations ──────────────────────────────────────────────────────────── */

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

@keyframes badgePop {
    0% { transform: scale(0); opacity: 0; }
    50% { transform: scale(1.2); }
    100% { transform: scale(1); opacity: 1; }
}

@keyframes growUp {
    0% { height: 0; opacity: 0; }
    100% { height: 100%; opacity: 1; }
}

@keyframes float {
    0%, 100% { transform: translateY(0) translateX(0); }
    25% { transform: translateY(-15px) translateX(10px); }
    50% { transform: translateY(-5px) translateX(20px); }
    75% { transform: translateY(-20px) translateX(30px); }
    100% { transform: translateY(0) translateX(40px); }
}

@keyframes waterFlow {
    0% { transform: translateX(0) rotate(0deg); }
    50% { transform: translateX(30px) rotate(5deg); }
    100% { transform: translateX(60px) rotate(-5deg); }
}

@keyframes explode {
    0% { transform: scale(1); }
    50% { transform: scale(1.3); }
    100% { transform: scale(0); opacity: 0; }
}

@keyframes sprout {
    0% { height: 0; opacity: 0; }
    30% { height: 20px; opacity: 0.5; }
    60% { height: 50px; opacity: 0.8; }
    100% { height: 80px; opacity: 1; }
}

/* ─── Process Animation Containers ────────────────────────────────────────── */

.animation-container {
    background: linear-gradient(180deg, #E0F2FE 0%, #BAE6FD 50%, #7DD3FC 100%);
    border-radius: 20px;
    padding: 30px;
    margin: 20px 0;
    position: relative;
    overflow: hidden;
    min-height: 200px;
}

.germination-anim {
    background: linear-gradient(180deg, #FEF9C3 0%, #92400E 60%, #78350F 100%);
    border-radius: 20px;
    padding: 30px;
    margin: 20px 0;
    text-align: center;
    position: relative;
    min-height: 250px;
}

.seed-icon {
    font-size: 50px;
    animation: bounce 2s ease-in-out infinite;
    display: inline-block;
}

.root-anim {
    font-size: 30px;
    animation: growUp 2s ease-out forwards;
    display: inline-block;
}

.shoot-anim {
    font-size: 40px;
    animation: sprout 3s ease-out forwards;
    display: inline-block;
}

.wind-seed {
    font-size: 30px;
    display: inline-block;
    animation: float 4s ease-in-out infinite;
}

.water-seed {
    font-size: 30px;
    display: inline-block;
    animation: waterFlow 3s ease-in-out infinite;
}

.explode-seed {
    font-size: 30px;
    display: inline-block;
    animation: explode 2s ease-out infinite;
}

/* ─── Farming Timeline ────────────────────────────────────────────────────── */

.timeline-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    margin: 20px 0;
}

.timeline-step {
    background: white;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    min-width: 100px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    animation: fadeIn 0.5s ease-out;
    position: relative;
}

.timeline-step::after {
    content: "→";
    position: absolute;
    right: -15px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 20px;
    color: #22C55E;
}

.timeline-step:last-child::after {
    content: "";
}

.timeline-icon {
    font-size: 30px;
    margin-bottom: 5px;
}

/* ─── Seed Anatomy Animation ──────────────────────────────────────────────── */

.seed-anatomy {
    background: linear-gradient(135deg, #FEF3C7, #FDE68A);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    margin: 20px 0;
    position: relative;
}

.seed-layer {
    display: inline-block;
    margin: 0 10px;
    text-align: center;
    animation: fadeIn 1s ease-out;
}

.seed-layer-icon {
    font-size: 50px;
    margin-bottom: 8px;
}

.seed-layer-label {
    font-size: 14px;
    font-weight: bold;
    color: #92400E;
}

/* ─── Scene Type Badge ────────────────────────────────────────────────────── */

.scene-type-badge {
    display: inline-block;
    background: #EFF6FF;
    color: #2563EB;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# ─── Animation Renderers ──────────────────────────────────────────────────────

def render_animation(animation_config):
    """Render CSS animations based on animation type."""
    anim_type = animation_config.get("type", "")

    if anim_type == "germination_stages":
        st.markdown("""
        <div class="germination-anim">
            <div style="margin-bottom: 15px; font-weight: bold; color: #78350F;">🎬 Germination in Action</div>
            <div style="display: flex; justify-content: center; align-items: flex-end; gap: 30px; height: 150px;">
                <div style="text-align: center;">
                    <div class="seed-icon">🌰</div>
                    <div style="font-size: 12px; color: #78350F;">Seed</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 40px; animation: bounce 1.5s ease-in-out infinite 0.5s;">💧</div>
                    <div style="font-size: 12px; color: #78350F;">+ Water</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 40px; animation: bounce 1.5s ease-in-out infinite 1s;">💥</div>
                    <div style="font-size: 12px; color: #78350F;">Cracks</div>
                </div>
                <div style="text-align: center;">
                    <div class="root-anim">⬇️🌿</div>
                    <div style="font-size: 12px; color: #78350F;">Root Down</div>
                </div>
                <div style="text-align: center;">
                    <div class="shoot-anim">🌱</div>
                    <div style="font-size: 12px; color: #78350F;">Shoot Up!</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "seed_dispersal":
        st.markdown("""
        <div class="animation-container">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #1E40AF;">🎬 Seeds on the Move!</div>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
                <div style="text-align: center; padding: 15px;">
                    <div class="wind-seed">🌬️ 🪶</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Wind</strong><br>Floating away...</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div class="water-seed">🌊 🥥</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Water</strong><br>Floating downstream...</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div style="font-size: 30px; animation: bounce 2s ease-in-out infinite;">🐕 🌿</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Animals</strong><br>Hitching a ride!</div>
                </div>
                <div style="text-align: center; padding: 15px;">
                    <div class="explode-seed">💥 🫛</div>
                    <div style="font-size: 13px; margin-top: 8px;"><strong>Explosion</strong><br>Pop! Scatter!</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "seed_anatomy":
        st.markdown("""
        <div class="seed-anatomy">
            <div style="font-weight: bold; margin-bottom: 20px; color: #92400E;">🎬 Inside a Seed — Layers Revealed</div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 20px; flex-wrap: wrap;">
                <div class="seed-layer" style="animation-delay: 0s;">
                    <div class="seed-layer-icon">🛡️</div>
                    <div class="seed-layer-label">Seed Coat<br><small>(Outer protection)</small></div>
                </div>
                <div style="font-size: 24px; color: #92400E;">→</div>
                <div class="seed-layer" style="animation-delay: 0.5s;">
                    <div class="seed-layer-icon">🍽️</div>
                    <div class="seed-layer-label">Cotyledons<br><small>(Food storage)</small></div>
                </div>
                <div style="font-size: 24px; color: #92400E;">→</div>
                <div class="seed-layer" style="animation-delay: 1s;">
                    <div class="seed-layer-icon">🌱</div>
                    <div class="seed-layer-label">Embryo<br><small>(Baby plant)</small></div>
                </div>
            </div>
            <div style="margin-top: 15px; display: flex; justify-content: center; gap: 40px;">
                <div style="font-size: 13px; color: #78350F;">⬇️ Radicle (root)</div>
                <div style="font-size: 13px; color: #78350F;">⬆️ Plumule (shoot)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "stem_cutting":
        st.markdown("""
        <div class="animation-container" style="background: linear-gradient(180deg, #ECFDF5, #D1FAE5);">
            <div style="font-weight: bold; text-align: center; margin-bottom: 20px; color: #065F46;">🎬 Growing a New Plant from a Stem Cutting</div>
            <div style="display: flex; justify-content: center; align-items: flex-end; gap: 25px; flex-wrap: wrap;">
                <div style="text-align: center;">
                    <div style="font-size: 40px;">✂️🌿</div>
                    <div style="font-size: 12px; margin-top: 5px;">Cut a healthy stem</div>
                </div>
                <div style="font-size: 20px; color: #22C55E;">→</div>
                <div style="text-align: center;">
                    <div style="font-size: 40px; animation: bounce 2s infinite;">🪴</div>
                    <div style="font-size: 12px; margin-top: 5px;">Plant in moist soil</div>
                </div>
                <div style="font-size: 20px; color: #22C55E;">→</div>
                <div style="text-align: center;">
                    <div style="font-size: 40px; animation: sprout 3s ease-out infinite;">🌿⬇️</div>
                    <div style="font-size: 12px; margin-top: 5px;">Roots grow from base</div>
                </div>
                <div style="font-size: 20px; color: #22C55E;">→</div>
                <div style="text-align: center;">
                    <div style="font-size: 40px; animation: bounce 1.5s ease-in-out infinite;">🌳</div>
                    <div style="font-size: 12px; margin-top: 5px;">New plant grows!</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif anim_type == "agriculture_timeline":
        st.markdown("""
        <div style="margin: 20px 0;">
            <div style="font-weight: bold; text-align: center; margin-bottom: 15px; color: #92400E;">🎬 The Farming Journey</div>
            <div class="timeline-container">
                <div class="timeline-step"><div class="timeline-icon">🚜</div><div>Plough</div></div>
                <div class="timeline-step"><div class="timeline-icon">🧪</div><div>Manure</div></div>
                <div class="timeline-step"><div class="timeline-icon">🌱</div><div>Sow</div></div>
                <div class="timeline-step"><div class="timeline-icon">💧</div><div>Irrigate</div></div>
                <div class="timeline-step"><div class="timeline-icon">🐛</div><div>Protect</div></div>
                <div class="timeline-step"><div class="timeline-icon">🌾</div><div>Harvest</div></div>
                <div class="timeline-step"><div class="timeline-icon">🏪</div><div>Store</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─── Session State Initialization ─────────────────────────────────────────────

if "scene_index" not in st.session_state:
    st.session_state.scene_index = 0

if "chapter_started" not in st.session_state:
    st.session_state.chapter_started = False

if "selected_chapter" not in st.session_state:
    st.session_state.selected_chapter = 1

if "xp" not in st.session_state:
    st.session_state.xp = 0

if "badges" not in st.session_state:
    st.session_state.badges = []

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

if "challenge_submitted" not in st.session_state:
    st.session_state.challenge_submitted = False

if "challenge_score" not in st.session_state:
    st.session_state.challenge_score = 0

if "experiment_result" not in st.session_state:
    st.session_state.experiment_result = None

if "activity_submitted" not in st.session_state:
    st.session_state.activity_submitted = False

if "activity_score" not in st.session_state:
    st.session_state.activity_score = 0

if "scene_xp_awarded" not in st.session_state:
    st.session_state.scene_xp_awarded = set()

# ─── Header (conditional) ─────────────────────────────────────────────────────

if not st.session_state.chapter_started:
    # Full header on home page
    col_logo, col_xp = st.columns([4, 1])

    with col_logo:
        st.title("🌟 WonderLearn")
        st.subheader("Learn Through Stories, Explore Through Adventures")

    with col_xp:
        st.metric("⭐ XP", st.session_state.xp)
        if st.session_state.badges:
            st.write("🏆 " + ", ".join(st.session_state.badges))

    # Student Info
    col1, col2, col3 = st.columns(3)

    with col1:
        student_name = st.text_input("Student Name", value="Explorer")

    with col2:
        selected_class = st.selectbox("Class", ["Class 5"])

    with col3:
        subject = st.selectbox("Subject", ["General Science"])
else:
    # Minimal header during chapter - just XP in corner
    student_name = "Explorer"

# ─── Load Chapters Index ──────────────────────────────────────────────────────

json_file = Path("content/class5/science/chapters.json")
data = None

if json_file.exists():
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

# ─── Home Screen ──────────────────────────────────────────────────────────────

if not st.session_state.chapter_started:
    st.success(f"Welcome {student_name}! 🚀 Choose an adventure to begin.")

    if data:
        st.subheader("📚 Available Adventures")

        for chapter in data["chapters"]:
            col_ch, col_badge = st.columns([4, 1])

            with col_ch:
                st.markdown(f"### Chapter {chapter['id']} — {chapter['title']}")

            with col_badge:
                st.write(f"🏆 {chapter['badge']}")

            chapter_folder = Path(f"content/class5/science/chapter{chapter['id']}")
            chapter_file = chapter_folder / "chapter.json"
            scene_file = chapter_folder / "scenes.json"

            if chapter_file.exists() and scene_file.exists():
                if st.button(f"🚀 Start: {chapter['title']}", key=f"chapter_{chapter['id']}"):
                    st.session_state.chapter_started = True
                    st.session_state.selected_chapter = chapter["id"]
                    st.session_state.scene_index = 0
                    st.session_state.quiz_submitted = False
                    st.session_state.challenge_submitted = False
                    st.session_state.activity_submitted = False
                    st.session_state.experiment_result = None
                    st.rerun()
            else:
                st.info("🚧 Coming Soon")

            st.divider()

# ─── Scene Rendering Engine ───────────────────────────────────────────────────

if st.session_state.chapter_started:

    # Compact top bar: Home button + Chapter title + XP
    col_home, col_title, col_xp_mini = st.columns([1, 4, 1])

    with col_home:
        if st.button("🏠 Home"):
            st.session_state.chapter_started = False
            st.session_state.scene_index = 0
            st.session_state.quiz_submitted = False
            st.session_state.challenge_submitted = False
            st.session_state.activity_submitted = False
            st.session_state.experiment_result = None
            st.rerun()

    with col_title:
        st.markdown("**🌟 WonderLearn**")

    with col_xp_mini:
        st.metric("⭐ XP", st.session_state.xp)

    chapter_data = load_chapter(st.session_state.selected_chapter)
    scenes_data = load_scenes(st.session_state.selected_chapter)

    if chapter_data is None or scenes_data is None:
        st.warning("🚧 This adventure is under development.")
        st.stop()

    scene_count = len(scenes_data["scenes"])
    scene = scenes_data["scenes"][st.session_state.scene_index]
    scene_type = scene.get("scene_type", "story")

    # Scene type badge
    type_labels = {
        "story": "📖 Story", "explore": "🔍 Explore", "experiment": "🧪 Experiment",
        "activity": "🎮 Activity", "challenge": "⚡ Challenge", "quiz": "📝 Quiz",
        "summary": "📋 Summary", "badge": "🏆 Badge Award"
    }
    st.markdown(f"<span class='scene-type-badge'>{type_labels.get(scene_type, scene_type)}</span>",
                unsafe_allow_html=True)

    # Background image (only if not "none")
    bg = scene.get("background", "none")
    if bg and bg != "none":
        background_file = f"assets/backgrounds/{bg}.jpg"
        if Path(background_file).exists():
            st.image(background_file, use_container_width=True)

    # ─── Scene Type: STORY ────────────────────────────────────────────────────

    if scene_type == "story":
        col_content, col_char = st.columns([3, 1])

        with col_content:
            st.header(scene["title"])

            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

            # Animation
            if "animation" in scene:
                render_animation(scene["animation"])

            # Steps display
            if "steps_display" in scene:
                st.write("")
                for i, step in enumerate(scene["steps_display"]):
                    st.markdown(f"""
                    <div class='step-card' style='animation-delay: {i * 0.2}s;'>
                        <strong>{step['icon']} Step {step['step']}: {step['title']}</strong><br>
                        {step['description']}
                    </div>
                    """, unsafe_allow_html=True)

            if "fun_fact" in scene:
                st.markdown(f"""
                <div class='fun-fact-box'>
                    <strong>🧠 Fun Fact:</strong> {scene['fun_fact']}
                </div>
                """, unsafe_allow_html=True)

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=250)

    # ─── Scene Type: EXPLORE ──────────────────────────────────────────────────

    elif scene_type == "explore":
        st.header(scene["title"])

        col_content, col_char = st.columns([3, 1])

        with col_content:
            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=200)

        # Animation
        if "animation" in scene:
            render_animation(scene["animation"])

        st.write("")
        st.subheader("🔍 Explore — Click to Learn More")

        if "hotspots" in scene:
            for hotspot in scene["hotspots"]:
                with st.expander(f"{hotspot['icon']} {hotspot['name']}", expanded=False):
                    st.write(hotspot["description"])
                    if "examples" in hotspot:
                        examples_str = ", ".join(hotspot["examples"])
                        st.info(f"📌 Examples: {examples_str}")
                    if "fun_fact" in hotspot:
                        st.markdown(f"""
                        <div class='fun-fact-box'>
                            <strong>🧠 Fun Fact:</strong> {hotspot['fun_fact']}
                        </div>
                        """, unsafe_allow_html=True)

    # ─── Scene Type: EXPERIMENT ───────────────────────────────────────────────

    elif scene_type == "experiment":
        st.header(scene["title"])

        col_content, col_char = st.columns([3, 1])

        with col_content:
            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=200)

        if "experiment" in scene:
            exp = scene["experiment"]
            st.write("")
            st.subheader(f"🧪 {exp['title']}")
            st.write(exp["instructions"])

            st.write("")
            conditions_state = {}

            for condition in exp["conditions"]:
                conditions_state[condition["id"]] = st.toggle(
                    f"{condition['icon']} {condition['name']}",
                    key=f"exp_{scene['id']}_{condition['id']}"
                )
                if conditions_state[condition["id"]]:
                    st.caption(f"   ↳ {condition['description']}")

            st.write("")
            if st.button("🔬 Run Experiment", key=f"run_exp_{scene['id']}"):
                required = [c for c in exp["conditions"] if c["required"]]
                all_required_on = all(conditions_state[c["id"]] for c in required)

                if all_required_on:
                    st.session_state.experiment_result = "success"
                else:
                    st.session_state.experiment_result = "failure"

            if st.session_state.experiment_result == "success":
                st.success(f"✅ {exp['success_message']}")
                for condition in exp["conditions"]:
                    if not condition["required"] and conditions_state.get(condition["id"]):
                        st.info(f"💡 {condition['name']}: {condition['description']}")

            elif st.session_state.experiment_result == "failure":
                st.error(f"❌ {exp['failure_message']}")
                missing = [c for c in exp["conditions"] if c["required"] and not conditions_state.get(c["id"])]
                for m in missing:
                    st.warning(f"Missing: {m['icon']} {m['name']} — {m['description']}")

    # ─── Scene Type: ACTIVITY (Matching / Sequence) ───────────────────────────

    elif scene_type == "activity":
        st.header(scene["title"])

        col_content, col_char = st.columns([3, 1])

        with col_content:
            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=200)

        # Animation
        if "animation" in scene:
            render_animation(scene["animation"])

        if "activity" in scene:
            activity = scene["activity"]
            st.write("")
            st.subheader(f"🎮 {activity['title']}")
            st.write(activity["instructions"])

            # ─── Matching Activity ────────────────────────────────────────────
            if activity["type"] == "matching":
                answers = {}
                options = activity["options"]

                for pair in activity["pairs"]:
                    answers[pair["item"]] = st.selectbox(
                        f"{pair['icon']} {pair['item']}",
                        options=["— Select —"] + options,
                        key=f"match_{scene['id']}_{pair['item']}"
                    )

                if st.button("✅ Check Answers", key=f"check_match_{scene['id']}"):
                    st.session_state.activity_submitted = True
                    correct = 0
                    for pair in activity["pairs"]:
                        if answers[pair["item"]] == pair["match"]:
                            correct += 1
                    st.session_state.activity_score = correct

                if st.session_state.activity_submitted:
                    total = len(activity["pairs"])
                    score = st.session_state.activity_score

                    if score == total:
                        st.balloons()
                        st.success(f"🎉 Perfect! You got all {total} correct!")
                    elif score >= total * 0.7:
                        st.success(f"👍 Great job! {score}/{total} correct!")
                    else:
                        st.warning(f"You got {score}/{total} correct. Review below:")

                    for pair in activity["pairs"]:
                        user_ans = answers.get(pair["item"], "— Select —")
                        is_correct = user_ans == pair["match"]
                        icon = "✅" if is_correct else "❌"
                        st.markdown(f"**{icon} {pair['item']}** → Correct: **{pair['match']}**")
                        st.caption(f"   {pair['explanation']}")

            # ─── Sequence Activity ────────────────────────────────────────────
            elif activity["type"] == "sequence":
                st.write("Arrange these steps in the correct order (1 = first):")
                user_order = {}

                for step in activity["steps"]:
                    user_order[step["id"]] = st.selectbox(
                        f"{step['icon']} {step['name']}",
                        options=list(range(1, len(activity["steps"]) + 1)),
                        key=f"seq_{scene['id']}_{step['id']}"
                    )

                if st.button("✅ Check Order", key=f"check_seq_{scene['id']}"):
                    st.session_state.activity_submitted = True
                    correct = sum(
                        1 for step in activity["steps"]
                        if user_order[step["id"]] == step["correct_position"]
                    )
                    st.session_state.activity_score = correct

                if st.session_state.activity_submitted:
                    total = len(activity["steps"])
                    score = st.session_state.activity_score

                    if score == total:
                        st.balloons()
                        st.success(f"🎉 Perfect order! All {total} steps correct!")
                    elif score >= total * 0.7:
                        st.success(f"👍 Great job! {score}/{total} in the right position!")
                    else:
                        st.warning(f"You got {score}/{total} in the right position. Here's the correct order:")

                    for step in sorted(activity["steps"], key=lambda s: s["correct_position"]):
                        st.markdown(f"""
                        <div class='step-card'>
                            <strong>{step['icon']} Step {step['correct_position']}: {step['name']}</strong><br>
                            {step['description']}
                        </div>
                        """, unsafe_allow_html=True)

    # ─── Scene Type: CHALLENGE (True/False) ───────────────────────────────────

    elif scene_type == "challenge":
        st.header(scene["title"])

        col_content, col_char = st.columns([3, 1])

        with col_content:
            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=200)

        if "challenge" in scene:
            challenge = scene["challenge"]
            st.write("")
            st.subheader(f"⚡ {challenge['title']}")

            user_answers = {}
            for q in challenge["questions"]:
                user_answers[q["id"]] = st.radio(
                    f"**{q['statement']}**",
                    options=["True", "False"],
                    key=f"tf_{scene['id']}_{q['id']}",
                    horizontal=True
                )

            if st.button("✅ Submit Challenge", key=f"submit_challenge_{scene['id']}"):
                st.session_state.challenge_submitted = True
                correct = 0
                for q in challenge["questions"]:
                    user_bool = user_answers[q["id"]] == "True"
                    if user_bool == q["answer"]:
                        correct += 1
                st.session_state.challenge_score = correct

            if st.session_state.challenge_submitted:
                total = len(challenge["questions"])
                score = st.session_state.challenge_score

                if score == total:
                    st.balloons()
                    st.success(f"🎉 Perfect! All {total} correct!")
                elif score >= total * 0.7:
                    st.success(f"👍 Great job! {score}/{total} correct!")
                else:
                    st.warning(f"Keep trying! {score}/{total} correct.")

                for q in challenge["questions"]:
                    user_bool = user_answers[q["id"]] == "True"
                    is_correct = user_bool == q["answer"]
                    css_class = "quiz-correct" if is_correct else "quiz-wrong"
                    icon = "✅" if is_correct else "❌"
                    correct_text = "True" if q["answer"] else "False"
                    st.markdown(f"""
                    <div class='{css_class}'>
                        {icon} <strong>{q['statement']}</strong> → Answer: <strong>{correct_text}</strong><br>
                        <em>{q['explanation']}</em>
                    </div>
                    """, unsafe_allow_html=True)

    # ─── Scene Type: QUIZ ─────────────────────────────────────────────────────

    elif scene_type == "quiz":
        st.header(scene["title"])

        col_content, col_char = st.columns([3, 1])

        with col_content:
            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=200)

        if "quiz" in scene:
            quiz = scene["quiz"]
            st.write("")
            st.subheader(f"📝 {quiz['title']}")
            st.write(f"**Pass score: {quiz['pass_score']}/{len(quiz['questions'])}**")

            user_answers = {}
            for i, q in enumerate(quiz["questions"]):
                user_answers[q["id"]] = st.radio(
                    f"**Q{i+1}. {q['question']}**",
                    options=q["options"],
                    key=f"quiz_{scene['id']}_{q['id']}"
                )

            if st.button("📨 Submit Quiz", key=f"submit_quiz_{scene['id']}"):
                st.session_state.quiz_submitted = True
                correct = 0
                for q in quiz["questions"]:
                    correct_answer = q["options"][q["correct"]]
                    if user_answers[q["id"]] == correct_answer:
                        correct += 1
                st.session_state.quiz_score = correct

            if st.session_state.quiz_submitted:
                total = len(quiz["questions"])
                score = st.session_state.quiz_score
                passed = score >= quiz["pass_score"]

                if passed:
                    st.balloons()
                    st.success(f"🎉 Congratulations! You scored {score}/{total} — Quiz Passed!")
                else:
                    st.error(f"You scored {score}/{total}. You need {quiz['pass_score']} to pass. Review and try again!")

                st.write("---")
                st.write("**Review:**")
                for q in quiz["questions"]:
                    correct_answer = q["options"][q["correct"]]
                    user_ans = user_answers[q["id"]]
                    is_correct = user_ans == correct_answer
                    css_class = "quiz-correct" if is_correct else "quiz-wrong"
                    icon = "✅" if is_correct else "❌"
                    st.markdown(f"""
                    <div class='{css_class}'>
                        {icon} <strong>{q['question']}</strong><br>
                        Your answer: {user_ans} | Correct: <strong>{correct_answer}</strong><br>
                        <em>{q['explanation']}</em>
                    </div>
                    """, unsafe_allow_html=True)

    # ─── Scene Type: SUMMARY ──────────────────────────────────────────────────

    elif scene_type == "summary":
        st.header(scene["title"])

        col_content, col_char = st.columns([3, 1])

        with col_content:
            if "dialogue" in scene:
                st.markdown(f"""
                <div class='dialogue-box'>
                    <div class='speaker'>{scene['dialogue']['speaker']}</div>
                    <br>{scene['dialogue']['text']}
                </div>
                """, unsafe_allow_html=True)

            st.write("")
            st.write(scene["narration"])

            # TTS audio
            if scene.get("tts"):
                with st.expander("🔊 Listen to Narration"):
                    render_audio_player(scene["narration"], scene["id"])

        with col_char:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=200)

        if "summary_points" in scene:
            st.write("")
            st.subheader("📋 What You Learned")
            for i, point in enumerate(scene["summary_points"]):
                st.markdown(f"""
                <div class='summary-card' style='animation-delay: {i * 0.15}s;'>
                    <strong>{point['icon']} {point['title']}</strong><br>
                    {point['text']}
                </div>
                """, unsafe_allow_html=True)

    # ─── Scene Type: BADGE ────────────────────────────────────────────────────

    elif scene_type == "badge":
        if "badge" in scene:
            badge = scene["badge"]

            st.markdown(f"""
            <div class='badge-container'>
                <div class='badge-icon'>{badge['icon']}</div>
                <h2>🏆 {badge['name']}</h2>
                <p>{badge['description']}</p>
            </div>
            """, unsafe_allow_html=True)

            if badge["name"] not in st.session_state.badges:
                st.session_state.badges.append(badge["name"])
                st.balloons()

        st.header(scene["title"])

        if "dialogue" in scene:
            st.markdown(f"""
            <div class='dialogue-box'>
                <div class='speaker'>{scene['dialogue']['speaker']}</div>
                <br>{scene['dialogue']['text']}
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.write(scene["narration"])

        # TTS audio
        if scene.get("tts"):
            with st.expander("🔊 Listen to Narration"):
                render_audio_player(scene["narration"], scene["id"])

        col_char_center = st.columns([1, 2, 1])
        with col_char_center[1]:
            character_file = f"assets/characters/{scene['character']}.png"
            if Path(character_file).exists():
                st.image(character_file, width=250)

    # ─── XP Award ─────────────────────────────────────────────────────────────

    scene_key = f"ch{st.session_state.selected_chapter}_s{scene['id']}"
    if scene_key not in st.session_state.scene_xp_awarded:
        xp_gain = scene.get("xp", 10)
        st.session_state.xp += xp_gain
        st.session_state.scene_xp_awarded.add(scene_key)

    # ─── Progress & Navigation ────────────────────────────────────────────────

    st.write("")
    st.progress((st.session_state.scene_index + 1) / scene_count)

    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.caption(f"Scene {st.session_state.scene_index + 1} of {scene_count}")
    with col_info2:
        st.caption(f"Type: {scene_type.title()}")
    with col_info3:
        st.caption(f"XP this scene: +{scene.get('xp', 10)}")

    st.divider()

    col_prev, col_scene_info, col_next = st.columns([1, 2, 1])

    with col_prev:
        if st.button("⬅ Previous", disabled=(st.session_state.scene_index == 0)):
            st.session_state.scene_index -= 1
            st.session_state.quiz_submitted = False
            st.session_state.challenge_submitted = False
            st.session_state.activity_submitted = False
            st.session_state.experiment_result = None
            st.rerun()

    with col_scene_info:
        st.markdown(f"<div class='xp-gain'>⭐ Total XP: {st.session_state.xp}</div>",
                    unsafe_allow_html=True)

    with col_next:
        if st.button("Next ➡", disabled=(st.session_state.scene_index >= scene_count - 1)):
            st.session_state.scene_index += 1
            st.session_state.quiz_submitted = False
            st.session_state.challenge_submitted = False
            st.session_state.activity_submitted = False
            st.session_state.experiment_result = None
            st.rerun()

# ─── Footer ──────────────────────────────────────────────────────────────────

st.divider()
st.caption("WonderLearn © 2026 | Learn Through Stories, Explore Through Adventures")
