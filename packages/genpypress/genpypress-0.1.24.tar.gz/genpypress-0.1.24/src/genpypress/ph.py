import subprocess
from pathlib import Path as _Path

import fire as _fire
from rich import traceback

from genpypress import app_cc as _app_cc
from genpypress import app_join as _app_join
from genpypress import app_patch_to_validtime as _app_patch_to_validtime
from genpypress import app_rewrite as _app_rewrite
from genpypress import app_to_async as _app_to_async

traceback.install(show_locals=False, max_frames=1)

_cwd = str(_Path.cwd())


def rewrite(directory: str = ".", config_file_name: str = "rewrite.json", max_files=20, run_press=False):
    """
    Umožní přepis souborů na základě konfigurace (rewrite.json).
    Pokud ještě konfigurační soubor neexistuje, založí ho.

    Args:
        directory (str): _description_
    """
    directory = _Path(directory)
    print(f"rewrite in: {directory=}")
    config_file = directory / config_file_name
    print(f"{config_file=}")
    try:
        config = _app_rewrite.read_config(config_file)
    except _app_rewrite.exceptions.ConfigEmptyContent as err:
        # OK, chybějící config file
        print(err)
        print(f"vytvářím vzorovový soubor: {config_file}")
        _app_rewrite.create_sample_config(config_file)
        return
    except Exception:  # chyba o které nic nevím
        raise

    project_json = directory / "project.json"
    if run_press and project_json.is_file():
        print("press run")
        subprocess.run(["press", "run"])

    # proveď přepis
    print("rewrite")
    _app_rewrite.rewrite_in_dir(config, directory, max_files)


def join(
    directory: str,
    join_to: str = "part_1.sql",
    delete: bool = True,
    mask: str = "*.sql",
    encoding: str = "utf-8",
    add_comment: bool = True,
):
    """sloučí sadu SQL souborů do jednoho, a smaže je"""
    _app_join.join_files(
        directory=directory, join_to=join_to, delete=delete, mask=mask, encoding=encoding, add_comment=add_comment
    )
    print("done")


def apatch(directory: str, limit: int = 50, encoding: str = "utf-8"):
    """apatch: patch TPT skriptů pro async stage

    Args:
        directory (str): adresář, kde jsou TPT skripty
        limit (int): kolik maximálně souborů upravit
        encoding (str): jak jsou soubory nakódované
    """
    d = _Path(directory)
    if not d.is_dir():
        print(f"toto není adresář: {directory}")
        exit(1)
    _app_patch_to_validtime.async_patch(d, limit, encoding)


def cc(
    directory: str,
    scenario: str = "drop",
    input_encoding: str = "utf-8",
    output_encoding: str = "utf-8",
    max_files: int = 20,
):
    """cc: conditional create

    Args:
        directory (str): directory where to do the work
        scenario (str): ["drop", "create", "cleanup", "drop-only"]
        input_encoding (str): Defaults to "utf-8".
        output_encoding (str): Defaults to "utf-8".
    """
    _app_cc.conditional_create(directory, scenario, input_encoding, output_encoding, max_files)


def ddl_to_async(
    folder: str,
    max_files: int = 20,
    encoding: str = "utf-8",
    default_type: str | None = None,
):
    """ddl_to_async: change DDL scripts to async stage implementaton

    Args:
        folder (str): the directory containing DDL scripts (MUST be *_LND or *_STG)
        max_files (int, optional): defaults to 20.
        encoding (str, optional): defaults to "utf-8".
        default_type (str, optional): if set, apply (s) or (i) to STG tables
    """
    _app_to_async.to_async(
        folder=folder,
        max_files=max_files,
        encoding=encoding,
        default_type=default_type,
    )


def _main():
    _fire.Fire()


if __name__ == "__main__":
    _main()
