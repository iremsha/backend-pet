import json
from pathlib import Path

import typer
import uvicorn
from fastapi.openapi.utils import get_openapi

from web.app import create_app

cli = typer.Typer()


@cli.command()
def run(*, port: int = typer.Option(8080), debug: bool = typer.Option(default=False, envvar="DEBUG")) -> None:
    reload = debug
    reload_dirs = []
    log_level = "info"
    if debug:
        package_path = Path(__file__).parent / Path("web")
        reload_dirs.append(package_path)
        log_level = "debug"

    uvicorn.run(
        "web.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=port,
        reload=reload,
        reload_dirs=reload_dirs,
        log_level=log_level,
    )


@cli.command()
def spec() -> None:
    app = create_app()
    with Path.open("api/openapi.json", "w") as f:
        json.dump(app.openapi(), f)
