# -*- coding: utf-8 -*-
from arkindex_cli.commands.process.recover import add_recover_parser
from arkindex_cli.commands.process.report import add_report_parser


def add_process_parser(subcommands) -> None:
    process_parser = subcommands.add_parser(
        "process",
        aliases=["processes", "import", "imports"],
        description="Manage processes",
        help="Manage processes",
    )
    subparsers = process_parser.add_subparsers()
    add_report_parser(subparsers)
    add_recover_parser(subparsers)

    def subcommand_required(*args, **kwargs):
        process_parser.error("A subcommand is required.")

    process_parser.set_defaults(func=subcommand_required)
