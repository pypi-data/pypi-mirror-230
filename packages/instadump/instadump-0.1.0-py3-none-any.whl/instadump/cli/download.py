from enum import Enum
import asyncio
from typing import Literal, Optional
import typer

from instadump.lib.downloader import download_from_json_dump

app = typer.Typer()


class MediaType(str, Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    CAROUSEL_ALBUM = "CAROUSEL_ALBUM"


async def amain(*args, **kwargs):
    await download_from_json_dump(*args, **kwargs)


@app.callback(invoke_without_command=True)
def main(
    filename: str,
    field: str = "media_url",
    media_type: MediaType = None,
):
    asyncio.run(amain(filename, field, media_type=media_type))


if __name__ == "__main__":
    app()
