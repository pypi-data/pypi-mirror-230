from __future__ import annotations

import asyncio
import base64
import logging
import mimetypes

from vortex.models import DesignObject
from vortex.models import DesignObjectAmbiguousError
from vortex.models import DesignObjectNotFound
from vortex.models import DesignType
from vortex.models import PuakmaServer
from vortex.soap import AppDesigner
from vortex.util import render_objects
from vortex.workspace import Workspace


logger = logging.getLogger("vortex")


def new(
    workspace: Workspace,
    server: PuakmaServer,
    names: list[str],
    app_id: int,
    design_type: DesignType,
    content_type: str | None = None,
    comment: str = "",
    inherit_from: str = "",
    parent_page: str | None = None,
    open_action: str | None = None,
    save_action: str | None = None,
) -> int:
    apps = [app for app in workspace.listapps(server) if app.id == app_id]
    if not apps:
        logger.error(f"No cloned application found with ID {app_id}")
        return 1

    if design_type.is_java_type:
        content_type = "application/java"
    elif design_type == DesignType.PAGE:
        content_type = "text/html"
    _ext = mimetypes.guess_extension(content_type) if content_type else None
    if _ext is None or content_type is None:
        logger.error(f"Unable to determine file type for '{content_type}'")
        return 1

    app = apps.pop()
    objs: list[DesignObject] = []
    for name in names:
        try:
            _, _obj = app.lookup_design_obj(name)
        except DesignObjectNotFound:
            # OK
            pass
        except DesignObjectAmbiguousError as e:
            logger.error(e)
            return 1
        else:
            logger.error(f"Design Object {_obj} already exists in {app}")
            return 1

        design_source = base64.b64encode(design_type.source_template(name)).decode()
        objs.append(
            DesignObject(
                -1,
                name,
                app,
                design_type,
                content_type,
                "",
                design_source,
                comment=comment,
                inherit_from=inherit_from,
                parent_page=parent_page,
                open_action=open_action,
                save_action=save_action,
            )
        )
    if not objs:
        return 1

    _show_params = True if parent_page or open_action or save_action else False
    print("The following Design Objects will be created:\n")
    render_objects(objs, show_params=_show_params)
    if input("\n[Y/y] to continue:") not in ["Y", "y"]:
        return 1

    with workspace.exclusive_lock():
        ret = asyncio.run(_acreate_objects(workspace, server, objs))
        workspace.mkdir(app)
        return ret


async def _acreate_objects(
    workspace: Workspace, server: PuakmaServer, objs: list[DesignObject]
) -> int:
    async with server as s:
        await s.server_designer.ainitiate_connection()
        logger.info(f"Connected to {s.host}")
        tasks = []
        for obj in objs:
            task = asyncio.create_task(_acreate(workspace, s.app_designer, obj))
            tasks.append(task)
        ret = 0
        for done in asyncio.as_completed(tasks):
            try:
                ret |= await done
            except (asyncio.CancelledError, Exception) as e:
                for task in tasks:
                    task.cancel()
                raise e
        return ret


async def _acreate(
    workspace: Workspace,
    app_designer: AppDesigner,
    obj: DesignObject,
) -> int:
    ok = await obj.acreate(app_designer)
    if ok:
        await obj.acreate_params(app_designer)
        obj.app.design_objects.append(obj)
        await asyncio.to_thread(obj.save, workspace)
    return 0 if ok else 1
