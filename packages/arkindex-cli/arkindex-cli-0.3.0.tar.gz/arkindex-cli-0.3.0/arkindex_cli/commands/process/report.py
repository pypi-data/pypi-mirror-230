# -*- coding: utf-8 -*-
import json
from typing import Optional
from uuid import UUID

from rich import print as rich_print
from rich.panel import Panel
from rich.progress import Progress
from rich.syntax import Syntax
from rich.table import Table

from arkindex_cli.auth import Profiles
from arkindex_cli.commands.process.base import get_global_report


def add_report_parser(subcommands) -> None:
    report_parser = subcommands.add_parser(
        "report",
        description="Build a global ML report for a process",
        help="Build a global ML report for a process",
    )
    report_parser.add_argument(
        "process_id", type=UUID, help="ID of the process to retrieve the status from"
    )
    report_parser.add_argument(
        "-r",
        "--run",
        dest="run_number",
        type=int,
        help="Workflow run number to retrieve a report for. Defaults to the latest run.",
    )
    report_parser.add_argument(
        "-j",
        "--json",
        dest="json_output",
        action="store_true",
        default=False,
        help="Output a JSON file listing failed elements instead of a human-readable summary.",
    )
    report_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Display every error message and traceback along with the stats."
        "Does not have any effect when using --json",
    )
    report_parser.set_defaults(func=run)


def run(
    process_id: UUID,
    run_number: Optional[int] = None,
    verbose: bool = False,
    json_output: bool = False,
    profile_slug: Optional[str] = None,
) -> int:
    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Loading API client")
        client = Profiles().get_api_client_or_exit(profile_slug)

    try:
        ml_report = get_global_report(client, process_id, run_number)
    except ValueError as e:
        rich_print(f"[bright_red]{e}")
        return 2

    if verbose:
        for element_id, data in ml_report.failed_elements.items():
            rich_print(f"Element {element_id}: {len(data['errors'])} error(s)")

            for error in data["errors"]:
                output = (
                    error.get("traceback", "")
                    + f"\n{error['class']}: {error['message']}"
                )
                rich_print(Panel(Syntax(output, "python3")))

    if json_output:
        print(json.dumps(ml_report.failed_elements))
        return

    total = len(ml_report["elements"])
    errored = len(ml_report.failed_elements)
    rich_print(
        f"[bold]{total}[/] elements: "
        f"[bold bright_green]{total - errored}[/] successful, "
        f"[bold bright_red]{errored}[/] with errors"
    )

    if not errored:
        return

    table = Table(title="Errors by class")
    table.add_column("Class")
    table.add_column("Count", justify="right")
    for class_name, count in ml_report.errors_by_class.items():
        table.add_row(class_name, str(count))
    rich_print(table)
