import json

def load_chapter():
    with open(
        "content/class5/science/chapter1/chapter.json",
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)

def load_scenes():
    with open(
        "content/class5/science/chapter1/scenes.json",
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)
