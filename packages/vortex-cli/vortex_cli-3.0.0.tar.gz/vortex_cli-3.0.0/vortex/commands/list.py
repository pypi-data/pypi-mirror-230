from __future__ import annotations

import logging

import tabulate

from vortex import util
from vortex.models import PuakmaApplication
from vortex.models import PuakmaServer
from vortex.workspace import Workspace

logger = logging.getLogger("vortex")


def list_(
    workspace: Workspace,
    server: PuakmaServer,
    *,
    group_filter: list[str],
    name_filter: list[str],
    template_filter: list[str],
    show_ids_only: bool = False,
    show_inherited: bool = False,
    show_inactive: bool = False,
    show_local_only: bool = False,
    open_urls: bool = False,
    open_dev_urls: bool = False,
) -> int:
    if show_local_only:
        apps = workspace.listapps()
    else:
        with server as s:
            apps = s.fetch_all_apps(
                name_filter,
                group_filter,
                template_filter,
                show_inherited,
                show_inactive,
            )
    if open_urls or open_dev_urls:
        util.open_app_urls(*apps, open_dev_url=open_dev_urls)
    else:
        if show_ids_only:
            for app in apps:
                print(app.id)
        else:
            _render_app_list(apps, show_inherited=show_inherited)
    return 0


def _render_app_list(
    apps: list[PuakmaApplication],
    *,
    show_inherited: bool,
) -> None:
    row_headers = [
        "ID",
        "Name",
        "Group",
        "Template Name",
    ]
    row_data = []

    if show_inherited:
        row_headers.append("Inherits From")

    for app in sorted(apps, key=lambda x: (x.group.casefold(), x.name.casefold())):
        row = [app.id, app.name, app.group, app.template_name]
        if show_inherited:
            row.append(app.inherit_from)
        row_data.append(row)
    print(tabulate.tabulate(row_data, headers=row_headers))
