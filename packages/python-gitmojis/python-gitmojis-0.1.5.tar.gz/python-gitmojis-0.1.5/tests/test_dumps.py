import pytest
from click.testing import CliRunner

from gitmojis.dumps import dump_gitmojis_api, get_gitmojis_api_update_summary_message
from gitmojis.loaders import load_gitmojis_json
from gitmojis.models import Gitmoji, GitmojiList


@pytest.fixture(params=[True, False], ids=["dry-run", "no-dry-run"])
def dry_run(request):
    return request.param


@pytest.fixture(params=[True, False], ids=["dev", "no-dev"])
def dev(request):
    return request.param


@pytest.fixture()
def flags(dry_run, dev):
    return list(
        filter(
            None,
            [
                "--dry-run" if dry_run else "",
                "--dev" if dev else "",
            ],
        )
    )


@pytest.fixture(autouse=True)
def mock_load_gitmojis_api(mocker, gitmoji_list):
    mocker.patch("gitmojis.loaders.load_gitmojis_api", return_value=gitmoji_list)
    mocker.patch("gitmojis.loaders.load_gitmojis_json", return_value=gitmoji_list)


@pytest.fixture(autouse=True)
def json_path(mocker, tmp_path, dev):
    json_path = tmp_path / "gitmojis.json"

    mocker.patch(
        f"gitmojis.dumps.GITMOJIS_JSON_PATH_{'REPO' if dev else 'PACKAGE'}",
        json_path,
    )

    return json_path


def test_get_gitmojis_api_update_summary_message_with_gitmojis(gitmoji_list):
    message = get_gitmojis_api_update_summary_message("➕ Added", gitmojis=gitmoji_list)
    gitmoji_details = "\n".join(
        f"* {gitmoji.emoji} `{gitmoji.code}` &ndash; {gitmoji.description}"
        for gitmoji in gitmoji_list
    ).rstrip()

    assert message == f"""➕ Added\n\n{gitmoji_details}"""


def test_get_gitmojis_api_update_summary_message_with_no_gitmojis():
    message = get_gitmojis_api_update_summary_message("Gitmojis 😜", GitmojiList())

    assert message == ""


def test_dump_gitmojis_api_with_api_and_backup_the_same(flags):
    result = CliRunner().invoke(dump_gitmojis_api, flags)

    assert result.stdout == "😎 The backup file is up-to-date with the Gitmoji API. ✅\n"


def test_dump_gitmojis_api_with_gitmojis_updated(
    request, mocker, gitmoji_list, flags, json_path
):
    gitmoji_list[-1] = Gitmoji(emoji="🚀")

    mocker.patch("gitmojis.dumps.load_gitmojis_api", return_value=gitmoji_list)

    result = CliRunner().invoke(dump_gitmojis_api, flags)

    assert "➕ Added" in result.stdout
    assert "➖ Discarded" in result.stdout

    if not request.getfixturevalue("dry_run"):
        assert load_gitmojis_json(source=json_path) == gitmoji_list
