import json
from pathlib import Path

def load_chapter(chapter_id):

    chapter_file = Path(
        f"content/class5/science/chapter{chapter_id}/chapter.json"
    )

    if not chapter_file.exists():
        return None

with open(
    chapter_file,
    "r",
    encoding="utf-8"
) as f:

    return json.load(f)

def load_scenes(chapter_id):

    scene_file = Path(
        f"content/class5/science/chapter{chapter_id}/scenes.json"
    )
    
    if not scene_file.exists():
        return None

with open(
    scene_file,
    "r",
    encoding="utf-8"
) as f:

    return json.load(f)
