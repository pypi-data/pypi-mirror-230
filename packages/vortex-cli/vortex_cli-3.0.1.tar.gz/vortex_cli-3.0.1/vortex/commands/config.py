from __future__ import annotations

from vortex import util
from vortex.workspace import SAMPLE_CONFIG
from vortex.workspace import Workspace


def config(
    workspace: Workspace,
    server_name: str | None,
    *,
    init: bool = False,
    print_sample: bool = False,
    update_vscode_settings: bool = False,
    reset_vscode_settings: bool = False,
    output_config_path: bool = False,
    output_workspace_path: bool = False,
) -> int:
    if print_sample:
        print(SAMPLE_CONFIG, end="")
        return 0
    if update_vscode_settings or reset_vscode_settings:
        return workspace.update_vscode_settings(reset_vscode_settings)
    if output_config_path:
        print(workspace.config_file)
        return 0
    if output_workspace_path:
        print(workspace.path)
        return 0
    if not init:
        workspace.print_info()
        util.print_row_break(" Server Info ")
        workspace.print_server_config_info(server_name)
    return 0
