from __future__ import annotations

import argparse
import contextlib
import logging
from collections.abc import Generator
from collections.abc import Sequence

from httpx import HTTPStatusError

from vortex import constants as C
from vortex import util
from vortex.commands.clean import clean
from vortex.commands.clone import clone
from vortex.commands.code import code
from vortex.commands.config import config
from vortex.commands.copy import copy
from vortex.commands.delete import delete
from vortex.commands.find import find
from vortex.commands.grep import grep
from vortex.commands.list import list_
from vortex.commands.log import log
from vortex.commands.new import new
from vortex.commands.watch import watch
from vortex.models import DesignType
from vortex.workspace import Workspace
from vortex.workspace import WorkspaceError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("watchfiles").setLevel(logging.ERROR)

logger = logging.getLogger("vortex")


@contextlib.contextmanager
def error_handler() -> Generator[None, None, None]:
    try:
        yield
    except (WorkspaceError, HTTPStatusError) as e:
        logger.error(e)
        raise SystemExit(1)
    except KeyboardInterrupt:
        raise SystemExit(130)
    except BaseException as e:
        logger.critical(e, stack_info=True, exc_info=True)
        raise SystemExit(1)


def _add_server_option(*parsers: argparse.ArgumentParser) -> None:
    for p in parsers:
        p.add_argument(
            "--server",
            "-s",
            metavar="NAME",
            help="Enter the name of the server definition in the config file to use",
        )


