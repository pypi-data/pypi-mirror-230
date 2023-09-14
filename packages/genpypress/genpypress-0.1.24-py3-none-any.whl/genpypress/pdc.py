import logging as _logging
import os as _os
import pathlib as _p
from collections import namedtuple as _namedtuple
from contextlib import contextmanager as _contextmanager

import fire as _fire
import oracledb as _ora

_logger = _logging.getLogger()


def _get_parent_directories(path: _p.Path) -> list[_p.Path]:
    """Returns a list of all parent directories for a pathlib.Path object.

    Args:
        path: The pathlib.Path object.

    Returns:
        A list of all parent directories.
    """
    directories = []
    current_path = path
    while current_path != current_path.parent:
        _logger.info(f"appending: {current_path}")
        directories.append(current_path)
        current_path = current_path.parent

    return directories


def _locate_client() -> _p.Path | None:
    dirs_to_try: list[_p.Path] = []
    files_to_try = ["oci.dll", "sqlplus.exe", "oci.msg", "libocci.so.12.2"]
    try:
        dirs_to_try.extend(_get_parent_directories(_p.Path(_os.environ["TNS_ADMIN"])))
    except KeyError:
        pass

    try:
        for pth in _os.environ["PATH"].split(";"):
            dirs_to_try.append(_p.Path(pth))
    except KeyError:
        pass

    for pth in dirs_to_try:
        _logger.info(str(pth))
        for file in files_to_try:
            if (pth / file).is_file():
                return pth

    _logger.warning("failed to switch to thick client")
    _logger.warning(
        "see https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html#enablingthick for mode details"
    )
    return None


def _switch_to_thick_client():
    client_dir = _locate_client()
    if client_dir:
        _ora.init_oracle_client(lib_dir=str(client_dir))


def _one_of(keys: list[str], default=None) -> str | None:
    if isinstance(keys, str):
        keys = [keys]
    for k in keys:
        try:
            val = _os.environ[k]
            return val
        except KeyError:
            continue
    return default


_DFLT_DIR = _os.getcwd()
_DFLT_USER = _one_of("TO2_PDC_USER")
_DFLT_PASS = _one_of("TO2_PDC_PASSWORD")
_DFLT_SRVR = _one_of("TO2_PDC_DSN")

_OraSession = _namedtuple("_OraSession", "session,cursor")


@_contextmanager
def _connection(dsn: str, user: str, password: str, commit: bool = False) -> _OraSession:
    with _ora.connect(user=user, password=password, dsn=dsn) as sess:
        with sess.cursor() as cur:
            if commit:
                sess.begin()
            yield _OraSession(cursor=cur, session=sess)
            if commit:
                sess.commit()


def restart(
    job_or_engine: str = "",
    dsn: str | None = _DFLT_SRVR,
    user: str | None = _DFLT_USER,
    password: str | None = _DFLT_PASS,
):
    engineId: int | None = None
    where: str = ""

    try:
        engineId = int(job_or_engine)
        where = f"engine_id = ${engineId}"
    except ValueError:
        if job_or_engine == "":
            where = "1=1"
        else:
            where = f"job_name like '%{job_or_engine}%'"

    upd = f"""
        update sess_job
        set max_runs = max_runs + 1, status = 0
        where {where}
        and status in (3,9)
        and job_name not like '%DIRECTOR%'
        and job_name not like '%SNIFFER%'
        """

    with _connection(dsn, user, password, commit=True) as c:
        c.cursor.execute(upd)


def stop(
    engine: int = 29,
    dsn: str | None = _DFLT_SRVR,
    user: str | None = _DFLT_USER,
    password: str | None = _DFLT_PASS,
):
    assert dsn
    assert user
    assert password
    _set_concurrent_jobs(engine, 0, dsn, user, password)


_Statement = _namedtuple("_Statement", "source,sql")


def deploy(
    what: str = _DFLT_DIR,
    max_files: int = 20,
    glob_mask: str = "*.sql",
    encoding: str = "utf-8",
    dsn: str | None = _DFLT_SRVR,
    user: str | None = _DFLT_USER,
    password: str | None = _DFLT_PASS,
    log_sql: bool = False,
):
    pth = _p.Path(what)
    files = []
    if pth.is_file():
        files.append(pth)
    elif pth.is_dir():
        files = list(pth.rglob(glob_mask))

    if len(files) == 0:
        raise ValueError("empty ist of files")
    if len(files) > max_files:
        raise ValueError(f"too much to deploy: {max_files=}, {len(files)=}")

    statements = []
    for f in files:
        content = f.read_text(encoding=encoding, errors="strict")
        _s = [stmt.strip() for stmt in content.split(";") if stmt.strip() != "commit"]
        _s = [_Statement(source=f, sql=sql) for sql in _s if sql.replace("\n", "") != ""]
        statements.extend(_s)

    print(f"deploy to: {dsn=}, {user=}")
    with _connection(user=user, password=password, dsn=dsn, commit=True) as c:
        cur = c.cursor
        for s in statements:
            try:
                if log_sql:
                    print(s.sql)
                cur.execute(s.sql)
            except Exception as e:
                print(e)
                print(f"at: {s.source}")
                print(f"sql: {s.sql}")
                raise
        cur.execute(
            """
            update ctrl_job
            set max_runs = 1
            where max_runs > 1 
            and (job_name like 'EP%' or job_name like 'AP%')
            and not (
                job_name like '%SNIFFER%'
            )
        """
        )
    print("all ok")


def start(
    engine: int = 29,
    jobs: int = 10,
    dsn: str | None = _DFLT_SRVR,
    user: str | None = _DFLT_USER,
    password: str | None = _DFLT_PASS,
):
    assert dsn
    assert user
    assert password
    _set_concurrent_jobs(engine, jobs, dsn, user, password)


def _set_concurrent_jobs(
    engine: int = 29,
    jobs: int = 10,
    dsn: str | None = _DFLT_SRVR,
    user: str | None = _DFLT_USER,
    password: str | None = _DFLT_PASS,
):
    sql = """
    update ctrl_parameters
    set param_val_int = :jobs
    where param_name in (
    'MAX_CONCURRENT_JOBS' /* v aktuálním runu (temporary nastavení) */,
    'MAX_CONCURRENT_JOBS_DFLT' /* default, kolik se nahodí v dalším runu na max_concurrent_jobs */
    )
    and param_cd = :engine
    """
    print(f"setting: {engine=}, {jobs=}")
    with _connection(user=user, password=password, dsn=dsn, commit=True) as c:
        c.cursor.execute(sql, engine=engine, jobs=jobs)


def delay(
    delay: int = 5,
    dsn: str | None = _DFLT_SRVR,
    user: str | None = _DFLT_USER,
    password: str | None = _DFLT_PASS,
):
    assert dsn
    assert user
    assert password
    sql = """
        update ctrl_job_status 
        set delay_minutes = :delay where status in (3,9)
    """
    print(f"setting delay to {delay}")
    print(f"{dsn=}, {user=}")
    with _connection(dsn, user, password, commit=True) as c:
        c.cursor.execute(sql, delay=delay)


# c:\apps\oracle\instantclient_19_10\admin\
def _main():
    _logging.basicConfig(level=_logging.INFO)
    _switch_to_thick_client()
    _fire.Fire()


if __name__ == "__main__":
    _main()
