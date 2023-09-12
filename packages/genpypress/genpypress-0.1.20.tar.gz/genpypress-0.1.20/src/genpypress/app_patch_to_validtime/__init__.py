from collections import namedtuple
from pathlib import Path
import re

LastStatementLine = namedtuple("LastStatementLine", "line_no,offset")
_UTF8 = "UTF-8"


class PatchError(ValueError):
    """PatchError: chyba patch procesu"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def async_patch(directory: Path, limit: int = 50, encoding: str = "utf-8"):
    """provede patch TPT skriptů v kontextu použití asynchronní stage"""
    # sestav seznam souborů
    files = list(directory.rglob("*.tpt"))
    if len(files) == 0:
        raise PatchError(f"Nula souborů na vstupu: directory={str(directory)}")
    if len(files) > limit:
        raise PatchError(
            f"Více souborů než jsme čekali.\n- {limit=}\n- {len(files)=}\n- directory={str(directory)}"
            + "\n\nPoužij parametr --limit, pokud chceš limit zvednout."
        )

    # projdi soubor za souborem, seber si informaci o tom kde jsme měli úspěch a kde problém
    problems = []
    for f in files:
        relpath = f.relative_to(directory)
        try:
            script = f.read_text(encoding=encoding, errors="strict")
        except UnicodeError:
            problems.append((relpath, "UnicodeError, oprav kódování a zkus to znovu"))
            continue

        try:
            new_script = _patch_text(script)
        except PatchError as e:
            problems.append((relpath, f"PatchError: {e.message}"))
            continue

        if new_script == script:
            continue

        try:
            f.write_text(new_script, encoding=encoding, errors="strict")
        except Exception as e:
            problems.append((relpath, f"{e}"))

    if len(problems) > 0:
        for p in problems:
            file, problem = p
            print(f"{str(file)}: {problem}")
    else:
        print("ALL OK!")


def _patch_text(text: str):
    lines = text.split("\n")

    # historicky jsme měli skripty označené jako nakódované v ANSI nebo v UTF-16, korekce na UTF-8
    line_using_charset = tpt_line_with_using_character_set(lines)
    if line_using_charset:
        lines[line_using_charset.position] = line_using_charset.text

    # nejdříve si najdeme potřebné pozice - následující MUSÍM mít k dispozici vždy
    i_apply = tpt_line_with_apply(lines)
    i_insert = tpt_line_with_insert(lines)
    i_operator = tpt_line_with_to_operator(lines)
    last_stmt = tpt_line_with_semicolon_above_operator(lines, i_operator)

    # následující můžu a nemusím mít k dispozici
    io_set_session = tpt_line_with_set_session(lines)
    io_restart_prm = tpt_line_with_restart_param(lines, i_operator)
    io_password = tpt_line_with_password(lines, i_operator)

    # pokud již ve skriptu JE set session validtime, končíme a nic neděláme
    if io_set_session > -1:
        return text

    # jinak musíme provést patch
    out_lines = lines.copy()

    # pokud je na řádku s APPLY apostrof, musíme ho "zasmrtit", ale současně ho musíme dodat za SET SESSION VALIDTIME
    i_apply_apostrof = ""
    if "'" in out_lines[i_apply]:
        if out_lines[i_apply].count("'") > 1:
            raise PatchError(f"na řádce s APPLY je víc apostrofů než jeden: {out_lines[i_apply]}")
        i_apply_apostrof = "\n          '\n"
        out_lines[i_apply] = out_lines[i_apply].replace("'", "")

    # řádek, kde je APPLY, obohatíme o SET SESSION VALIDTIME
    # to musíme udělat vždy - set session ve skriptu není (jinak bychom ho vrátili bez úprav)
    out_lines[i_apply] = (
        out_lines[i_apply]
        + "\n          'SET SESSION VALIDTIME AS OF TIMESTAMP ''%LOAD_DT% 23:59:59'';'"
        + "\n          ,"
        + i_apply_apostrof
    )

    # řádek, kde je insert, musíme zabalit do SELECT * FROM (
    # poslední statement musíme zakončit na ) as T
    # ale jen opkud prní select není SELECT * FROM
    if not tpt_is_first_select_star(lines):
        out_lines[i_insert] = out_lines[i_insert] + "\n          SELECT * FROM ("
        out_lines[last_stmt.line_no] = (
            out_lines[last_stmt.line_no][: last_stmt.offset]
            + "\n          ) as T\n"
            + out_lines[last_stmt.line_no][last_stmt.offset :]
        )

    # pokud ještě nemáme  RestartAtFirstDmlGFroup, doplnit
    if io_restart_prm == -1:
        if io_password == -1:
            raise PatchError("""nenašel jsem řádek, kde je "UserPassword" parametr na úrovni TO OPERATOR""")
        out_lines[io_password] = out_lines[io_password] + "\n             " + """, "RestartAtFirstDMLGroup" = 'Yes'"""

    # doplň prázdný řádek, pokud na konci není
    if len(out_lines[-1]) > 0:
        out_lines.append("")

    # vrať zpátky upravený skript ...
    return "\n".join(out_lines)


def tpt_is_first_select_star(in_lines: list[str]) -> bool:
    for line in in_lines:
        line = line.upper().lstrip(",' ")
        line = "".join(line.split(" "))
        if line.startswith("SELECT"):
            if line.startswith("SELECT*FROM"):
                return True
            return False
    raise PatchError("failed to get the select")


def _list_contains_another(list1, list2):
    """Returns True if list1 is contained in list2, False otherwise."""
    for e1, e2 in zip(list1, list2):
        if e1 != e2:
            return False
    return True


LineWithEncoding = namedtuple("LineWithEncoding", "position,text")


def tpt_line_with_using_character_set(in_lines: list[str]) -> LineWithEncoding | None:
    """vrací čádek kde je characterset, a normalizuje ho na utf-8"""
    line_no = -1
    counter = 0
    for line in in_lines:
        line = line.strip(" ").upper()
        elements = re.split(r"\s+", line)
        if _list_contains_another(elements, ["USING", "CHARACTER", "SET"]):
            line_no = counter
            break
        counter = counter + 1

    replacements_from = ["LATIN1250_1A0", "UTF16"]
    if line_no > -1:
        line = in_lines[line_no].upper()
        for r in replacements_from:
            line = line.replace(r, _UTF8)
        return LineWithEncoding(position=line_no, text=line)
    return None


def tpt_line_with_apply(in_lines: list[str]) -> int:
    """vrací pozice řádek, kde je APPLY"""
    lines = []
    for i, line in enumerate(in_lines):
        if line.strip("' ").upper() == "APPLY":
            lines.append(i)

    if len(lines) == 0:
        raise PatchError("Nenašel jsem řádek, kde by byl APPLY statement.")
    if len(lines) > 1:
        raise PatchError(f"Příliš mnoho řádků, kde je APPLY: {lines=}")
    return lines[0]


def tpt_line_with_insert(in_lines: list[str]) -> int:
    """vrací pozice řádek, kde je INSERT"""
    lines = []
    for i, line in enumerate(in_lines):
        line = line.replace("'", "").strip().removeprefix(",").strip().upper()
        if line.startswith("INSERT") and "INTO" in line:
            lines.append(i)

    if len(lines) == 0:
        raise PatchError("Nenašel jsem řádek, kde by byl INSERT statement.")
    if len(lines) > 1:
        raise PatchError(f"Příliš mnoho řádků, kde je insert: {lines=}")
    return lines[0]


def tpt_line_with_to_operator(in_lines: list[str]) -> int:
    """vrací pozice řádek, kde je TO OPERATOR"""
    lines = []
    for i, line in enumerate(in_lines):
        line = line.upper().strip()
        if line == "TO OPERATOR":
            lines.append(i)

    if len(lines) == 0:
        raise PatchError("Nenašel jsem řádek, kde by byl INSERT statement.")
    if len(lines) > 1:
        raise PatchError(f"Příliš mnoho řádků, kde je insert: {lines=}")
    return lines[0]


def tpt_line_with_semicolon_above_operator(in_lines: list[str], line_with_to_operator: int) -> LastStatementLine:
    """
    funkce vrací tupple LastStatementLine
    - .line_no - číslo řádku, kde končí poslední statement nad TO OPERATOR
    - .offset - offset, na kterém je středník, nebo apostrof ... tj kde je ukončený statement
    """
    last_statement_line = -1
    for i, line in enumerate(in_lines):
        line = line.replace(" ", "")
        if line == ";'" or line == "'":
            if i > last_statement_line and i <= line_with_to_operator:
                last_statement_line = i
        if i > line_with_to_operator:
            break
    if last_statement_line == -1:
        raise PatchError(
            f"""Nenašel jsem řádek, který by byl nad `TO OPERATOR`, a který by končil středníkem nebo apostrofem.
        Číslo řádku : {line_with_to_operator = }"""
        )

    offset_apostrof = in_lines[last_statement_line].rfind(";")
    if offset_apostrof == -1:
        offset_apostrof = in_lines[last_statement_line].rfind("'")
    if offset_apostrof == -1:
        raise PatchError(f"Na řádce {last_statement_line=} jsem nenašel ani středník ani apostrof")

    return LastStatementLine(line_no=last_statement_line, offset=offset_apostrof)


def tpt_line_with_set_session(in_lines: list[str]) -> int:
    """vrací pozice řádek, kde je SET SESSION VALIDTIME, nebo -1"""
    lines = []
    for i, line in enumerate(in_lines):
        line = line.strip().upper()
        if "SET SESSION VALIDTIME" in line:
            lines.append(i)

    if len(lines) > 1:
        raise PatchError(f"Příliš mnoho řádků, kde je SET SESSION VALIDTIME: {lines=}")

    if len(lines) == 0:
        return -1

    return lines[0]


def tpt_line_with_restart_param(in_lines: list[str], to_operator_line: int) -> int:
    """vrací pozice řádek, kde je RestartAtFirstDMLGroup, nebo -1"""
    lines = []
    for i, line in enumerate(in_lines):
        line = line.strip().upper()
        if "RESTARTATFIRSTDMLGROUP" in line and i > to_operator_line:
            lines.append(i)

    if len(lines) > 1:
        raise PatchError(f"Příliš mnoho řádků, kde je RestartAtFirstDMLGroup: {lines=}")

    if len(lines) == 0:
        return -1

    return lines[0]


def tpt_line_with_password(in_lines: list[str], to_operator_line: int) -> int:
    """vrací pozice řádek, kde je RestartAtFirstDMLGroup, nebo -1"""
    lines = []
    for i, line in enumerate(in_lines):
        line = line.strip().upper()
        if "USERPASSWORD" in line and i > to_operator_line:
            lines.append(i)

    if len(lines) > 1:
        raise PatchError(f"Příliš mnoho řádků, kde je UserPassword: {lines=}")

    if len(lines) == 0:
        return -1

    return lines[0]
