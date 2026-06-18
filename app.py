import streamlit as st
import json
from pathlib import Path
from utils.content_loader import load_chapter, load_scenes

st.markdown("""

<style>

.story-container {
    background: white;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    margin-top: 15px;
}

.dialogue-box {
    background: #F8FAFC;
    border-left: 6px solid #22C55E;
    padding: 20px;
    border-radius: 15px;
    font-size: 18px;
    margin-top: 15px;
}

.speaker {
    font-size: 20px;
    font-weight: bold;
    color: #2563EB;
}

</style>

""", unsafe_allow_html=True)

st.set_page_config(
page_title="WonderLearn",
page_icon="🌟",
layout="wide"
)

if "scene_index" not in st.session_state:
    st.session_state.scene_index = 0

if "chapter_started" not in st.session_state:
    st.session_state.chapter_started = False

if "selected_chapter" not in st.session_state:
    st.session_state.selected_chapter = 1

    if "xp" not in st.session_state:
        st.session_state.xp = 0


st.title("🌟 WonderLearn")
st.subheader("Learn Through Stories, Explore Through Adventures")
st.metric(
    "⭐ XP Earned",
    st.session_state.xp
)
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

if not st.session_state.chapter_started:
    st.success(f"Welcome {student_name}! 🚀")

json_file = Path("content/class5/science/chapters.json")

if json_file.exists():

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

if not st.session_state.chapter_started:

    st.subheader("📚 Available Adventures")

    for chapter in data["chapters"]:
        
        st.markdown(
            f"### Chapter {chapter['id']} - {chapter['title']}"
        )
        
        st.write(
            f"🏆 Badge: {chapter['badge']}"
        )
        
        chapter_folder = Path(
            f"content/class5/science/chapter{chapter['id']}"
        )
        
        chapter_file = chapter_folder / "chapter.json"
        scene_file = chapter_folder / "scenes.json"
        
        if chapter_file.exists() and scene_file.exists():
        
            if st.button(
                f"Start {chapter['title']}",
                key=f"chapter_{chapter['id']}"
            ):
                st.session_state.chapter_started = True
                st.session_state.selected_chapter = chapter["id"]
                st.session_state.scene_index = 0
                st.rerun()
        
        else:
        
            st.info("🚧 Coming Soon")
        
        st.divider()

# else:
#     st.error("chapters.json not found")

if st.session_state.chapter_started:

    if st.button("🏠 Back to Home"):
        st.session_state.chapter_started = False
        st.session_state.scene_index = 0
        st.rerun()

    # st.write("Selected Chapter:", st.session_state.selected_chapter)
    
    chapter_data = load_chapter(
    st.session_state.selected_chapter
    )
    
    scenes_data = load_scenes(
    st.session_state.selected_chapter
    )

    # st.write("Chapter Data:", chapter_data)
    # st.write("Scenes Data:", scenes_data)

    if chapter_data is None or scenes_data is None:
        
        st.warning(
            "🚧 This adventure is under development and will be available soon."
        )
    
        if st.button("🏠 Return to Home"):
        
            st.session_state.chapter_started = False
            st.session_state.scene_index = 0
        
            st.rerun()
        
        st.stop()
    
    scene_count = len(scenes_data["scenes"])
    
    scene = scenes_data["scenes"][
        st.session_state.scene_index
    ]

    background_file = (
        f"assets/backgrounds/{scene['background']}.jpg"
        )
        
        if Path(background_file).exists():
        
        st.image(
            background_file,
            use_container_width=True
        )
        
        st.markdown(
        "<div class='story-container'>",
        unsafe_allow_html=True
        )
        
        col1, col2 = st.columns([2,1])
        
        with col1:
        
        st.header(scene["title"])
        
        st.markdown(
            f"""
            <div class='dialogue-box'>
                <div class='speaker'>
                    {scene['dialogue']['speaker']}
                </div>
                <br>
                {scene['dialogue']['text']}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.write("")
        st.write(scene["narration"])
        
        with col2:
        
        character_file = (
            f"assets/characters/{scene['character']}.png"
        )
        
        if Path(character_file).exists():
        
            st.image(
                character_file,
                width=300
            )
        
        st.markdown(
        "</div>",
        unsafe_allow_html=True
        )

    
    st.progress(
        (st.session_state.scene_index + 1) / scene_count
    )
    
    st.write(
        f"Scene {st.session_state.scene_index + 1} of {scene_count}"
    )
    
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
            st.session_state.xp += 10
            st.rerun()

st.divider()

st.caption(
"WonderLearn © 2026 | Learn Through Stories, Explore Through Adventures"
)
