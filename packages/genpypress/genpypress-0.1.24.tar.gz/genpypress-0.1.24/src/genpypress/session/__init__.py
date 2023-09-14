import contextlib
import os
import sys

import teradatasql

# od verze 3.9 je k dispozici collections.abc.Generator, ve starších verzích typing.Generator
_version = (sys.version_info.major * 100) + sys.version_info.minor
if _version > 309:
    from collections.abc import Generator
else:
    from typing import Generator


def _one_of(keys: list[str], default=None) -> str | None:
    for k in keys:
        try:
            val = os.environ[k]
            return val
        except KeyError:
            continue
    return default


DEFAULT_HOSTNAME = _one_of(["TERADATA_HOSTNAME"], default="edwprod.cz.o2")
DEFAULT_USER = _one_of(["TERADATA_USER", "TO2_DOMAIN_USER"], default=None)
DEFAULT_PASSWORD = _one_of(["TERADATA_PASSWORD", "TO2_DOMAIN_PASSWORD"], default=None)


class ParameterError(ValueError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


@contextlib.contextmanager
def connect_teradata(
    hostname: str = DEFAULT_HOSTNAME,
    username: str = DEFAULT_USER,
    password: str = DEFAULT_PASSWORD,
    logmech: str | None = "LDAP",
    tmode: str = "TERA",
) -> Generator[teradatasql.TeradataConnection, None, None]:
    """Simple context manager, which can connect to Teradata using "sensible defaults".

    Args:
        hostname (str): hostname, defaults to DEFAULT_HOSTNAME ("edwprod.cz.o2")
        username (str): defaults to os.environ['TO2_DOMAIN_USER']
        password (str): defaults to os.environ['TO2_DOMAIN_PASSWORD']
        logmech (str, optional): defaults to "LDAP".
        tmode (str): ANSI or TERA; defaults to TERA

    Returns:
        teradatasql.TeradataConnection

    Throws:
        any error supported by the teradatasql module
    """
    if username is None:
        raise ParameterError(
            "username: should not be None. You can set it as ENV variable: TERADATA_USER, TO2_DOMAIN_USER"
        )
    if password is None:
        raise ParameterError("password: should not be None")
    with teradatasql.connect(host=hostname, user=username, password=password, logmech=logmech) as session:
        yield session
