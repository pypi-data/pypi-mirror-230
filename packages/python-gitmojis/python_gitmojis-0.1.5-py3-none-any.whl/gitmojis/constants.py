from pathlib import Path
from typing import Final

GITMOJIS_API_URL: Final = "https://gitmoji.dev/api/gitmojis"

GITMOJIS_JSON_PATH_PACKAGE: Final = Path(__file__).parent / "assets" / "gitmojis.json"

GITMOJIS_JSON_PATH_REPO: Final = (
    Path.cwd() / "src" / "gitmojis" / "assets" / "gitmojis.json"
)

DUMP_GITMOJIS_API_PULL_REQUEST_BODY: Final = """## Gitmoji API dumped! 🎉

The latest version of the official Gitmoji [API][gitmoji-api] has been dumped to the repo's backup file. 🗃️

{gitmojis_summary}

[gitmoji-api]: https://github.com/carloscuesta/gitmoji/tree/master/packages/gitmojis#api
"""
