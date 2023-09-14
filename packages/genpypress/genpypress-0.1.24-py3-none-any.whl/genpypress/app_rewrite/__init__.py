import json
import logging
import pathlib
import textwrap

import cattr
from attr import define

from genpypress.app_rewrite import exceptions

logger = logging.getLogger()

logging.basicConfig(level=logging.INFO)


@define
class Rewrite:
    old_val: str
    new_val: str


@define
class Rule:
    where: str
    rules: list[Rewrite]

    def satisfies_path(self, file: pathlib.Path) -> bool:
        where = _to_norm_str(self.where)
        file = _to_norm_str(file)
        retval = where in file
        logger.debug(f"{retval=}, {where=}, {file=}")
        return retval


@define
class _MatchedFile:
    path: pathlib.Path
    rule: Rule


def _config_from_str(content: str) -> list[Rewrite] | None:
    lines = [line for line in content.split("\n") if not _is_comment(line)]
    filtered_content = "\n".join(lines)
    try:
        from_json = json.loads(filtered_content)
        config = cattr.structure(from_json, list[Rule])
    except Exception:
        raise
    return config


def create_sample_config(config_file: pathlib.Path):
    if config_file.exists():
        raise exceptions.ConfigError(f"can not create sample config, path exists: {config_file}")
    sample = textwrap.dedent(
        r"""
        # Toto je vzorový konfiguační soubor pro aplikaci ph rewrite
        # řádky uvozené mřížkou jsou komentáře, nejsou součástí konfigurace
        # konfigurace je vlastně seznamem pravidel
        [
            { 
                # where: udává, jaké soubory se přepisují
                #        název souboru se převede na lowercase, znormalizují se 
                #        zpětná lomítka (na lomítka) - a pokud název souboru OBSAHUJE
                #        text uvedený ve where, v souboru se provedou replacementy
                "where": "ppfb_cust_dn1/trf/dm01_ppfb_cust_dn1.sql",
                
                # rules: seznam pravidel
                #        každé pravidlo obsahuje "starou" hodnotu a "novou" hodnotu
                #        v souboru se provádí jednoduchá substituce, tj replacement
                #        je CASE SENSITIVE! Nepodporují se regulární výrazy.
                "rules": [
                    { 
                        "old_val" : "%AP_STG_V_LOAD_DB%.MDS_PPFB_WHITELIST",
                        "new_val" : "%AP_STG_V_LOAD_DB-DEV%.MDS_PPFB_WHITELIST"
                    },
                    {
                        "old_val" : "CT_DN1.product_code in",
                        "new_val" : "CT_DN1.product_code like any"
                    },
                    {
                        "old_val" : "'PRODC_TS_TARIFF_BUNDLE_O2_ZUSAMMEN_PPF_1'",
                        "new_val" : "'%PRODC_TS_TARIFF_BUNDLE_OPTIC_INT_HD_250_O2TV%'"
                    }
                ]
            },
            { 
                "where": "ppfb_cust_dn1/trf/another_file.sql",
                "rules": [
                    { 
                        "old_val" : "old",
                        "new_val" : "new"
                    }                    
                ]
            }
        ]
    """
    )
    config_file.write_text(sample, encoding="utf-8", errors="strict")


def read_config(config: pathlib.Path | str, encoding: str = "utf-8") -> list[Rewrite]:
    # pokud jde o instanci pathlib.Path, pokus se načíst soubor, nebo vrať None
    if isinstance(config, pathlib.Path):
        if not config.is_file():
            raise exceptions.ConfigEmptyContent
        content = config.read_text(encoding=encoding, errors="strict")
    else:
        content = config

    if not isinstance(content, str):
        raise exceptions.ConfigInvalidContentError("expected to get a string value")
    if not len(content) > 0:
        raise exceptions.ConfigInvalidContentError(f"expected to get a non zero length string {len(content)=}")

    return _config_from_str(content)


def rewrite_in_dir(config: list[Rule], directory: pathlib.Path, max_files: int):
    # sestav seznam souborů
    files = []
    for f in directory.rglob("*.*"):
        if not f.is_file():
            continue
        logger.debug(f)
        for rule in config:
            if rule.satisfies_path(f):
                logger.debug("match!")
                files.append(_MatchedFile(path=f, rule=rule))

    if len(files) > max_files:
        raise exceptions.LimitError(f"příliš mnoho kandidátů: {max_files=}, {len(files)=}")

    logger.info(f"{len(files)=}")
    for mtch in files:
        rewrite_file(mtch)


def rewrite_file(mtch: _MatchedFile, encoding: str = "utf-8"):
    old_content = mtch.path.read_text(encoding=encoding, errors="strict")
    new_content = rewrite_text(old_content, mtch.rule.rules, encoding)
    if old_content == new_content:
        logger.warning(f"no change for: {mtch.path}")
        return
    logger.info(f"WRITE: {mtch.path}")
    mtch.path.write_text(new_content, encoding=encoding, errors="strict")


def rewrite_text(old_content: str, rules: list[Rule], encoding: str = "utf-8"):
    new_content = old_content
    for r in rules:
        new_content = new_content.replace(r.old_val, r.new_val)
    return new_content


def _is_comment(line: str) -> bool:
    line = line.strip()
    if line.startswith("#"):
        return True
    if line.startswith("//"):
        return True
    return False


def _to_norm_str(path: pathlib.Path) -> str:
    if isinstance(path, pathlib.Path):
        path = str(path.absolute())
    path = path.lower()
    path = path.replace("\\", "/")
    return path
