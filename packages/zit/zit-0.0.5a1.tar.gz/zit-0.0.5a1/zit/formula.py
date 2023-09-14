import codecs
import json
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

import typer
import yaml
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from websocket import create_connection

from .config import (
    WS_FORMULA_INSTALL_ENDPOINT,
    WS_FORMULA_PUBLISH_ENDPOINT,
    ZITRC_FILE,
    logger,
)
from .utils import find_zit_root

formula_app = app = typer.Typer(name="formula", help="Formula commands")


def _walk(path):
    for p in Path(path).iterdir():
        if p.is_dir():
            yield from _walk(p)
            continue
        yield p


def send_files(file_paths, ws=None, chunk_size=102400):
    if not ws:
        ws = create_connection(WS_FORMULA_PUBLISH_ENDPOINT)

    succeed = True

    # Create an incremental decoder, thanks to gpt4
    decoder = codecs.getincrementaldecoder("utf-8")()

    for path in file_paths:
        with Progress(
            TextColumn(" " * 28),
            TextColumn("   sending:"),
            BarColumn(),
            TextColumn("[yellow]{task.description}"),
            TextColumn("•"),
            TextColumn("[magenta]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("[green]{task.completed}/{task.total}"),
            TextColumn("•"),
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task(description=" " * 30, total=os.path.getsize(path))

            progress.update(task, description=f"{path if len(path) <= 30 else ('...' + path[-27:]):<30}")
            try:
                msg = {"path": path}
                ws.send(json.dumps(msg))

                with open(path, "rb") as f:
                    # send file in chunks
                    while True:
                        data = f.read(chunk_size)

                        if not data:
                            break

                        # bytes to string
                        decoded_data = decoder.decode(data, final=False)
                        ws.send(decoded_data)

                        resp = ws.recv()
                        recv_stat = json.loads(resp)

                        if not recv_stat.get("size") % (1 * chunk_size):
                            progress.update(task, completed=recv_stat.get("size"))

                    # Flush the decoder for any remaining data
                    decoded_data = decoder.decode(b"", final=True)
                    if decoded_data:
                        ws.send(decoded_data)

                    # notify end of file
                    ws.send("EOF")

                if recv_stat.get("path") != path or recv_stat.get("size") != os.path.getsize(path):
                    raise Exception(f"File {path} not transferred correctly")

                progress.update(task, completed=recv_stat.get("size"))

            except Exception as err:
                logger.exception(f"Communication error: {err}")
                succeed = False
                break

    return succeed


@app.command(name="publish", help="Publish formula")
def publish(force: bool = False):
    # authentication
    if not ZITRC_FILE.exists():
        logger.warning('Key not found, please login first by "zit auth login"')
        return

    with ZITRC_FILE.open("r") as f:
        token = f.read()

    # authentication
    ws = create_connection(WS_FORMULA_PUBLISH_ENDPOINT)
    ws.send(json.dumps({"token": token}))
    recv_msg = json.loads(ws.recv())
    authenticated = recv_msg.get("authenticated")

    if not authenticated:
        logger.warning('Invalid key, please login first by "zit auth login"')
        return

    user = recv_msg.get("user", {})

    # check if username is confirmed
    if not user.get("username_confirmed"):
        logger.info(
            "Your username is auto-generated during signup. Please go to https://zityspace.cn/set-username to set your"
            " username first."
        )
        return

    file_paths = []

    # infer formula name and version
    if not Path("config.yaml").is_file():
        logger.warning("No config.yaml found, are you inside formula root?")
        return

    cfg = yaml.safe_load(open("config.yaml", "rb"))
    file_paths.append("config.yaml")

    # entrypoint main.py
    entrypoint = cfg.get("config", {}).get("entrypoint")
    if entrypoint is not None:
        main = entrypoint.get("main")
        if main is not None and Path(main).is_file():
            file_paths.append(main)

    # UI part
    ui = cfg.get("config", {}).get("ui")
    if ui is not None:
        if not Path(ui, "index.html").is_file():
            logger.warning("No index.html found, is ui field pointed to the bundled ui folder?")
            return

        file_paths += [str(p) for p in _walk(ui)]

    # check if already published
    title, slug, version, author, description = (
        cfg.get("title"),
        cfg.get("slug"),
        cfg.get("version"),
        cfg.get("author"),
        cfg.get("description"),
    )

    ws.send(
        json.dumps(
            {
                "title": title,
                "slug": slug,
                "version": version,
                "author": author,
                "description": description,
                "force": force,
            }
        )
    )
    recv_msg = json.loads(ws.recv())
    passed = recv_msg.get("passed")

    if not passed:
        logger.warning(recv_msg.get("reason"))
        return

    logger.info(f'publishing: {user.get("username")}/{cfg.get("slug")} == {cfg.get("version")}')

    # send files
    succeed = send_files(file_paths, ws=ws)
    if not succeed:
        return

    # notify finished
    ws.send(json.dumps({"finished": True}))

    # wait for success notification from entrypoint
    recv_msg = json.loads(ws.recv())
    _ = recv_msg.get("finished")

    logger.info("done :)")


def download_formula(name, version, ws=None):
    if not ws:
        ws = create_connection(WS_FORMULA_INSTALL_ENDPOINT)

    creator, slug = name.split("/")
    zit_root = find_zit_root(Path.cwd())
    cache_path = zit_root / ".zit" / "cache" / creator / slug

    if cache_path.exists():
        shutil.rmtree(cache_path)

    while True:
        msg = json.loads(ws.recv())

        # new file arrived
        if msg.get("path") is not None:
            path, total = msg.get("path"), msg.get("total")
            size = 0

            with Progress(
                TextColumn(" " * 28),
                TextColumn(" receiving:"),
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

                progress.update(task, description=f"{path if len(path) <= 30 else ('...' + path[-27:]):<30}")

                try:
                    (cache_path / path).parent.mkdir(parents=True, exist_ok=True)
                    with (cache_path / path).open("wb") as f:
                        # receive file in chunks
                        while True:
                            chunk = ws.recv()

                            # end of file message
                            if chunk == b"EOF":
                                break

                            f.write(chunk)

                            size += len(chunk)
                            progress.update(task, completed=size)

                        if size != total:
                            raise Exception(f"File {path} not transferred correctly")

                except Exception as err:
                    logger.exception(f"Communication error: {err}")
                    return False

        # finished receiving all files
        elif msg.get("finished"):
            break

    return True


@app.command(name="install", help="Install formula")
def install(name: str, version: str, force: bool = False):
    # authentication
    if not ZITRC_FILE.exists():
        logger.warning('Key not found, please login first by "zit auth login"')
        return

    with ZITRC_FILE.open("r") as f:
        token = f.read()

    ws = create_connection(WS_FORMULA_INSTALL_ENDPOINT)
    ws.send(json.dumps({"token": token}))
    recv_msg = json.loads(ws.recv())
    authenticated = recv_msg.get("authenticated")

    if not authenticated:
        logger.warning('Invalid key, please login first by "zit auth login"')
        return

    # check if formula and version is valid in registry
    creator, slug = name.split("/")

    ws.send(json.dumps({"creator": creator, "slug": slug, "version": version}))

    recv_msg = json.loads(ws.recv())
    passed = recv_msg.get("passed")

    if not passed:
        logger.warning(recv_msg.get("reason"))
        return

    # confirm existence of remote formula and version
    version_to_install = recv_msg.get("version")
    zit_root = find_zit_root(Path.cwd())
    formula_path = zit_root / ".zit" / "formulas" / name

    # check locally
    if formula_path.is_dir():
        cfg_path = formula_path / "config.yaml"
        cfg = yaml.safe_load(cfg_path.open("rb"))

        if cfg.get("version") == version_to_install and not force:
            logger.warning(f"{name} == {version} already installed.")
            return

    if version == "latest":
        logger.info(f"installing: {name} == latest ({version_to_install})")
    else:
        logger.info(f"installing: {name} == {version}")

    # download formula to cache
    succeed = download_formula(name, version_to_install, ws)
    if not succeed:
        return

    # copy from cache to formulas
    cache_path = zit_root / ".zit" / "cache" / name
    if formula_path.exists():
        shutil.rmtree(formula_path)
    shutil.copytree(cache_path, formula_path)
    shutil.rmtree(cache_path)

    # update database
    now = datetime.now().replace(microsecond=0)
    cfg = yaml.safe_load((formula_path / "config.yaml").open("rb"))
    formula = {
        "title": cfg.get("title"),
        "slug": slug,
        "description": cfg.get("description"),
        "version": version_to_install,
        "creator": creator,
        "author": cfg.get("author"),
        "config": json.dumps(cfg.get("config")),
        "updated_at": now,
    }

    db = zit_root / ".zit" / "zit.sqlite"
    conn = sqlite3.connect(db)
    with conn:
        cur = conn.cursor()

        cur.execute("SELECT * FROM formulas WHERE creator=? AND slug=?", (creator, slug))
        rec = cur.fetchone()
        if rec is None:
            formula["installed_at"] = now
            sql = f"INSERT INTO formulas ({', '.join(list(formula.keys()))}) VALUES ({', '.join(['?']*len(formula))})"
            cur.execute(sql, list(formula.values()))

        else:
            sql = f"UPDATE formulas SET {' = ?, '.join(list(formula.keys()))} = ? WHERE id = ?"
            cur.execute(sql, list(formula.values()) + [rec[0]])

    conn.close()

    logger.info("done :)")


@app.command(name="delete", help="Delete formula")
def delete(name: str):
    zit_root = find_zit_root(Path.cwd())
    formula_path = zit_root / ".zit" / "formulas" / name

    if not formula_path.is_dir():
        logger.warning(f"{name} not installed.")
        return

    # confirm deletion
    if input(f"Are you sure you want to delete {name}? [y/N]: ").lower() != "y":
        return

    logger.info(f"deleting: {name}")

    # delete formula
    shutil.rmtree(formula_path)

    # update database
    db = zit_root / ".zit" / "zit.sqlite"
    conn = sqlite3.connect(db)
    creator, slug = name.split("/")
    with conn:
        cur = conn.cursor()

        cur.execute("SELECT * FROM formulas WHERE creator=? AND slug=?", (creator, slug))
        rec = cur.fetchone()
        if rec is not None:
            cur.execute("DELETE FROM formulas WHERE id=?", (rec[0],))
            cur.execute("DELETE FROM instances WHERE formula_id=?", (rec[0],))

    conn.close()

    # delete log
    log_file = zit_root / ".zit" / "logs" / f"{creator}" / f"{slug}.log"
    if log_file.exists():
        os.remove(log_file)

    logger.info("done :)")
