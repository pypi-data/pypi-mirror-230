import pytest

from gitmojis.core import get_gitmojis


@pytest.fixture()
def load_gitmojis_api(mocker):
    return mocker.patch("gitmojis.core.load_gitmojis_api")


@pytest.fixture()
def load_gitmojis_json(mocker):
    return mocker.patch("gitmojis.core.load_gitmojis_json")


def test_get_gitmojis_with_valid_api_response(load_gitmojis_api):
    get_gitmojis()

    assert load_gitmojis_api.called


def test_get_gitmojis_with_connection_error(mocker, load_gitmojis_json):
    mocker.patch("gitmojis.core.load_gitmojis_api", side_effect=ConnectionError)

    get_gitmojis()

    assert load_gitmojis_json.called
