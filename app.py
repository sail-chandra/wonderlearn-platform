import streamlit as st
import json
from pathlib import Path
from utils.content_loader import (
load_chapter,
load_scenes
)

# --------------------------------------------------

# Page Configuration

# --------------------------------------------------

st.set_page_config(
page_title="WonderLearn",
page_icon="🌟",
layout="wide"
)

# --------------------------------------------------

# Session State

# --------------------------------------------------

if "scene_index" not in st.session_state:
    st.session_state.scene_index = 0

if "chapter_started" not in st.session_state:
    st.session_state.chapter_started = False

# --------------------------------------------------

# Theme Styling

# --------------------------------------------------

st.markdown("""

<style>

.hero {
    padding: 30px;
    border-radius: 20px;
    background: linear-gradient(135deg,#2563EB,#22C55E);
    color: white;
    text-align: center;
    margin-bottom: 20px;
}

.chapter-card {
    padding: 15px;
    border-radius: 15px;
    background: #F8FAFC;
    border: 1px solid #E5E7EB;
    margin-bottom: 10px;
}

.badge {
    background: #FBBF24;
    color: black;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
}

.scene-box {
    padding: 20px;
    border-radius: 15px;
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    margin-top: 20px;
}

</style>

""", unsafe_allow_html=True)

# --------------------------------------------------

# Hero Section

# --------------------------------------------------

st.markdown("""

<div class='hero'>
    <h1>🌟 WonderLearn</h1>
    <h3>Learn Through Stories, Explore Through Adventures</h3>
    <p>An Interactive Learning Platform for Young Explorers</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------

# Student Profile

# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
student_name = st.text_input(
"Student Name",
value="Explorer"
)

with col2:
selected_class = st.selectbox(
"Class",
["Class 5"]
)

with col3:
subject = st.selectbox(
"Subject",
["General Science"]
)

# --------------------------------------------------

# Welcome Message

# --------------------------------------------------

st.success(f"Welcome {student_name}! 🚀")

# --------------------------------------------------

# Progress Section

# --------------------------------------------------

st.subheader("📈 Learning Progress")

st.progress(0)

st.info("You have not started any chapter yet.")

# --------------------------------------------------

# Load Chapters

# --------------------------------------------------

json_file = Path("content/class5/science/chapters.json")

if json_file.exists():

```
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

st.subheader("📚 Available Adventures")

for chapter in data["chapters"]:

    st.markdown(f"""
    <div class='chapter-card'>
        <h4>Chapter {chapter['id']} : {chapter['title']}</h4>
        <span class='badge'>
            🏆 {chapter['badge']}
        </span>
    </div>
    """, unsafe_allow_html=True)

    if st.button(
        f"Start {chapter['title']}",
        key=f"chapter_{chapter['id']}"
    ):
        st.session_state.chapter_started = True
        st.session_state.scene_index = 0
        st.rerun()
```

else:
st.error(
"chapters.json not found. Please verify the path: "
"content/class5/science/chapters.json"
)

# --------------------------------------------------

# Achievement Zone

# --------------------------------------------------

st.subheader("🎖 Achievement Zone")

c1, c2, c3, c4 = st.columns(4)

with c1:
st.metric("XP", "0")

with c2:
st.metric("Badges", "0")

with c3:
st.metric("Completed", "0")

with c4:
st.metric("Level", "Explorer")

# --------------------------------------------------

# Chapter Scene Engine

# --------------------------------------------------

if st.session_state.chapter_started:

```
st.divider()

if st.button("🏠 Back to Home"):
    st.session_state.chapter_started = False
    st.session_state.scene_index = 0
    st.rerun()

chapter_data = load_chapter()
scenes_data = load_scenes()

scene_count = len(scenes_data["scenes"])

if st.session_state.scene_index >= scene_count:
    st.session_state.scene_index = 0

scene = scenes_data["scenes"][
    st.session_state.scene_index
]

st.header(scene["title"])

st.caption(
    f"Scene {st.session_state.scene_index + 1} of {scene_count}"
)

st.markdown(
    f"**🎭 Character:** {scene['character']}"
)

st.info(scene["narration"])

if "dialogue" in scene:

    st.success(
        f"{scene['dialogue']['speaker']}: "
        f"{scene['dialogue']['text']}"
    )

# Scene Type Display

st.markdown(
    f"**Scene Type:** {scene['type'].title()}"
)

# Hotspots

if "hotspots" in scene:

    st.subheader("🔍 Explore")

    for hotspot in scene["hotspots"]:

        with st.expander(hotspot["name"]):
            st.write(hotspot["description"])

# Activities

if "activities" in scene:

    st.subheader("🎮 Activities")

    for activity in scene["activities"]:
        st.write("•", activity)

# Examples

if "examples" in scene:

    st.subheader("🌱 Examples")

    for example in scene["examples"]:
        st.write("•", example)

# Steps

if "steps" in scene:

    st.subheader("🧑‍🌾 Farming Steps")

    for i, step in enumerate(scene["steps"], start=1):
        st.write(f"{i}. {step}")

st.divider()

col_prev, col_next = st.columns(2)

with col_prev:

    if st.button(
        "⬅ Previous",
        disabled=(
            st.session_state.scene_index == 0
        )
    ):
        st.session_state.scene_index -= 1
        st.rerun()

with col_next:

    if st.button(
        "Next ➡",
        disabled=(
            st.session_state.scene_index
            >= scene_count - 1
        )
    ):
        st.session_state.scene_index += 1
        st.rerun()
```

# --------------------------------------------------

# Footer

# --------------------------------------------------

st.divider()

st.caption(
"WonderLearn © 2026 | Learn Through Stories, Explore Through Adventures"
)
