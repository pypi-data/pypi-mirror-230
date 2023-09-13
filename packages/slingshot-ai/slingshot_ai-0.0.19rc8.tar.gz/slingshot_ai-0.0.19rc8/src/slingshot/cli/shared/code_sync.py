from __future__ import annotations

import asyncio
import contextlib
import platform
import shutil
import sys
from logging import getLogger
from pathlib import Path
from time import sleep
from typing import Any, Iterator

import sh  # type: ignore
import typer

from slingshot import schemas
from slingshot.cli.config.slingshot_cli import SlingshotCLIApp
from slingshot.cli.shared.formatting import describe_component_type
from slingshot.cli.shared.ssh import start_ssh_for_app
from slingshot.sdk.config import client_settings
from slingshot.sdk.errors import SlingshotException
from slingshot.sdk.graphql import fragments
from slingshot.sdk.slingshot_sdk import SlingshotSDK
from slingshot.sdk.utils import console

app = SlingshotCLIApp()
logger = getLogger(__name__)


async def start_code_sync(sync_path: Path, component_spec: fragments.ComponentSpec, *, sdk: SlingshotSDK) -> None:
    """
    Starts code sync with a remote app. The app should already be running, or this will fail with an error.
    :param sync_path: The local path to sync with the remote
    :param component_spec: Spec of the app to sync against (may be a session or other app such as a web app)
    :param sdk: Slingshot SDK
    """

    ssh_connection_details = await start_ssh_for_app(component_spec, use_case='code sync', sdk=sdk)
    ssh_connection_str = (
        f"{ssh_connection_details.username}@{ssh_connection_details.hostname}:{ssh_connection_details.port}"
    )
    formatted_component_type = describe_component_type(component_spec.component_type, component_spec.app_sub_type)
    target_sync_path = (
        "/slingshot/session" if component_spec.app_sub_type == schemas.AppSubType.SESSION else "/mnt/slingshot/code"
    )

    await _start_unison(formatted_component_type, ssh_connection_str, sync_path, target_sync_path, verbose=sdk.verbose)


async def _start_unison(
    component_type: str, ssh_connection_str: str, sync_path: Path | None, target_sync_path: str, verbose: bool = False
) -> None:
    if sync_path is None:
        sync_path = Path.cwd()
    if not _is_unison_installed():
        _print_unison_install_instructions()
        raise typer.Exit(1)

    # TODO: poll until sshd is available. For now, we can assume it takes <1s.
    sleep(1)
    remote_ssh = f"ssh://{ssh_connection_str}/{target_sync_path}"
    logger.debug(remote_ssh)

    p = "working directory" if sync_path.cwd().absolute() == sync_path.absolute() else sync_path
    for _ in range(3):  # retry 3 times
        console.print(f"[blue]Syncing {p} to your {component_type}...[/blue]")
        try:
            # run unison command in a subprocess
            # assumes ssh key is already added to the server authorized_keys
            with _open_log_file(verbose) as (stdout, stderr):
                # TODO: support explicit selection of the SSH key
                #  unison /local/path ssh://remote/path -sshcmd 'ssh -i /path/to/your_specific_key'
                sh.unison(
                    str(sync_path),
                    remote_ssh,
                    batch=True,  # batch mode: ask no questions at all
                    repeat="watch",  # synchronize repeatedly (using unison-fsmonitor process to detect changes)
                    prefer="newer",  # choose newer version for conflicting changes
                    copyonconflict=True,  # keep copies of conflicting files
                    sshargs="-o StrictHostKeyChecking=no",  # skip known_hosts check
                    _long_prefix="-",
                    _err=stderr,
                    _out=stdout,
                )
        except sh.ErrorReturnCode:
            # TODO consider parsing the unison.log to e.g. automatically identify if it's a `Permission denied
            #  (publickey)` error
            console.print("[yellow]An error occurred while syncing your code. Retrying...[/yellow]")
            console.print(
                "[yellow]Please make sure the SSH key used for code sync has been added to the SSH agent[/yellow]"
            )
            await asyncio.sleep(1)  # wait for a second before retrying
    unison_log_file = client_settings.global_config_folder / "unison.log"
    raise SlingshotException(f"Error running unison, please check {unison_log_file} for more details")


def _is_unison_installed() -> bool:
    _unison = shutil.which("unison") is not None
    if not _unison:
        console.print("[red]Unison is not installed[/red]")
    _fsmonitor = shutil.which("unison-fsmonitor") is not None
    if not _fsmonitor:
        console.print("[red]Unison-fsmonitor is not installed[/red]")
    return _unison and _fsmonitor


def _print_unison_install_instructions() -> None:
    uname = platform.uname()

    console.print("[yellow] We use unison and unison-fsmonitor for code sync, please install [/yellow]")
    if uname.system == "Darwin":
        console.print("[yellow] Using homebrew:[/yellow]")
        console.print("[yellow]  brew install unison[/yellow]")
        console.print("[yellow]  brew install eugenmayer/dockersync/unox[/yellow]")
    elif uname.system == "Linux":
        console.print("[yellow] Manually from official releases:[/yellow]")
        console.print(
            "[yellow]  wget -qO- "
            "https://github.com/bcpierce00/unison/releases/download/v2.53.0/"
            "unison-v2.53.0+ocaml-4.13.1+x86_64.linux.tar.gz"
            " | sudo tar -zxvf - -C /usr bin/[/yellow]"
        )
    console.print("[yellow] For more information see:[/yellow]")
    console.print("[yellow]  https://github.com/bcpierce00/unison/blob/master/INSTALL.md [/yellow]")


@contextlib.contextmanager
def _open_log_file(verbose: bool) -> Iterator[tuple[Any, Any]]:  # stdout, stderr
    log_file = client_settings.global_config_folder / "unison.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # If verbose, print to stdout/stderr, otherwise write to log file
    if verbose:
        yield sys.stdout, sys.stderr
    else:
        with open(log_file, "w") as f:
            yield f, f
