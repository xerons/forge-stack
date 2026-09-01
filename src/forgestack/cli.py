"""ForgeStack CLI root."""

import typer

from .commands import agents_cmd, board_cmd, doctor_cmd, inbox_cmd, init_cmd, manager_cmd, \
    open_cmd, setup_cmd, status_cmd, update_cmd, version

app = typer.Typer(name="forgestack", help="Existing tools, one development workflow.")


@app.command()
def version_cmd() -> None:
    version.cli()


@app.command()
def setup(dry_run: bool = typer.Option(False, "--dry-run")) -> None:
    setup_cmd.cli(dry_run=dry_run)


@app.command()
def init() -> None:
    init_cmd.cli()


@app.command()
def agents() -> None:
    agents_cmd.cli()


@app.command()
def manager() -> None:
    manager_cmd.cli()


@app.command()
def open_cmd_fn() -> None:
    open_cmd.cli()


@app.command()
def board() -> None:
    board_cmd.cli()


@app.command()
def status() -> None:
    status_cmd.cli()


@app.command()
def inbox() -> None:
    inbox_cmd.cli()


@app.command()
def doctor() -> None:
    raise SystemExit(doctor_cmd.cli())


@app.command()
def update() -> None:
    update_cmd.cli()
