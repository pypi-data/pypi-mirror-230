from __future__ import annotations

from typing import Optional

import typer

from ..sdk.slingshot_sdk import SlingshotSDK
from ..shared.config import load_slingshot_project_config
from .config.slingshot_cli import SlingshotCLIApp

app = SlingshotCLIApp()


@app.command("push", requires_project=True, top_level=True)
async def push(
    description: Optional[str] = typer.Option(None, help="A short description of your code (for reference purposes)."),
    path: Optional[str] = typer.Option(
        None,
        help="The path to the directory you wish to sync. Defaults to the current directory. [NOT IMPLEMENTED YET]",
    ),
    *,
    sdk: SlingshotSDK,
) -> None:
    """Push a new version of your code to Slingshot by creating a new code artifact."""
    load_slingshot_project_config()  # Load the slingshot config so that we raise if it's missing

    await sdk.push_code(code_dir=path, description=description, and_print=True)
    await sdk.apply_project()
