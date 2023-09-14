import os
from pathlib import Path

import typer

from .auth import auth_app
from .dashboard import dashboard_app
from .example import example_app
from .formula import formula_app

app = typer.Typer()


@app.command(name="init", help="Initialize zit project")
def init():
    current_dir = Path.cwd()
    zit_dir = current_dir / ".zit"

    if not zit_dir.exists():
        os.makedirs(zit_dir)
        typer.echo(f"Initializing zit project in {zit_dir}")
    else:
        typer.echo(f"Project already initialized in {zit_dir}")


app.add_typer(auth_app)
app.add_typer(formula_app)
app.add_typer(dashboard_app)
app.add_typer(example_app)

if __name__ == "__main__":
    app()
