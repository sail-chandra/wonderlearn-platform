import json

def load_chapter(chapter_id):

    with open(
        f"content/class5/science/chapter{chapter_id}/chapter.json",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

def load_scenes(chapter_id):

    with open(
        f"content/class5/science/chapter{chapter_id}/scenes.json",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)
