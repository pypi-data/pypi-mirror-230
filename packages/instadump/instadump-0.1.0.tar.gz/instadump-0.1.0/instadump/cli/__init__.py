import typer
import logging

from instadump.cli import (
    crawl,
    download,
)

logger = logging.getLogger(__name__)

app = typer.Typer()
app.add_typer(download.app, name="download-media")
app.add_typer(crawl.app, name="crawl")


@app.callback(invoke_without_command=True)
def main(verbose: bool = False):
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    if verbose:
        logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    app()
