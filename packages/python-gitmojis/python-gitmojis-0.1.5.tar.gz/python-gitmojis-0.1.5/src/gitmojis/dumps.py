import json

import click

from .constants import (
    DUMP_GITMOJIS_API_PULL_REQUEST_BODY,
    GITMOJIS_JSON_PATH_PACKAGE,
    GITMOJIS_JSON_PATH_REPO,
)
from .loaders import load_gitmojis_api, load_gitmojis_json
from .models import GitmojiList


def get_gitmojis_api_update_summary_message(header: str, gitmojis: GitmojiList) -> str:
    if not gitmojis:
        return ""
    for index, gitmoji in enumerate(gitmojis):
        if index == 0:
            message = f"{header}\n\n"
        message += f"* {gitmoji.emoji} `{gitmoji.code}` &ndash; {gitmoji.description}"
        if index < len(gitmojis) - 1:
            message += "\n"
    return message


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Don't make the dump, just show the backup update summary.",
)
@click.option(
    "--dev",
    is_flag=True,
    help="Dump the API to the repo's, not the package's, backup.",
)
def dump_gitmojis_api(dry_run: bool, dev: bool) -> None:
    """Make a dump of the Gitmojis API to the backup file."""
    if (gitmojis_api := load_gitmojis_api()) == (gitmojis_json := load_gitmojis_json()):
        click.echo("😎 The backup file is up-to-date with the Gitmoji API. ✅")
    else:
        added_gitmojis_message = get_gitmojis_api_update_summary_message(
            header="### ➕ Added",
            gitmojis=GitmojiList(list(set(gitmojis_api) - set(gitmojis_json))),
        )
        discarded_gitmojis_message = get_gitmojis_api_update_summary_message(
            header="### ➖ Discarded",
            gitmojis=GitmojiList(list(set(gitmojis_json) - set(gitmojis_api))),
        )

        click.echo(
            DUMP_GITMOJIS_API_PULL_REQUEST_BODY.format(
                gitmojis_summary=("\n" * 2).join(
                    filter(None, [added_gitmojis_message, discarded_gitmojis_message])
                )
            )
        )

        if not dry_run:
            json_path, json_data = (
                GITMOJIS_JSON_PATH_REPO if dev else GITMOJIS_JSON_PATH_PACKAGE,
                [gitmoji.to_dict() for gitmoji in gitmojis_api],
            )
            with json_path.open("w", encoding="UTF-8") as fp:
                json.dump(json_data, fp, ensure_ascii=False, indent=2)
                fp.write("\n")  # to avoid `end-of-file-fixer` hook error!
