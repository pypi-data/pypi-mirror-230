import pathlib
from typing import Callable

_cwd = str(pathlib.Path.cwd())

COPY_TO_PKG = "--+ +rule.packaging.copy = true"
STAGE = "AP_STG"
LANDING = "AP_LND"
EP_LND = "EP_LND"
EP_STG = "EP_STG"

_OLD_LND_TECH_COLS = ["upd_dttm", "extract_dttm", "hash_val", "load_id"]
_OLD_STG_TECH_COLS = [
    "load_id",
    "active_flag",
    "load_id",
    "ins_dttm",
    "load_dttm",
    "extract_dttm",
    "hash_val",
    "upd_dttm",
]
LAYERS = {
    "AP_LND": LANDING,
    "AP_STG": STAGE,
    EP_LND: LANDING,
    EP_STG: STAGE,
}

AP_LND_TECH_COLS = [
    f"      {c}"
    for c in [
        "-- technické sloupce AP_LND vrstvy ------------------------",
        "hash_val VARCHAR(32) CHARACTER SET LATIN,",
        "file_name VARCHAR(1024) CHARACTER SET LATIN NOT NULL,",
        "load_id INTEGER DEFAULT -1,",
        "job_id   INTEGER DEFAULT -1,",
        "extract_dttm TIMESTAMP(0)",
    ]
]

AP_STG_TECH_COLS_s = [
    f"      {c}"
    for c in [
        "--- technické sloupce AP_STG vrstvy STAV-------------------------------------",
        "hash_val CHAR(32) CHARACTER SET LATIN,",
        "start_dttm TIMESTAMP(0) NOT NULL,",
        "end_dttm TIMESTAMP(0) NOT NULL,",
        "PERIOD FOR vt_per  (start_dttm, end_dttm) AS VALIDTIME,",
        "load_id INTEGER NOT NULL,",
        "job_id INTEGER NOT NULL,",
        "active_flag CHAR(1) CHARACTER SET LATIN",
    ]
]

AP_STG_TECH_COLS_i = [
    f"      {c}"
    for c in [
        "--- technické sloupce AP_STG vrstvy INCR-------------------------------------",
        "extract_dttm TIMESTAMP(0) NOT NULL,",
        "loaded_dttm TIMESTAMP(0) NOT NULL,",
        "load_id INTEGER NOT NULL,",
        "job_id INTEGER NOT NULL",
    ]
]

AP_STG_TECH_COLS = {"i": AP_STG_TECH_COLS_i, "s": AP_STG_TECH_COLS_s}

MAGICAL_MARKER = "--*-- automatic conversion by genpypress"
MAGIC_COMMENT_START = "/*+"
COMMENT_END = "*/"


class _NextIteration(StopIteration):
    pass


def to_async(
    folder: str,
    max_files: int = 20,
    encoding: str = "utf-8",
    default_type: str | None = None,
):
    p_folder = pathlib.Path(folder)
    files = list(p_folder.rglob("*.sql"))
    files.extend(list(p_folder.rglob("*.bteq")))

    if len(files) > max_files:
        raise ValueError(f"got {len(files)}, expected {max_files=}")

    for f in files:
        print(f)
        file_to_async(f, encoding=encoding, default_type=default_type)


