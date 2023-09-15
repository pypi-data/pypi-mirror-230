import json
import sys
from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import requests
from requests import RequestException

from . import constants
from .models import Gitmoji, GitmojiList

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

__all__ = [
    "load_gitmojis_api",
    "load_gitmojis_json",
]


class BaseGitmojiLoader:
    def __new__(cls, *args: Any, **kwargs: Dict[str, Any]) -> Self:
        if cls is BaseGitmojiLoader:
            raise TypeError(
                f"only subclasses of {BaseGitmojiLoader.__name__} may be instantiated."
            )
        return super().__new__(cls)

    def __init__(self, /, *, default_source: Any) -> None:
        self.default_source = default_source

    def __call__(self, /, *, source: Optional[Any] = None) -> GitmojiList:
        self._source = source or self.default_source

        return GitmojiList(
            [Gitmoji.from_dict(gitmoji_dict) for gitmoji_dict in self._load_gitmojis()]
        )

    @abstractmethod
    def _load_gitmojis(self) -> Sequence[Dict[str, Any]]:
        ...


class ApiGitmojiLoader(BaseGitmojiLoader):
    def __init__(self) -> None:
        super().__init__(default_source=constants.GITMOJIS_API_URL)

    def __call__(self) -> GitmojiList:  # type: ignore[override]
        return super().__call__()

    def _load_gitmojis(self) -> List[Dict[str, Any]]:
        try:
            (response := requests.get(self._source)).raise_for_status()
        except RequestException as exc_info:
            raise ConnectionError(
                "loading Gitmoji data from the API failed."
            ) from exc_info
        gitmojis = response.json().get("gitmojis")
        if gitmojis is None:
            raise ValueError("the current Gitmoji API data format isn't supported.")
        return gitmojis  # type: ignore[no-any-return]


load_gitmojis_api = ApiGitmojiLoader()


class JsonGitmojiLoader(BaseGitmojiLoader):
    def __init__(self) -> None:
        super().__init__(default_source=constants.GITMOJIS_JSON_PATH_PACKAGE)

    def _load_gitmojis(self) -> List[Dict[str, Any]]:
        with Path(self._source).open(mode="r", encoding="UTF-8") as fp:
            gitmojis = json.load(fp)
        if not isinstance(gitmojis, list):
            raise TypeError(
                f"on a top level, the JSON data to be loaded from '{self._source}' "
                f"must be a list, not {type(gitmojis).__name__}."
            )
        return gitmojis


load_gitmojis_json = JsonGitmojiLoader()
