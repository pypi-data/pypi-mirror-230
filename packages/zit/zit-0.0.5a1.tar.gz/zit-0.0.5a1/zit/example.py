import os
from enum import Enum
from pathlib import Path

import httpx
import typer
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn

from .config import REGISTRY_ENDPOINT, ZITRC_FILE, logger
from .utils import SubprocessError, find_zit_root, run_subprocess

example_app = app = typer.Typer(name="example", help="Example commands")


class ExampleName(str, Enum):
    detection_fashion = "detection/fashion"


# Helper function to extract filename from Content-Disposition
def get_filename_from_content_disposition(content_disposition):
    parts = content_disposition.split(";")
    for part in parts:
        if "filename=" in part:
            return part.split("=")[1].strip(' "')
    return None  # default if not found


@app.command(name="pull", help="Pull example")
def pull(name: ExampleName, unzip: bool = True):
    if not ZITRC_FILE.exists():
        logger.warning('Key not found, please login first by "zit auth login"')
        return

    with ZITRC_FILE.open("r") as f:
        token = f.read()

    zit_root = find_zit_root(Path.cwd())

    with httpx.Client(headers={"Token": token}) as client:
        with client.stream("GET", f"{REGISTRY_ENDPOINT}/example?name={name.value}") as response:
            if response.status_code == 401:
                logger.warning('Invalid key, please login first by "zit auth login"')
                return

            if response.status_code == 404:
                logger.warning(f"Example {name.value} not found")
                return

            total = int(response.headers["Content-Length"])

            content_disposition = response.headers.get("Content-Disposition", "")
            filename = get_filename_from_content_disposition(content_disposition)

            chunk_size = 81920

            with Progress(
                TextColumn(" " * 28),
                TextColumn("   receiving:"),
                BarColumn(),
                TextColumn("[yellow]{task.description}"),
                TextColumn("•"),
                TextColumn("[magenta]{task.percentage:>3.0f}%"),
                TextColumn("•"),
                TextColumn("[green]{task.completed}/{task.total}"),
                TextColumn("•"),
                TimeRemainingColumn(),
            ) as progress:
                task = progress.add_task(description=" " * 30, total=total)

                progress.update(
                    task, description=f"{filename if len(filename) <= 30 else ('...' + filename[-27:]):<30}"
                )

                with open(zit_root / filename, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size):
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))

            if not unzip:
                return

            try:
                run_subprocess(["tar", "-xzf", filename], cwd=zit_root)
                logger.info("Example extracted successfully")
            except SubprocessError as e:
                logger.error(f"Error extracting example: {e}")

            os.remove(zit_root / filename)
