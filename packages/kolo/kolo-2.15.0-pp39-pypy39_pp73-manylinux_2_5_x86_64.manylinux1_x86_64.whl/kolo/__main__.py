from __future__ import annotations

import gzip
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
from runpy import run_module, run_path

import click
import httpx

from . import django_schema
from .config import load_config
from .db import (
    TraceNotFoundError,
    create_schema_table,
    db_cursor,
    delete_traces_before,
    delete_traces_by_id,
    list_traces_from_db,
    load_trace_from_db,
    save_invocation_in_sqlite,
    save_schema,
    setup_db,
    vacuum_db,
)
from .profiler import KoloProfiler
from .serialize import monkeypatch_queryset_repr
from .utils import pretty_byte_size


DATETIME_FORMATS = click.DateTime(
    (
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S.%f",
    )
)


DJANGO_SETTINGS_ERROR = """Django settings not found.
Use `--settings` or set the `DJANGO_SETTINGS_MODULE` environment variable."""

TRACE_NOT_FOUND_ERROR = "Could not find trace_id: `{trace_id}`"

TEST_GENERATION_ERROR = """\
Test generation dependencies are not installed.

Run `pip install 'kolo[test_generation]'` to install them.
"""


def get_profiler(one_trace_per_test) -> KoloProfiler:
    config = load_config()
    db_path = setup_db(wal_mode=config.get("wal_mode", True))
    return KoloProfiler(
        db_path, config=config, one_trace_per_test=one_trace_per_test, source="kolo run"
    )


def profile_module(profiler: KoloProfiler, module_name: str):
    monkeypatch_queryset_repr()
    with profiler:
        run_module(module_name, run_name="__main__", alter_sys=True)


def profile_path(profiler: KoloProfiler, path: str):
    monkeypatch_queryset_repr()
    with profiler:
        run_path(path, run_name="__main__")


@click.group()
def cli():
    """Base for all kolo command line commands"""

    # Ensure the current working directory is on the path.
    # Important when running the `kolo` script installed by setuptools.
    # Not really necessary when using `python -m kolo`, but doesn't hurt.
    # Note, we use 1, not 0: https://stackoverflow.com/q/10095037
    # This probably doesn't matter for our use case, but it doesn't hurt.
    sys.path.insert(1, ".")


def python_noop_profiler(frame, event, arg):  # pragma: no cover
    pass


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("path")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.option("--one-trace-per-test", default=False, is_flag=True)
@click.option("--noop", default=False, is_flag=True)
def run(path, args, one_trace_per_test, noop):
    """
    Profile python code using kolo.

    PATH is the path to the python file or module being profiled.
    """
    if path == "python":
        path, *args = args
        if path == "-m":
            path, *args = args
            module = True
        else:
            module = False
    elif path.endswith(".py"):
        module = False
    else:
        module = True

    # Monkeypatch sys.argv, so the profiled code doesn't get confused
    # Without this, the profiled code would see extra args it doesn't
    # know how to handle.
    sys.argv = [path, *args]

    if noop:  # pragma: no cover
        config = load_config()
        if config.get("use_rust", True):
            from ._kolo import register_noop_profiler

            register_noop_profiler()
        else:
            sys.setprofile(python_noop_profiler)

        try:
            if module:
                run_module(path, run_name="__main__", alter_sys=True)
            else:
                run_path(path, run_name="__main__")
        finally:
            sys.setprofile(None)
        return

    profiler = get_profiler(one_trace_per_test)
    try:
        if module:
            profile_module(profiler, path)
        else:
            profile_path(profiler, path)
    finally:
        if not one_trace_per_test:  # pragma: no branch
            profiler.save_request_in_db()


@cli.group()
def trace():
    """
    List, dump, delete and load traces.
    """


@cli.command()
@click.argument("path")
@click.option(
    "--created-at",
    help="Mark this trace as created at this time.",
    type=DATETIME_FORMATS,
)
def load_trace(path, created_at=None):
    """
    DEPRECATED - Use: kolo trace load.
    """
    load_trace_base(path, created_at)  # pragma: no cover


def load_trace_base(path, created_at):
    config = load_config()
    wal_mode = config.get("wal_mode", True)
    db_path = setup_db(wal_mode=wal_mode)

    try:
        with open(path) as dump:
            raw_data = dump.read()
    except FileNotFoundError:
        raise click.ClickException(f'File "{path}" not found')

    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError:
        raise click.ClickException("Trace file is not valid json")
    try:
        trace_id = data["trace_id"]
    except KeyError:
        raise click.ClickException("Trace file is missing the `trace_id`")
    try:
        save_invocation_in_sqlite(
            db_path,
            trace_id,
            raw_data,
            wal_mode=wal_mode,
            ignore_errors=False,
            created_at=created_at,
        )
    except sqlite3.IntegrityError:
        raise click.ClickException(f"Trace ID `{trace_id}` already exists")

    click.echo(f"Loaded trace {trace_id}")


