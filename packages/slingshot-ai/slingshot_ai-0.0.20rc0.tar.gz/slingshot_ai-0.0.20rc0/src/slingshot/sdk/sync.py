from __future__ import annotations

import os
import typing
import zipfile
from contextlib import contextmanager
from io import BytesIO
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator, Optional

import sh  # type: ignore
import typer
from sh import CommandNotFound, ErrorReturnCode

from slingshot import schemas
from slingshot.sdk.errors import SlingshotException
from slingshot.sdk.utils import bytes_to_str, console, md5_hash
from slingshot.shared.utils import get_data_or_raise

if typing.TYPE_CHECKING:
    from slingshot.sdk import SlingshotSDK

logger = getLogger(__name__)
app = typer.Typer()

ROOT_SUFFIX_TO_IGNORE = ["__pycache__", ".egg-info", ".slingshot"]

MAX_FILESIZE = 100_000  # 100KiB in bytes

MAX_FILESIZE_LARGE = 1_000_000  # 1MiB in bytes

MAX_TOTAL_SIZE = 10_000_000  # 10MiB in bytes

MAX_NUM_FILES = 1000


def should_skip_root(root: str) -> bool:
    return any(root.endswith(suffix) for suffix in ROOT_SUFFIX_TO_IGNORE)


def _zip_artifact_recursive(quiet: bool) -> bytes:
    """
    Zip the files in the current working directory, recursively. Excludes files based on size and git metadata:
      - Ignored files are skipped unless they're committed, in which case they're limited at MAX_FILESIZE
      - Files that are neither ignored nor committed are included, limited at MAX_FILESIZE
      - Otherwise, files are limited at MAX_FILESIZE_LARGE
    """
    with BytesIO() as zip_io:
        with zipfile.ZipFile(zip_io, "w") as zf:
            try:
                _zip_with_git_ls(quiet, zf)
            except (CommandNotFound, ErrorReturnCode):
                _zip_legacy(quiet, zf)

        bytes_ = zip_io.getvalue()
        if len(bytes_) > MAX_TOTAL_SIZE:
            raise SlingshotException(f"Sync directory is too large ({len(bytes_)} bytes) ⚠️. ")
        return bytes_


def _zip_legacy(quiet: bool, zf: zipfile.ZipFile) -> None:
    if not quiet:
        console.print("[yellow]Using legacy code push strategy[/yellow]. (Make sure 'git' is on your PATH to resolve.)")

    for root, dirs, files in os.walk("."):
        if should_skip_root(root):
            continue
        if len(files) > MAX_NUM_FILES:
            console.print(f"Sync directory has too many files: '{root}' ⚠️. Skipping this directory.", style="yellow")
            continue
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            if size > MAX_FILESIZE:
                relative_path = os.path.relpath(file_path)
                if not quiet:
                    console.print(
                        f"Skipping '{relative_path}' because it is too large ({bytes_to_str(size)}) ⚠️", style="yellow"
                    )
                continue
            zf.write(file_path)


def _zip_with_git_ls(quiet: bool, zf: zipfile.ZipFile) -> None:
    tracked_files = set(Path(path) for path in sh.git("ls-files").splitlines())
    untracked_files = set(Path(path) for path in sh.git("ls-files", "-o", "--exclude-standard").splitlines())
    for root, dirs, files in os.walk("."):
        if should_skip_root(root):
            continue

        for file in files:
            file_path = Path(os.path.join(root, file))
            size = os.path.getsize(file_path)
            if file_path in tracked_files:
                if size > MAX_FILESIZE_LARGE:
                    relative_path = os.path.relpath(file_path)
                    if not quiet:
                        console.print(
                            f"Skipping '{relative_path}' because it is too large ({bytes_to_str(size)}) ⚠️",
                            style="yellow",
                        )
                    continue
                zf.write(file_path)
            elif file_path in untracked_files:
                if size > MAX_FILESIZE:
                    relative_path = os.path.relpath(file_path)
                    if not quiet:
                        console.print(
                            f"Skipping '{relative_path}' because it is too large ({bytes_to_str(size)}) ⚠️",
                            style="yellow",
                        )
                    continue
                zf.write(file_path)


async def sync_code(
    sdk: SlingshotSDK, path: Path, description: Optional[str], quiet: bool = False
) -> tuple[schemas.UploadedSourceCode, bool]:
    logger.debug(f"Zipping up {path}...")
    zip_bytes = zip_code_artifact(path)

    # Check if the code is already uploaded
    local_code_hash = md5_hash(zip_bytes)
    project_id = await sdk._get_current_project_id_or_raise()
    latest_source_code = await sdk.api.get_latest_source_codes_for_project(project_id)
    if latest_source_code is not None and latest_source_code.blob_artifact.bytes_hash == local_code_hash:
        console.print(f"Code hasn't changed. Skipping upload.")
        return (
            schemas.UploadedSourceCode(
                source_code_id=latest_source_code.source_code_id, source_code_name=latest_source_code.blob_artifact.name
            ),
            False,
        )

    num_bytes = len(zip_bytes)
    console.print(f"Pushing code to Slingshot ({bytes_to_str(num_bytes)})...")
    # Save zip_bytes to a temporary file
    with TemporaryDirectory() as tmpdir:
        artifact_path = Path(tmpdir) / "code.zip"
        with open(artifact_path, "wb") as f:
            f.write(zip_bytes)
        artifact = await sdk.upload_artifact(
            artifact_path=artifact_path, blob_artifact_name="code", as_zip=True, quiet=quiet
        )
    if not artifact:
        raise SlingshotException("Failed to upload code to Slingshot")
    resp = await sdk.api.upload_source_code(artifact.blob_artifact_id, description, project_id=project_id)
    uploaded_source_code_resp = get_data_or_raise(resp)
    return uploaded_source_code_resp, True


def zip_code_artifact(root: Path, *, quiet: bool = False) -> bytes:
    """Zip the files in the current working directory, recursively. If the working directory is within a
    git repository, zip only the files that are in the directory and in the repository."""
    with enter_route(root):
        logger.debug(f"Zipping up {root.absolute()}...")
        return _zip_artifact_recursive(quiet)


@contextmanager
def enter_route(path: Path) -> Generator[None, None, None]:
    """
    Open the experimental directory in a context manager and return to the original directory on exit.

    (We can change this in the future)
    """
    cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(cwd)


def _zip_artifact_git(git_ls: list[str]) -> bytes:
    """
    Zip the files in the current working directory, based on the git ls-files output. This automatically
    excludes files that are gitignored.
    """
    with BytesIO() as zip_io:
        with zipfile.ZipFile(zip_io, "w") as zf:
            for file in git_ls:
                zf.write(file)
        return zip_io.getvalue()
