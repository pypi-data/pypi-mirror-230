"""
AGENCY CLI for running and interacting with the scripts.
"""
from enum import Enum
from typing import List

import typer
from rich import print
from typing_extensions import Annotated

from contact_magic.scripts.run_workflows import run_sheets
from contact_magic.scripts.sync_scraper_options_to_workersheets import (
    sync_scraper_options,
)
from contact_magic.scripts.update_workflow_approval_metrics import (
    update_rows_approved_and_remaining,
)

app = typer.Typer()


class ScriptOptions(Enum):
    run_sheets = "run_sheets"
    update_approved = "update_approved"
    sync_scraper_options = "sync_scraper_options"


@app.command()
def pipeline(
    task: List[ScriptOptions] = None,
    run_all: Annotated[bool, typer.Option("--run-all")] = False,
    times_to_run: Annotated[int, typer.Option(min=1)] = 1,
):
    """
    Run a list of scripts in a single command.

    Notice how you can set the order and number of times to run.

    Ex: "python agency.py --task run_sheets --task run_sheets --task update_approved"

    To run all of the scripts

    Ex: "python agency.py --run-all"
    """
    commands = {
        "run_sheets": run_sheets,
        "update_approved": update_rows_approved_and_remaining,
        "sync_scraper_options": sync_scraper_options,
    }
    tasks = task or []
    for _ in range(times_to_run):
        if run_all:
            for name, command in commands.items():
                print(f":robot_face: [green]Running[/green] {name}")
                command()
                print(f":robot_face: [green]Completed[/green] {name}")
            continue
        for task in tasks:
            print(f":robot_face: [green]Running[/green] {task.value}")
            commands[task.value]()
            print(f":robot_face: [green]Completed[/green] {task.value}")
