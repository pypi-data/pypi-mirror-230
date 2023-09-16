import json
import logging
import mimetypes
from pathlib import Path

import httpx
from aiofiles import open
from tqdm.asyncio import tqdm

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    pass


async def download_task(
    client: httpx.AsyncClient,
    item: dict,
    field: str,
    output_dir: str,
) -> None:
    try:
        response = await client.get(item[field])
        content_type = response.headers["Content-Type"]
        extension = mimetypes.guess_extension(content_type)
        filename = f"{output_dir}/{item['id']}{extension}"
        async with open(filename, "wb") as f:
            await f.write(response.content)
    except Exception as e:
        raise DownloadError(f"Error downloading: {item}") from e


async def download_from_json_dump(
    filename: str,
    field: str,
    media_type: str = None,
):
    path = Path(filename)

    # load file
    with path.open() as f:
        data = json.load(f)

    # create output directory
    output_dir = path.parent / path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    # download media
    async with httpx.AsyncClient(timeout=300) as client:
        tasks = [
            download_task(client, item, field, output_dir)
            for item in data
            if field in item and (media_type is None or item["media_type"] == media_type)
        ]
        for result in tqdm.as_completed(tasks):
            try:
                await result
            except Exception as e:
                logger.error(e)