import re
from typing import Optional
from collections import namedtuple
from attrs import define, field

BACKTICKS = "```"

KeyAndVal = namedtuple("KeyAndVal", "key val")


class ParsingError(ValueError):
    def __init__(self, message):
        super().__init__(message)


@define
class ColumnMapping:
    column: str
    mapped_to: str = field(default="")
    transformation_rule: str = field(default="")
    comment: str = field(default="")


@define
class Mapping:
    model: str
    data_source: str
    table: str
    name: str

    mapped_to: list[str] = field(factory=list)
    comment: Optional[str] = field(default=None)

    etl_historization: Optional[str] = field(default=None)
    etl_matching_rules: list[str] = field(factory=list)
    etl_main_source: Optional[str] = field(default=None)
    etl_referenced_sources: Optional[str] = field(default=None)
    etl_filter_criterion: Optional[str] = field(default=None)
    etl_active_flag: Optional[str] = field(default=None)
    etl_groupping: Optional[str] = field(default=None)
    etl_calendar: Optional[str] = field(default=None)

    etl_before_insert: Optional[str] = field(default=None)
    etl_after_insert: Optional[str] = field(default=None)

    column_mappings: list[ColumnMapping] = field(factory=list)
    attached_rules: list[str] = field(factory=list)
    etl_prep_steps: list[str] = field(factory=list)
    etl_post_steps: list[str] = field(factory=list)

    def __getitem__(self, key):
        col_name = key.lower()
        for cm in self.column_mappings:
            if col_name == cm.column.lower():
                return cm
        raise KeyError(f"column is not mapped: {key}")


def _split(line: str) -> list[str]:
    return re.split(r"[, \n\t]+", line)


def filter_keep_code(lines: list[str]) -> list[str]:
    """
    filter_keep_code: only keep those lines of the text, that are enclosed by backticks

    Args:
        lines (list[str]): lines of text

    Returns:
        list[str]: filtered lines of text

    Throws:
        ParsingException if a code block is not finished.
    """
    in_code = False
    in_skipped_code = False
    result = []
    open_line, at_line = 0, 0

    for line in lines:
        at_line += 1
        stripped_line = line.strip()

        if stripped_line.startswith("# Parse errors"):
            break

        if line.strip() == BACKTICKS:
            if in_skipped_code:
                in_skipped_code = False
            else:
                in_code = not in_code
            if in_code:
                open_line = at_line
            continue

        if stripped_line.startswith(BACKTICKS):
            in_skipped_code = True
            continue

        if not in_code:
            continue
        if stripped_line.startswith("#"):
            continue

        result.append(line)
    if in_code:
        raise ParsingError(f"Problem at line {open_line}: code block is not closed")
    return result


def _is_key_val_property(line: str, throws_on_fail=False) -> Optional[KeyAndVal]:
    line = line.strip()

    try:
        position = line.index("=")
    except ValueError:
        if throws_on_fail:
            raise ParsingError(f"input line is not a key value property: {line}")
        return None

    k = line[:position].upper().strip()
    v = line[(position + 1) :].strip()
    return KeyAndVal(key=k, val=v)


def _is_in_square_brackets(line: str) -> Optional[KeyAndVal]:
    """
    returns the tuple KeyAndVal, if the line is in square brackets.
    throws ParsingError if the tuple is not separated by equal sign

    Args:
        line (str): _description_

    Returns:
        Optional[KeyAndVal]: _description_
    """
    line = line.strip()
    if not (line.startswith("[") and line.endswith("]")):
        return None
    line = line[1:-1]  # strip brackets
    return _is_key_val_property(line, throws_on_fail=True)