@trace.command()
@click.argument("path")
@click.option(
    "--created-at",
    help="Mark this trace as created at this time.",
    type=DATETIME_FORMATS,
)
def load(path, created_at):
    """
    Load a trace from a file into the Kolo database.
    """
    load_trace_base(path, created_at)


@cli.command()
@click.argument("trace_id")
@click.option("--file", help="The name of the file to save the trace to.")
def dump_trace(trace_id, file):
    """
    DEPRECATED - Use: kolo trace dump.
    """
    dump_trace_base(trace_id, file)  # pragma: no cover


def dump_trace_base(trace_id, file):
    config = load_config()
    wal_mode = config.get("wal_mode", True)
    db_path = setup_db(wal_mode=wal_mode)

    try:
        data = load_trace_from_db(db_path, trace_id, wal_mode=wal_mode)
    except TraceNotFoundError:
        raise click.ClickException(TRACE_NOT_FOUND_ERROR.format(trace_id=trace_id))

    if file:
        with open(file, "w") as f:
            f.write(data)
    else:
        click.echo(data)


@trace.command()
@click.argument("trace_id")
@click.option("--file", help="The name of the file to save the trace to.")
def dump(trace_id, file):
    """
    Dump a trace from the Kolo database to stdout or a specified file.
    """
    dump_trace_base(trace_id, file)


@cli.command()
def list_traces():
    """
    DEPRECATED - Use: kolo trace list.
    """
    list_traces_base()  # pragma: no cover


def list_traces_base(count=500, reverse=False):
    config = load_config()
    wal_mode = config.get("wal_mode", True)
    db_path = setup_db(wal_mode=wal_mode)

    traces = list_traces_from_db(
        db_path, wal_mode=wal_mode, count=count, reverse=reverse
    )

    if not traces:
        click.echo("No traces found")
        return

    for trace, timestamp, size in traces:
        size = pretty_byte_size(size)
        click.echo(f"{trace} at {timestamp} ({size})")


@trace.command()
@click.option("--count", help="The number of rows to show.", default=500)
@click.option(
    "--reverse",
    help="Reverse the order of the rows: newest at the bottom.",
    default=False,
    is_flag=True,
)
def list(count, reverse):
    """
    List of recent traces stored by kolo.
    """
    list_traces_base(count, reverse)


@cli.command()
@click.option(
    "--before",
    help="Delete traces older than this datetime.",
    type=DATETIME_FORMATS,
)
@click.option(
    "--vacuum",
    help="Recover disk space from the Kolo database.",
    default=False,
    is_flag=True,
)
def delete_old_traces(before, vacuum):
    """
    DEPRECATED - Use: kolo trace delete --old
    """
    delete_traces_base(
        trace_ids=(), old=True, before=before, vacuum=vacuum
    )  # pragma: no cover


def delete_traces_base(trace_ids, old, before, vacuum):
    config = load_config()
    wal_mode = config.get("wal_mode", True)
    db_path = setup_db(wal_mode=wal_mode)

    if trace_ids:
        delete_traces_by_id(db_path, trace_ids, wal_mode)
    elif old:
        if before is None:
            before = datetime.now() - timedelta(days=30)

        deleted_count = delete_traces_before(db_path, before, wal_mode)
        click.echo(f"Deleted {deleted_count} old traces created before {before}.")

    if vacuum:
        vacuum_db(db_path)


@trace.command()
@click.argument("trace_ids", required=False, nargs=-1)
@click.option("--old", is_flag=True, default=False, help="Delete old traces.")
@click.option(
    "--before",
    help="Delete traces older than this datetime. Must be used with `--old`.",
    type=DATETIME_FORMATS,
)
@click.option(
    "--vacuum",
    help="Recover disk space from the Kolo database.",
    default=False,
    is_flag=True,
)
def delete(trace_ids, old, before, vacuum):
    """
    Delete one or more traces stored by Kolo.
    """

    if before is not None and old is False:
        raise click.ClickException("--before requires --old")

    if old is False and not trace_ids and vacuum is False:
        raise click.ClickException("Must specify either TRACE_IDS, --old, or --vacuum")

    if trace_ids and old:
        raise click.ClickException("Cannot specify TRACE_IDS and --old together")

    delete_traces_base(trace_ids, old, before, vacuum)


