from gitmojis.loaders import load_gitmojis_api, load_gitmojis_json
from gitmojis.models import GitmojiList

__all__ = [
    "gitmojis",
]


def get_gitmojis() -> GitmojiList:
    try:
        gitmojis = load_gitmojis_api()
    except ConnectionError:
        gitmojis = load_gitmojis_json()
    return gitmojis


gitmojis = get_gitmojis()