def from_markdown(text: str, filter=filter_keep_code) -> Mapping:
    """
    Parses a markdown file and returns mapping.

    Args:
        text (str): _description_
        filter (_type_, optional): _description_. Defaults to filter_keep_code.
    """
    lines = text.split("\n")
    in_multiline = False
    colmap: Optional[ColumnMapping] = None
    line_buffer = []
    property = ""

    ret_map = Mapping(model="", data_source="", table="", name="")
    lines = filter_keep_code(lines)
    for line in lines:
        stripped_line = line.strip()

        if not in_multiline:
            # skip empty lines and comments
            if stripped_line == "":
                continue

            # accept change of context
            ctx_change = _is_in_square_brackets(stripped_line)
            if ctx_change:
                match ctx_change.key:
                    case "MODEL":
                        ret_map.model = ctx_change.val
                    case "TABLE":
                        ret_map.table = ctx_change.val
                    case "DATA_SOURCE":
                        ret_map.data_source = ctx_change.val
                    case "MAPPING":
                        ret_map.name = ctx_change.val
                    case "COLUMN":
                        colmap = ColumnMapping(column=ctx_change.val)
                        ret_map.column_mappings.append(colmap)
                    case "BUSINESS_RULE":
                        ret_map.attached_rules.append(ctx_change.val)
                continue

            # should be a key/val property then ...
            kv = _is_key_val_property(line)
            if not kv:
                raise ParsingError(f"line should be key/val property: {line}")

            # might be a multiline property ....
            # in that case, keep everything after the arrow
            property = kv.key
            skv: str = kv.val.strip()
            if skv.startswith("->"):
                skv = skv.removeprefix("->").strip()
                if skv != "":
                    line_buffer.append(skv)
                in_multiline = True
                continue
        else:
            if stripped_line != "<-":
                line_buffer.append(line)
                continue
            else:
                in_multiline = False

        if property == "":
            raise ParsingError(f"internal error: property is not set: line={line}")

        # store what you have
        if len(line_buffer) > 0:
            stored_value = "\n".join(line_buffer)
        else:
            stored_value = kv.val.lstrip()

        # if column_mapping exists, we are modifying the column mapping
        if colmap and colmap.column != "":
            match property:
                case "MAPPED_TO":
                    colmap.mapped_to = stored_value
                case ("TO2_PDM_EDW.ETL_TRANSFORMATION_RULE" | "TO2_PDM_EDW.ETL_TRANSFORMATION_RULES"):
                    colmap.transformation_rule = stored_value
                case "COMMENT":
                    colmap.comment = stored_value
                case _:
                    raise ParsingError(f"unknown property for column mapping {colmap.column}: {property}")

            line_buffer = []
            continue

        # otherwise it is a table property
        match property:
            case "MAPPED_TO":
                ret_map.mapped_to = sorted(_split(stored_value))

            case "COMMENT":
                ret_map.comment = stored_value
            case "TO2_PDM_EDW.ETL_HISTORIZATION":
                ret_map.etl_historization = stored_value
            case "TO2_PDM_EDW.ETL_MATCHING_RULES":
                ret_map.etl_matching_rules = sorted(_split(stored_value))
            case "TO2_PDM_EDW.ETL_MAIN_SOURCE":
                ret_map.etl_main_source = stored_value
            case "TO2_PDM_EDW.ETL_REFERENCED_SOURCES":
                ret_map.etl_referenced_sources = stored_value
            case "TO2_PDM_EDW.ETL_FILTER_CRITERION":
                ret_map.etl_filter_criterion = stored_value
            case "TO2_PDM_EDW.ETL_TRANSFORMATION_ALGORITHM":
                ret_map.etl_groupping = stored_value
            case "TO2_PDM_EDW.ETL_TRANSFORMATION_RULES":
                ret_map.etl_active_flag = stored_value
            case "TO2_PDM_EDW.ETL_CALENDAR":
                ret_map.etl_calendar = stored_value
            case "TO2_PDM_EDW.ETL_PREP_STEP":
                ret_map.etl_prep_steps.append(stored_value)
            case "TO2_PDM_EDW.ETL_POST_STEP":
                ret_map.etl_prep_steps.append(stored_value)
        line_buffer = []

    return ret_map