def manage_py_settings():
    import ast

    try:
        with open("manage.py") as f:
            data = f.read()
    except OSError:  # pragma: no cover
        return None
    source = ast.parse(data, "manage.py")
    for node in ast.walk(source):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "setdefault"
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == "DJANGO_SETTINGS_MODULE"
            and isinstance(node.args[1], ast.Constant)
        ):
            return node.args[1].value  # pragma: no cover
    return None


def load_django(settings):
    import django

    if settings:
        os.environ["DJANGO_SETTINGS_MODULE"] = settings
    elif os.environ.get("DJANGO_SETTINGS_MODULE"):
        pass
    else:
        settings = manage_py_settings()
        if settings:
            os.environ["DJANGO_SETTINGS_MODULE"] = settings  # pragma: no cover
        else:
            raise click.ClickException(DJANGO_SETTINGS_ERROR)

    django.setup()


@cli.command()
@click.argument("trace_id")
@click.option("--test-name", default="test_my_view")
@click.option("--test-class", default="MyTestCase")
@click.option("--file", type=click.File("w"))
@click.option("--settings", default="")
@click.option("--template", default="")
def generate_test(trace_id, test_name, test_class, file, settings, template):
    import logging

    logging.disable()

    try:
        try:
            from .generate_tests import generate_from_trace_id
        except ModuleNotFoundError:  # pragma: no cover
            raise click.ClickException(TEST_GENERATION_ERROR)

        load_django(settings)

        try:
            test_code = generate_from_trace_id(
                trace_id, test_class, test_name, template
            )
        except TraceNotFoundError as e:
            raise click.ClickException(TRACE_NOT_FOUND_ERROR.format(trace_id=e.args[0]))

        if file:
            file.write(test_code)
        else:
            click.echo(test_code)
    finally:
        logging.disable(logging.NOTSET)


@cli.command()
@click.option("--settings", default="")
def store_django_model_schema(settings):
    from .git import COMMIT_SHA

    load_django(settings)

    schema = django_schema.get_schema()

    db_config = load_config()
    wal_mode = db_config.get("wal_mode", True)
    db_path = setup_db(wal_mode=wal_mode)
    with db_cursor(db_path, wal_mode) as cursor:
        create_schema_table(cursor)
        save_schema(cursor, schema, COMMIT_SHA)


@cli.command()
def dbshell():  # pragma: no cover
    """
    Open a sqlite3 shell to the Kolo database.
    """
    config = load_config()
    wal_mode = config.get("wal_mode", True)
    db_path = setup_db(wal_mode)
    subprocess.run(["sqlite3", db_path], check=True)


@trace.command()
@click.argument("trace_id")
def upload(trace_id):
    """
    Upload a trace to the kolo dashboard
    """
    config = load_config()
    wal_mode = config.get("wal_mode", True)
    db_path = setup_db(wal_mode)

    try:
        data = load_trace_from_db(db_path, trace_id, wal_mode=wal_mode)
    except TraceNotFoundError:
        raise click.ClickException(TRACE_NOT_FOUND_ERROR.format(trace_id=trace_id))

    base_url = os.environ.get("KOLO_BASE_URL", "https://my.kolo.app")
    url = f"{base_url}/api/traces/"
    payload = gzip.compress(data.encode("utf-8"))
    response = httpx.post(url, files={"data": payload})
    if response.status_code == 201:
        click.echo(f"{trace_id} uploaded successfully!")
    else:
        errors = response.json()
        raise click.ClickException(errors)


@trace.command()
@click.argument("trace_id")
def download(trace_id):
    """
    Download a trace from the kolo dashboard
    """
    config = load_config()
    wal_mode = config.get("wal_mode", True)
    db_path = setup_db(wal_mode)

    base_url = os.environ.get("KOLO_BASE_URL", "https://my.kolo.app")
    url = f"{base_url}/api/traces/{trace_id}/"
    response = httpx.get(url)

    if response.status_code == 404:
        raise click.ClickException(f"`{trace_id}` was not found by the server.")
    elif response.status_code != 200:
        raise click.ClickException(f"Unexpected status code: {response.status_code}.")

    try:
        data = gzip.decompress(response.content).decode("utf-8")
    except gzip.BadGzipFile:
        raise click.ClickException("Downloaded trace was not gzipped.")
    except UnicodeDecodeError:
        raise click.ClickException("Downloaded trace was not utf-8.")

    try:
        save_invocation_in_sqlite(
            db_path,
            trace_id,
            data,
            wal_mode=wal_mode,
            ignore_errors=False,
        )
    except sqlite3.IntegrityError:
        raise click.ClickException(f"`{trace_id}` already exists.")

    click.echo(f"`{trace_id}` downloaded successfully!")


if __name__ == "__main__":
    cli()  # pragma: no cover
