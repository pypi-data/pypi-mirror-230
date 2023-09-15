import pytest
import requests

from gitmojis.loaders import ApiGitmojiLoader, BaseGitmojiLoader, JsonGitmojiLoader
from gitmojis.models import GitmojiList


class MockedGitmojiLoader(BaseGitmojiLoader):
    def __init__(self):
        return super().__init__(default_source=None)

    def _load_gitmojis(self):
        return [{"emoji": emoji} for emoji in self._source]


@pytest.fixture()
def mock_api_response(gitmoji_dict):
    class MockedApiResponse:
        gitmojis = [gitmoji_dict]

        def __init__(self, valid):
            self.valid = valid

        def json(self, *args, **kwargs):
            return {"gitmojis": self.gitmojis} if self.valid else {}

        def raise_for_status(self, *args, **kwargs):
            ...

    return MockedApiResponse


@pytest.fixture()
def mock_json(gitmoji_dict):
    class MockedJson:
        gitmojis = [gitmoji_dict]

        def __init__(self, valid):
            self.valid = valid

        def load(self, *args, **kwargs):
            return self.gitmojis if self.valid else {"gitmojis": [gitmoji_dict]}

    return MockedJson


@pytest.fixture(autouse=True)
def mock_pathlib_path_open(mocker):
    mocker.patch("pathlib.Path.open")


def test_base_gitmoji_loader_instantiation():
    with pytest.raises(
        TypeError,
        match=f"only subclasses of {BaseGitmojiLoader.__name__} may be instantiated.",
    ):
        BaseGitmojiLoader()


def test_base_gitmoji_loader_subclass_instantiation():
    load_gitmojis = MockedGitmojiLoader()

    assert isinstance(load_gitmojis, BaseGitmojiLoader)


def test_base_gitmoji_loader_subclass_call():
    load_gitmojis = MockedGitmojiLoader()

    gitmojis = load_gitmojis(source=["💥", "✨", "🐛", "📝"])

    assert isinstance(gitmojis, GitmojiList)


def test_api_gitmoji_loader_call_with_success_response(mocker, mock_api_response):
    mocker.patch("requests.get", return_value=mock_api_response(valid=True))

    load_gitmojis = ApiGitmojiLoader()

    gitmojis = load_gitmojis()

    assert isinstance(gitmojis, GitmojiList)


@pytest.mark.parametrize(
    "exc_class",
    [
        requests.ConnectionError,
        requests.HTTPError,
        requests.RequestException,
    ],
)
def test_api_gitmoji_loader_call_with_request_error(mocker, exc_class):
    mocker.patch("requests.get", side_effect=exc_class)

    load_gitmojis = ApiGitmojiLoader()

    with pytest.raises(
        ConnectionError, match="loading Gitmoji data from the API failed."
    ) as exc_info:
        load_gitmojis()
    assert isinstance(exc_info.value.__cause__, exc_class)


def test_api_gitmoji_loader_call_with_invalid_response_json(mocker, mock_api_response):
    mocker.patch("requests.get", return_value=mock_api_response(valid=False))

    load_gitmojis = ApiGitmojiLoader()

    with pytest.raises(
        ValueError, match="the current Gitmoji API data format isn't supported."
    ):
        load_gitmojis()


def test_json_gitmoji_loader_call_with_valid_json(mocker, mock_json):
    mocker.patch("gitmojis.loaders.json", mock_json(valid=True))

    load_gitmojis = JsonGitmojiLoader()

    gitmojis = load_gitmojis(source="does_not_exist.json")

    assert isinstance(gitmojis, GitmojiList)


def test_json_gitmoji_loader_call_with_invalid_json(mocker, mock_json):
    mocker.patch("gitmojis.loaders.json", mock_json(valid=False))

    load_gitmojis = JsonGitmojiLoader()

    with pytest.raises(
        TypeError,
        match=(
            "on a top level, the JSON data to be loaded from 'does_not_exist.json' "
            "must be a list, not dict."
        ),
    ):
        load_gitmojis(source="does_not_exist.json")
