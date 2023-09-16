from __future__ import annotations

import functools
import re

from vortex.colour import Colour
from vortex.models import DesignObject
from vortex.models import DesignType
from vortex.models import PuakmaServer
from vortex.workspace import Workspace


def grep(
    workspace: Workspace,
    server: PuakmaServer,
    pattern: str,
    *,
    app_ids: list[int] | None = None,
    design_types: list[DesignType] | None = None,
    output_paths: bool = False,
    exclude_resources: bool = True,
) -> int:
    if exclude_resources:
        design_types = [t for t in DesignType if t != DesignType.RESOURCE]

    regex = re.compile(pattern.encode())
    apps = (
        app for app in workspace.listapps(server) if (not app_ids or app.id in app_ids)
    )
    objs = [
        obj
        for app in apps
        for obj in app.design_objects
        if (not obj.is_jar_library)
        and (not design_types or obj.design_type in design_types)
    ]

    _output_match = functools.partial(_output, workspace, output_path=output_paths)

    for obj in sorted(objs, key=lambda obj: obj.name):
        bytes_to_search = obj.design_source if obj.do_save_source else obj.design_data
        match = re.search(regex, bytes_to_search)
        _output_match(match, obj) if match else None

    return 0


def _output(
    workspace: Workspace,
    match: re.Match[bytes],
    obj: DesignObject,
    *,
    output_path: bool,
) -> None:
    try:
        text = match.string.decode()
    except UnicodeDecodeError:
        # Found a binary resource or jar library etc., skip
        return
    line_indx = text.count("\n", 0, match.start())
    line_no = line_indx + 1
    if output_path:
        print(f"{obj.design_path(workspace)}:{line_no}")
    else:
        matched_text = match.group().decode()
        line = text.splitlines()[line_indx].strip()
        new_text = Colour.highlight(matched_text, Colour.RED, line)
        print(f"{Colour.highlight(obj.file_name, Colour.BOLD)}:{line_no}:{new_text}")
