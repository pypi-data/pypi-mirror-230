# -*- coding: utf-8 -*-
import argparse
import errno
import warnings
from pathlib import Path

from arkindex_cli.commands.benchmark import add_benchmark_parser
from arkindex_cli.commands.classes import add_classes_parser
from arkindex_cli.commands.elements import add_elements_parser
from arkindex_cli.commands.export import add_export_parser
from arkindex_cli.commands.login import add_login_parser
from arkindex_cli.commands.models import add_models_parser
from arkindex_cli.commands.process import add_process_parser
from arkindex_cli.commands.secrets import add_secrets_parser
from arkindex_cli.commands.selection import add_selection_parser
from arkindex_cli.commands.upload import add_upload_parser
from arkindex_cli.commands.worker import add_worker_parser


def get_version():
    version_file = Path(__file__).absolute().parent.parent / "VERSION"
    if version_file.is_file():
        with version_file.open() as f:
            return f.read().strip()
    else:
        import pkg_resources

        try:
            return pkg_resources.get_distribution("arkindex-cli").version
        except pkg_resources.ResolutionError:
            pass


def get_parser():
    parser = argparse.ArgumentParser(description="Arkindex command-line tool")
    parser.add_argument(
        "-p",
        "--profile",
        dest="profile_slug",
        metavar="SLUG",
        help="Slug of an Arkindex profile to use instead of the default.",
    )

    version = get_version()
    if version:
        parser.add_argument(
            "-V",
            "--version",
            action="version",
            version=f"%(prog)s {version}",
        )

    subcommands = parser.add_subparsers(metavar="subcommand")

    add_benchmark_parser(subcommands)
    add_classes_parser(subcommands)
    add_elements_parser(subcommands)
    add_export_parser(subcommands)
    add_login_parser(subcommands)
    add_process_parser(subcommands)
    add_secrets_parser(subcommands)
    add_upload_parser(subcommands)
    add_models_parser(subcommands)
    add_worker_parser(subcommands)
    add_selection_parser(subcommands)

    return parser


def main():
    # Ignore the deprecation warnings of the SQLite export functions, which are only intended for other scripts.
    warnings.filterwarnings(
        action="ignore", category=FutureWarning, module="arkindex_cli.commands.export"
    )

    parser = get_parser()
    args = vars(parser.parse_args())
    if "func" in args:
        # Run the subcommand's function
        try:
            status = args.pop("func")(**args)
            parser.exit(status=status)
        except KeyboardInterrupt:
            # Just quit silently on ^C instead of displaying a long traceback
            parser.exit(status=errno.EOWNERDEAD)
    else:
        parser.error("A subcommand is required.")
