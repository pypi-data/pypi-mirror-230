from pathlib import Path


_cwd = str(Path.cwd())


class JoinError(ValueError):
    def __init__(self, message) -> None:
        super().__init__(message)


def join_files(
    directory: str = _cwd,
    join_to: str = "part_1.sql",
    delete: bool = True,
    mask: str = "*.sql",
    encoding: str = "utf-8",
    add_comment: bool = True,
):
    """sloučí sadu souborů do jednoho

    Args:
        directory (str): složka kde se sloučení má provést (default=.)
        join_to (str): název cílového souboru ("part_1.sql").
        delete (bool): True znamená, že se zdrojové soubory mají smazat
        mask (str): maska souborů ("*.sql").
        encoding (str): kódování ("utf-8".)

    Raises:
        JoinError: pokud se něco nepovede.
    """
    tgt_dir = Path(directory)
    if not tgt_dir.is_dir():
        raise JoinError(f"toto není adresář: {directory=}")

    tgt_file = tgt_dir / join_to
    if tgt_file.is_file():
        raise JoinError(f"cílový soubor již existuje: {tgt_file=}")

    files = [f for f in tgt_dir.glob(mask) if f.is_file()]
    content = [(f.name, f.read_text(encoding=encoding, errors="strict")) for f in files]

    with tgt_file.open("w", encoding=encoding, errors="strict") as h:
        for filename, insides in content:
            if add_comment:
                h.write(f"/* {filename}*/\n")
            h.write(insides)
            h.write("\n\n")

    for f in files:
        f.unlink()
