from __future__ import annotations

from vortex.models import DesignType
from vortex.models import PuakmaServer
from vortex.util import render_objects
from vortex.workspace import Workspace


def find(
    workspace: Workspace,
    server: PuakmaServer,
    name: str,
    *,
    app_ids: list[int] | None = None,
    design_types: list[DesignType] | None = None,
    exclude_resources: bool = True,
    show_params: bool = False,
    show_ids_only: bool = False,
    fuzzy_search: bool = True,
) -> int:
    apps = (
        app
        for app in workspace.listapps(server)
        if (not app_ids or (app.id in app_ids))
    )

    if exclude_resources:
        design_types = [t for t in DesignType if t != DesignType.RESOURCE]

    matches = (
        obj
        for app in apps
        for obj in app.design_objects
        if (
            (fuzzy_search and name.lower() in obj.name.lower())
            or (name.lower() == obj.name.lower())
        )
        and (not design_types or obj.design_type in design_types)
    )
    if show_ids_only:
        for obj in matches:
            print(obj.id)
    else:
        render_objects(matches, show_params=show_params)

    return 0