def _as_lnd(
    content: str,
    file_name: str | None = None,
    *args,
    **kwargs,
) -> str:
    # nedělej dvakrát stejnou úpravu, protože to asi dopadne špatně
    if MAGICAL_MARKER in content:
        return content

    lines = content.split("\n")
    out_lines = []
    skip_stats, skip_tech_cols, seen_index, magic_block = False, False, False, False
    for line in lines:
        stripped_line = line.strip().lower()

        # pokud řádek přepíná databázi, skip
        if stripped_line.startswith("database "):
            continue

        # korekce magických komentářů
        if MAGIC_COMMENT_START in stripped_line:
            magic_block = True
            line = line.replace(MAGIC_COMMENT_START, "")
            stripped_line = line.strip().lower()
        if magic_block:
            if stripped_line.startswith("+"):
                line = " ".join(["--+", line.strip()])
            if stripped_line.endswith(COMMENT_END):
                line = line.replace(COMMENT_END, "")
                magic_block = False

        # pokud řádek definuje statistiky, skip
        if stripped_line.startswith("collect "):
            skip_stats = True
            continue
        if skip_stats:
            if stripped_line.endswith(";"):
                skip_stats = False
            continue

        # pokud řádek je comment, nebo create, odstraň databázi
        # a znormalizuj na MULTISET tabulku
        line = _remove_database(line, stripped_line=stripped_line, database=EP_LND)

        # pokud je řádek comment, a je na technickém slouci, skip
        try:
            if stripped_line.startswith("comment on column"):
                for c in _OLD_LND_TECH_COLS:
                    if f".{c} is '" in stripped_line:
                        raise _NextIteration
        except _NextIteration:
            continue

        # pokud řádek definuje první technický sloupec, doplň novou definici
        # a skip až do indexu
        if _is_lnd_tech_column(stripped_line):
            skip_tech_cols = True
            continue
        if skip_tech_cols and _is_primary_index(stripped_line):
            skip_stats, seen_index = False, True
            out_lines.extend(AP_LND_TECH_COLS)
            out_lines.extend(")")

        # pokud je řádek "PARTITIN BY" na indexu tak ho přeskoč (doplň středník)
        if seen_index and stripped_line.startswith("partition by"):
            out_lines.append(";")
            continue
        # korekce magickýxh komentářů
        # alert zóny jsou nesmyslné, a engine_id je 9
        if "+SrcAlertZone" in line:
            continue
        if "+SrcEngineID" in line:
            line = "--+ +SrcEngineID = 9"
        elif "+SrcExtractDttmMask" in line:
            line = line.replace(" 00:00:00", " 23:59:59")
        out_lines.append(line)

    # doplň automarker
    out_lines.extend(
        [
            COPY_TO_PKG,
            MAGICAL_MARKER,
            "",
        ]
    )
    return "\n".join(out_lines)


def _ask(
    prompt: str,
    *,
    default: str | None = None,
    to_lower: bool = True,
    valid_choices: list | None = None,
) -> str:
    """show the prompt and ask for a value"""
    _prompt = prompt if prompt.endswith(" ") else f"{prompt} "
    if valid_choices:
        _prompt = _prompt + f"[{'/'.join(valid_choices)}]"
    if default:
        _prompt = _prompt + f": {default=} "

    while True:
        retval = input(_prompt).strip()
        if default and retval == "":
            retval = default
        if valid_choices:
            if retval in valid_choices:
                return retval
            continue
        return retval


def _as_stg(
    content: str,
    *,
    prompt_func: Callable = _ask,
    file_name: str | None = None,
    default_type: str | None = None,
    **kwargs,
) -> str:
    # nedělej dvakrát stejnou úpravu, protože to asi dopadne špatně
    if MAGICAL_MARKER in content:
        return content

    # potřebujeme správný set auditních sloupců, doptáme se jaký chceme použít
    prompt = f"soubor {file_name}: auditní sloupce stav(s) nebo inkrement(i)?"
    if default_type:
        assert default_type in ["s", "i"]
        _typ = default_type
    else:
        _typ = prompt_func(prompt, default="s", valid_choices=["s", "i"], to_lower=True)

    audit_columns = AP_STG_TECH_COLS[_typ]

    lines = content.split("\n")
    out_lines = []
    skip_stats, skip_tech_cols, seen_index, magic_block = False, False, False, False
    pk_cols = None

    for line in lines:
        stripped_line = line.strip().lower()

        # pokud řádek přepíná databázi, skip
        if stripped_line.startswith("database "):
            continue

        # korekce magických komentářů
        if MAGIC_COMMENT_START in stripped_line:
            magic_block = True
            line = line.replace(MAGIC_COMMENT_START, "")
            stripped_line = line.strip().lower()
        if magic_block:
            if stripped_line.startswith("+"):
                line = " ".join(["--+", line.strip()])
            if stripped_line.endswith(COMMENT_END):
                line = line.replace(COMMENT_END, "")
                magic_block = False

        # pokud řádek definuje statistiky, skip
        if stripped_line.startswith("collect "):
            skip_stats = True
            continue
        if skip_stats:
            if stripped_line.endswith(";"):
                skip_stats = False
            continue

        # pokud řádek je comment, nebo create, odstraň databázi
        line = _remove_database(line, stripped_line=stripped_line, database=EP_STG)

        # pokud je řádek comment, a je na technickém slouci, skip
        try:
            if stripped_line.startswith("comment on column"):
                for c in _OLD_STG_TECH_COLS:
                    if f".{c} is '" in stripped_line:
                        raise _NextIteration
        except _NextIteration:
            continue

        # pokud řádek definuje první technický sloupec, doplň novou definici
        # a skip až do indexu
        if _is_stg_tech_column(stripped_line):
            skip_tech_cols = True
            continue
        if skip_tech_cols and _is_primary_index(stripped_line):
            if pk_cols is None:
                pk_cols = _get_list_of_columns(stripped_line)
            skip_stats, seen_index = False, True
            out_lines.extend(audit_columns)
            out_lines.extend(")")

        # pokud je řádek "PARTITIN BY" na indexu tak ho přeskoč (doplň středník)
        if seen_index and stripped_line.startswith("partition by"):
            pass
            # TODO(really?) - předpokládám že nepotřebuju přeskakovat partition klauzuli
            # out_lines.append(";")
            # continue
        # korekce magickýxh komentářů
        # alert zóny jsou nesmyslné, a engine_id je 9
        if "+SrcAlertZone" in line:
            continue
        if "+SrcEngineID" in line:
            line = "--+ +SrcEngineID = 9"
        elif "+SrcExtractDttmMask" in line:
            line = line.replace(" 00:00:00", " 23:59:59")
        out_lines.append(line)

    # pokud jde o stavovou tabulku, označ sloupce primárního indexu za primární klíč
    if _typ == "i" and pk_cols:
        out_lines.append("")
        for col in pk_cols:
            out_lines.append(f"--+ +column.{col}.primary = true")
        out_lines.append("")

    # doplň automarker
    out_lines.extend([COPY_TO_PKG, MAGICAL_MARKER, ""])
    return "\n".join(out_lines)


