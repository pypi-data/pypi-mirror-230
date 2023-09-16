import logging

import typer

from instadump.lib.config import load_config
from instadump.lib.instagram import Crawler, InstagramClient

logger = logging.getLogger(__name__)
app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(
    config: str = "config.yaml",
    ig_connected_id: str = typer.Option(None, envvar="IG_CONNECTED_ID"),
    ig_access_token: str = typer.Option(None, envvar="IG_ACCESS_TOKEN"),
):
    config = load_config(config)
    client = InstagramClient(ig_connected_id, ig_access_token)
    crawler = Crawler(client, config)
    crawler.run()


if __name__ == "__main__":
    app()
