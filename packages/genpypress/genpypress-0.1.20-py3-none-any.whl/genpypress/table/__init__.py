import json
import subprocess
import sys
from pathlib import Path

import cattr
from attrs import define, field

__SUPPORTED_PLATFORMS__ = ["win32"]

assert sys.platform in __SUPPORTED_PLATFORMS__, f"unsupported platform: {sys.platform}"

_bin_dir = Path(__file__).parent / "_bin"
_table2json = _bin_dir / "table2json.exe"
assert _table2json.is_file(), f"panic: jsonizer is not installed?: {_table2json}"


@define
class Rules:
    keys: list[str] = field(default=list())
    map: dict[str, str] = field(default=dict())


@define
class Column:
    name: str = field(default="")
    comment: str = field(default="")
    primary: bool = field(default=False)
    mandatory: bool = field(default=False)
    data_type: str = field(default="")
    data_type_base: str = field(default="")
    scale: int = field(default=None)
    precission: int = field(default=None)
    is_derived: bool = field(default=False)
    is_derived_from: str = field(default=None)
    is_derived_to: str = field(default=None)
    is_validtime: bool = field(default=False)
    is_volatile: bool = field(default=False)
    is_transactiontime: bool = field(default=False)
    compress: str = field(default="")
    character_set: str = field(default="")
    case_specific: bool = field(default=False)
    etl_src_not_available: bool = field(default=False)
    etl_crc_format: str = field(default="")
    etl_src_header: str = field(default="")
    etl_src_size_in_bytes: int = field(default=0)
    rules: Rules = field(default=Rules())
    cdc_src_column: str = field(default="")
    cdc_src_data_type: str = field(default="")
    cdc_src_scale: int = field(default=0)


@define
class Table:
    database: str = field(default="")
    name: str = field(default="")
    comment: str = field(default="")
    set_or_multiset: str = field(default="")
    columns: list[Column] = field(default="")
    pi_name: str = field(default=None)
    pi_is_upi: bool = field(default=False)
    pi_columns: list[str] = field(default=list())
    pi_partitions: str = field(default=None)
    pi_isolated_loading: bool = field(default=False)

    def __getitem__(self, key) -> Column:
        if isinstance(key, int):
            return self.columns[key]
        assert isinstance(key, str), f"key is not a str: {key.__class__.__name__}"
        for c in self.columns:
            if c.name.casefold() == key.casefold():
                return c
        raise KeyError(f"{key}: not found in {self.name}")

    def __setitem__(self, key, val) -> None:
        assert isinstance(val, Column), f"expected a column instance, got {val.__class__.__name__}"
        if isinstance(key, int):
            self.columns.insert(key, val)
            return
        self.columns.append(val)

    def ___del_from_pi___(self, name: str):
        pos = None
        for i, c in enumerate(self.pi_columns):
            if c.casefold() == name:
                pos = i
                break
        if pos is not None:
            del self.pi_columns[pos]

    def __delitem__(self, name_or_index: int | str | Column):
        colname = None
        if isinstance(name_or_index, Column):
            colname = name_or_index.name.casefold()
        elif isinstance(name_or_index, str):
            colname = name_or_index.casefold()

        if colname:
            pos = -1
            for i, c in enumerate(self.columns):
                if c.name.casefold() == colname:
                    pos = i
                    break
            if pos == -1:
                raise IndexError(f"column not found in {self.name}: {colname}")

            self.___del_from_pi___(colname)
            del self.columns[pos]
            return

        if isinstance(name_or_index, int):
            self.___del_from_pi___(self.columns[name_or_index].name)
            del self.columns[name_or_index]
            return

        raise ValueError(f"expected to get one of int, str, Columns, got: {name_or_index.__class__.__name__}")

    def __len__(self) -> int:
        return len(self.columns)

    def __iter__(self):
        return self.columns.__iter__()

    def __contains__(self, item):
        colname = None
        if isinstance(item, Column):
            colname = item.name
        elif isinstance(item, str):
            colname = item
        assert colname, f"expected to get one of str, Column, got: {item.__class__.__name__}"
        for c in self.columns:
            if c.name.casefold() == colname.casefold():
                return True
        return False

    def __reversed__(self):
        return self.columns.__reversed__()


def from_file(filename: str | Path, timeout_seconds=2) -> list[Table] | Table:
    """returns a list of Table instances parsed from DDL script.

    Args:
        filename (str | Path): path to the script
        timeout_seconds (int, optional): safeguard; the parser can freeze on invalid DDL,
            therefore it will be allowed to run only for limited time.
            After the limite it will be killed (and exception will be raised).
    Raises:
        subprocess.TimeoutExpired: signifies that the DDL is likely invalid.
        subprocess.CalledProcessError: signifies that the DDL is likely invalid.

    Returns:
        list[Table] | Table: list of table instances (if found)
    """
    if isinstance(filename, str):
        filename = Path(filename)
    assert isinstance(filename, Path), f"filename: not a path: {filename.__class__.__name__}"
    filename = filename.resolve()
    assert filename.is_file(), f"filename: does not exist {filename}"

    jsonizer = [str(_table2json), "-file", str(filename)]

    # check_output raises CalledProcessError on non-zero exit status as specified in the question's text unlike proc.communicate() method.
    #
    try:
        output_bytes = subprocess.check_output(jsonizer, stderr=subprocess.STDOUT, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        raise subprocess.TimeoutExpired(
            f"timeout: {_table2json.name} did not finish in under {timeout_seconds} seconds: check the file {filename}"
        )
    except subprocess.CalledProcessError:
        raise subprocess.CalledProcessError(f"error: {_table2json.name} returned error, check the file {filename}")

    # get the json
    output_string = output_bytes.decode("utf-8")
    # get the table
    tables_list = json.loads(output_string)
    tables = cattr.structure(tables_list, list[Table])
    if len(tables) == 1:
        return tables[0]
    return tables