def _get_list_of_columns(line: str) -> list[str] | None:
    empty = []
    # co je před závorkou je definice indexu
    before, sep, after = line.partition("(")
    if sep == "":
        return empty
    # co je před závorkou je seznam sloupců
    before, sep, after = after.partition(")")
    if sep == "":
        return empty
    columns = [c.strip() for c in before.split(", ")]
    return columns


def _is_primary_index(stripped_line: str) -> bool:
    return stripped_line.startswith("primary index") or stripped_line.startswith("unique primary index")


def _is_stg_tech_column(stripped_line: str) -> bool:
    for col in _OLD_STG_TECH_COLS:
        _col = f"{col} "
        if stripped_line.startswith(_col):
            return True
    return False


def _is_lnd_tech_column(stripped_line: str) -> bool:
    for col in _OLD_LND_TECH_COLS:
        _col = f"{col} "
        if stripped_line.startswith(_col):
            return True
    return False


def _remove_database(line: str, *, stripped_line: str, database: str):
    if not (stripped_line.startswith("create ") or stripped_line.startswith("comment ")):
        return line
    return line.replace(f"{database}.", "").replace(" SET TABLE", " MULTISET TABLE")


CALLBACKS = {LANDING: _as_lnd, STAGE: _as_stg}


def file_to_async(
    f: pathlib.Path,
    encoding: str = "utf-8",
    default_type: str | None = None,
):
    """Open the file, and correct it to the correct layer

    Args:
        f (pathlib.Path): _description_
    """
    ph = f.parent.name.upper()
    if ph not in LAYERS:
        err = "\n".join(
            [
                "PROBLEM:  Can not determine if this is stage or landing layer.",
                "SOLUTION: The file needs to be in a subdir which represents the database",
                "FILE:     %s" % str(f),
            ]
        )
        raise ValueError(err)

    # read the file and get new content
    content = f.read_text(encoding=encoding)
    func = CALLBACKS[LAYERS[ph]]
    new_content = func(content, file_name=f"{f.parent.name}/{f.name}", default_type=default_type)
    if new_content != content:
        print("...write")
        f.write_text(new_content, encoding=encoding)


if __name__ == "__main__":
    for line in ["COMMENT ON COLUMN OCS_BALANCE_EXPIRY_BAL.hash_val IS 'Audit column - MD5 hash for this record';"]:
        stripped_line = line.strip().lower()
        if stripped_line.startswith("comment on column"):
            for c in _OLD_STG_TECH_COLS:
                print(f"{c}")
                if f".{c} is '" in stripped_line:
                    raise ValueError
                    continue
            print(stripped_line)