def _add_design_type_option(
    *parsers: argparse.ArgumentParser | argparse._MutuallyExclusiveGroup,
) -> None:
    for p in parsers:
        p.add_argument(
            "--type",
            "-t",
            nargs="*",
            dest="design_type",
            type=DesignType.from_name,
            metavar="DESIGN_TYPE",
            help=(f"Choices: {[t.name.lower() for t in DesignType]}"),
        )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Vortex command line tool")
    parser.add_argument(
        "--version", "-V", action="version", version=f"vortex-cli {C.VERSION}"
    )
    parser.add_argument(
        "--workspace",
        "-w",
        metavar="DIR",
        help="Override the Workspace directory path",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        help="Set this flag to see DEBUG messages",
        action="store_true",
    )

    command_parser = parser.add_subparsers(dest="command")

    list_parser = command_parser.add_parser(
        "list",
        aliases=("ls",),
        help=(
            "List Puakma Applications on the server or cloned locally."
            "(ls is an alias for 'vortex list --local')"
        ),
    )
    list_parser.add_argument(
        "--group",
        "-g",
        nargs="*",
        help="Enter application 'group' substrings to filter the results",
    )
    list_parser.add_argument(
        "--name",
        "-n",
        nargs="*",
        help="Enter application 'name' substrings to filter the results",
    )
    list_parser.add_argument(
        "--template",
        "-t",
        nargs="*",
        help="Enter application 'template' substrings to filter the results",
    )
    list_parser.add_argument(
        "--local",
        action="store_true",
        dest="show_local_only",
        help="Set this flag to list locally cloned applications instead",
    )
    list_parser.add_argument(
        "--show-inherited",
        help="Set this flag to also display inherited applications",
        action="store_true",
    )
    list_parser.add_argument(
        "--show-inactive",
        help="Set this flag to also display inactive applications",
        action="store_true",
    )
    list_parser.add_argument(
        "--ids-only",
        "-x",
        help=(
            "Set this flag to only display the ID's of the applications in the output"
        ),
        dest="show_ids_only",
        action="store_true",
    )
    list_parser.add_argument(
        "--open-urls",
        "-o",
        help="Set this flag to open each application URL in a web browser",
        action="store_true",
    )
    list_parser.add_argument(
        "--open-dev-urls",
        "-d",
        help="Set this flag to open each application webdesign URL in a web browser",
        action="store_true",
    )

    clone_parser = command_parser.add_parser(
        "clone",
        help="Clone Puakma Applications and their design objects into the workspace",
    )
    clone_parser.add_argument(
        "app_ids",
        nargs="*",
        metavar="APP_ID",
        help="The ID(s) of the Puakma Application(s) to clone",
        type=int,
    )
    clone_parser.add_argument(
        "--get-resources",
        "-r",
        help="Set this flag to also clone the application's resources",
        action="store_true",
    )
    clone_parser.add_argument(
        "--open-urls",
        "-o",
        help="Set this flag to open the application and webdesign URLs after cloning",
        action="store_true",
    )
    clone_parser.add_argument(
        "--reclone",
        help="Set this flag to reclone the already locally cloned applictions",
        action="store_true",
    )
    code_parser = command_parser.add_parser(
        "code",
        help="Open the workspace in Visual Studio Code",
        add_help=False,
    )
    code_parser.add_argument("--help", "-h", action="store_true")

    watch_parser = command_parser.add_parser(
        "watch",
        help=(
            "Watch the workspace for changes to Design Objects "
            "and upload them to the server"
        ),
    )

    command_parser.add_parser(
        "clean",
        help="Delete the cloned Puakma Application directories in the workspace",
    )

    config_parser = command_parser.add_parser(
        "config", help="View and manage configuration"
    )
    # TODO These could probably be a mutexgroup
    config_parser.add_argument(
        "--sample",
        dest="print_sample",
        action="store_true",
        help="Print a sample 'vortex-server-config.ini' file to the console",
    )
    config_parser.add_argument(
        "--update-vscode-settings",
        action="store_true",
        help="Updates the vortex.code-workspace file. Creating it if doesn't exist",
    )
    config_parser.add_argument(
        "--reset-vscode-settings",
        action="store_true",
        help="Recreates the vortex.code-workspace file",
    )
    config_parser.add_argument(
        "--output-config-path",
        action="store_true",
        help="Outputs the file path to the config file",
    )
    config_parser.add_argument(
        "--output-workspace-path",
        action="store_true",
        help="Outputs the file path to the workspace",
    )
    config_parser.add_argument(
        "--init",
        action="store_true",
        help=(
            "Creates the workspace directory and a sample "
            f"'{Workspace.CONFIG_FILE_NAME}' file, if they don't already exist"
        ),
    )

    log_parser = command_parser.add_parser(
        "log",
        help="View the last items in the server log",
    )
    log_parser.add_argument(
        "-n",
        type=int,
        help="The number of logs to return (1 - 50). Default is %(default)s.",
        default=10,
        dest="limit",
    )

    find_parser = command_parser.add_parser(
        "find",
        help="Find Design Objects of cloned applications by name",
        usage="%(prog)s [options] name",
    )
    find_parser.add_argument("name", help="The name of Design Objects to find")
    find_parser.add_argument("--app-id", type=int, nargs="*", dest="app_ids")
    find_parser.add_argument("--fuzzy", "-z", action="store_true")
    find_parser.add_argument(
        "--ids-only",
        "-x",
        help="Set this flag to only display the ID's of the objects in the output",
        dest="show_ids_only",
        action="store_true",
    )
    find_parser.add_argument(
        "--show-params",
        help="Set this flag to also display the Design Object parameters",
        action="store_true",
    )
    find_design_type_mutex = find_parser.add_mutually_exclusive_group()
    find_design_type_mutex.add_argument("--exclude-resources", action="store_true")

    grep_parser = command_parser.add_parser(
        "grep",
        help=(
            "Search the contents of cloned Design Objects using a Regular Expression."
        ),
        usage="%(prog)s [options] pattern",
    )
    grep_parser.add_argument("pattern", help="The Regular Expression pattern to match")
    grep_parser.add_argument("--app-id", type=int, nargs="*", dest="app_ids")
    grep_parser.add_argument("--output-paths", action="store_true")
    grep_design_type_mutex = grep_parser.add_mutually_exclusive_group()
    grep_design_type_mutex.add_argument("--exclude-resources", action="store_true")

    new_parser = command_parser.add_parser("new", help="Create new Design Object(s)")
    new_parser.add_argument("names", nargs="+")
    new_parser.add_argument("--app-id", type=int, required=True)
    new_parser.add_argument("--comment", "-c")
    new_parser.add_argument("--inherit-from")
    new_parser.add_argument("--open-action")
    new_parser.add_argument("--save-action")
    new_parser.add_argument("--parent-page")
    new_parser.add_argument(
        "--type",
        "-t",
        dest="design_type",
        type=DesignType.from_name,
        metavar=f"[{', '.join([t.name.lower() for t in DesignType])}]",
        required=True,
    )
    new_parser.add_argument(
        "--content-type", help="The MIME Type. Only used when creating a 'resource'."
    )

    copy_parser = command_parser.add_parser(
        "copy", help="Copy a Design Object from one application to another"
    )
    copy_parser.add_argument("ids", nargs="+", metavar="DESIGN_ID", type=int)
    copy_parser.add_argument(
        "--app-id", nargs="+", type=int, required=True, metavar="APP_ID"
    )
    copy_parser.add_argument("--copy-params", action="store_true")

    delete_parser = command_parser.add_parser(
        "delete", help="Delete Design Object(s) by ID"
    )
    delete_parser.add_argument("obj_ids", nargs="+", type=int, metavar="DESIGN_ID")

    SERVER_COMMANDS = (
        "list",
        "ls",
        "clone",
        "watch",
        "log",
        "new",
        "delete",
        "copy",
        "find",
        "grep",
    )
    _server_parsers = (
        list_parser,
        clone_parser,
        watch_parser,
        log_parser,
        new_parser,
        delete_parser,
        copy_parser,
        find_parser,
        grep_parser,
    )
    _add_server_option(*_server_parsers, config_parser)
    _add_design_type_option(find_design_type_mutex, grep_design_type_mutex)

    # Validate Arguments
    args, remaining_args = parser.parse_known_args(argv)
    if args.command != "code":
        parser.parse_args(argv)  # Call this for validation
    if args.command == "new" and (
        args.design_type == DesignType.RESOURCE and not args.content_type
    ):
        new_parser.error("--type argument value 'resource' requires --content-type")
    if args.command == "clone" and not (args.app_ids or args.reclone):
        clone_parser.error("Please specifiy the APP_ID[s] to clone or use --reclone")

    # Configure loggers
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.DEBUG)
        logging.getLogger("watchfiles").setLevel(logging.INFO)

    with error_handler():
        workspace_path = getattr(args, "workspace", None)
        server_name = getattr(args, "server", None)
        init = args.command == "config" and args.init
        workspace = Workspace(workspace_path, init)

        if args.command in SERVER_COMMANDS:
            server = workspace.read_server_from_config(server_name)

            if args.command in ("list", "ls"):
                local_only = args.show_local_only or args.command == "ls"
                return list_(
                    workspace,
                    server,
                    group_filter=args.group,
                    name_filter=args.name,
                    template_filter=args.template,
                    show_ids_only=args.show_ids_only,
                    show_inherited=args.show_inherited,
                    show_inactive=args.show_inactive,
                    show_local_only=local_only,
                    open_urls=args.open_urls,
                    open_dev_urls=args.open_dev_urls,
                )
            elif args.command == "clone":
                return clone(
                    workspace,
                    server,
                    args.app_ids,
                    get_resources=args.get_resources,
                    open_urls=args.open_urls,
                    reclone=args.reclone,
                )
            elif args.command == "watch":
                return watch(workspace, server)
            elif args.command == "log":
                return log(server, args.limit)
            elif args.command == "find":
                return find(
                    workspace,
                    server,
                    args.name,
                    app_ids=args.app_ids,
                    design_types=args.design_type,
                    exclude_resources=args.exclude_resources,
                    show_params=args.show_params,
                    show_ids_only=args.show_ids_only,
                    fuzzy_search=args.fuzzy,
                )
            elif args.command == "grep":
                return grep(
                    workspace,
                    server,
                    args.pattern,
                    app_ids=args.app_ids,
                    design_types=args.design_type,
                    output_paths=args.output_paths,
                    exclude_resources=args.exclude_resources,
                )
            elif args.command == "new":
                return new(
                    workspace,
                    server,
                    app_id=args.app_id,
                    names=args.names,
                    design_type=args.design_type,
                    content_type=args.content_type,
                    comment=args.comment,
                    inherit_from=args.inherit_from,
                    parent_page=args.parent_page,
                    open_action=args.open_action,
                    save_action=args.save_action,
                )
            elif args.command == "delete":
                return delete(workspace, server, args.obj_ids)
            elif args.command == "copy":
                return copy(
                    workspace,
                    server,
                    args.ids,
                    to_app_ids=args.app_id,
                    copy_params=args.copy_params,
                )
        elif args.command == "clean":
            return clean(workspace)
        elif args.command == "code":
            if args.help:
                code_parser.print_help()
                util.print_row_break()
                remaining_args.insert(0, "--help")
            return code(workspace, remaining_args)
        elif args.command == "config":
            return config(
                workspace,
                server_name,
                init=args.init,
                print_sample=args.print_sample,
                update_vscode_settings=args.update_vscode_settings,
                reset_vscode_settings=args.reset_vscode_settings,
                output_config_path=args.output_config_path,
                output_workspace_path=args.output_workspace_path,
            )
        elif args.command:
            raise NotImplementedError(f"Command '{args.command}' is not implemented.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
