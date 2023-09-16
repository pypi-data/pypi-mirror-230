from __future__ import annotations

import asyncio
import binascii
import logging
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path
from typing import Any

from vortex import util
from vortex.models import DesignObject
from vortex.models import DesignType
from vortex.models import JavaClassVersion
from vortex.models import PuakmaApplication
from vortex.models import PuakmaServer
from vortex.spinner import Spinner
from vortex.workspace import Workspace

logger = logging.getLogger("vortex")


def clone(
    workspace: Workspace,
    server: PuakmaServer,
    app_ids: list[int],
    *,
    get_resources: bool = False,
    open_urls: bool = False,
    reclone: bool = False,
) -> int:
    if reclone:
        app_ids.extend(app.id for app in workspace.listapps(server))

    with (
        workspace.exclusive_lock(),
        Spinner(f"Cloning {app_ids}..."),
    ):
        return asyncio.run(
            _aclone_apps(workspace, server, app_ids, get_resources, open_urls)
        )


async def _aclone_apps(
    workspace: Workspace,
    server: PuakmaServer,
    app_ids: list[int],
    get_resources: bool,
    open_urls: bool,
) -> int:
    tasks = []
    async with server as s:
        await s.server_designer.ainitiate_connection()
        logger.info(f"Connected to {s.host}")

        for app_id in app_ids:
            task = asyncio.create_task(_aclone_app(workspace, s, app_id, get_resources))
            tasks.append(task)

        ret = 0
        for done in asyncio.as_completed(tasks):
            try:
                app, _ret = await done
                if open_urls and app:
                    util.open_app_urls(app)
                ret |= _ret
            except (KeyboardInterrupt, Exception) as e:
                for task in tasks:
                    task.cancel()
                raise e
            except asyncio.CancelledError:
                logger.error("Operation Cancelled")
                for task in tasks:
                    task.cancel()
                ret = 1
                break
        else:
            ret |= workspace.update_vscode_settings()
    return ret


async def _aclone_app(
    workspace: Workspace,
    server: PuakmaServer,
    app_id: int,
    get_resources: bool,
) -> tuple[PuakmaApplication | None, int]:
    """Clone a Puakma Application into a newly created directory"""

    logger.info(f"Cloning [{app_id}] from {server.host}...")

    app_xml, _obj_rows = await asyncio.gather(
        server.app_designer.aget_application_xml(app_id),
        PuakmaApplication.afetch_design_objects(server, app_id, get_resources),
    )

    try:
        app, app_ele = _parse_app_xml(server, app_xml, app_id)
    except (ValueError, KeyError) as e:
        logger.error(e)
        return None, 1

    eles = app_ele.findall("designElement", namespaces=None)
    objs = _aparse_design_objs(_obj_rows, app)
    _match_and_validate_design_objs(objs, eles)

    app.design_objects = objs
    app_dir = workspace.mkdir(app, True)
    try:
        logger.info(f"Saving {len(objs)} ({len(eles)}) Design Objects [{app_id}]...")
        await asyncio.to_thread(_save_objs, workspace, objs)
    except asyncio.CancelledError:
        util.rmtree(app_dir)
        return None, 1

    logger.info(f"Successfully cloned {app} into '{app_dir.name}'")

    return app, 0


def _save_objs(workspace: Workspace, objs: list[DesignObject]) -> None:
    for obj in objs:
        obj.save(workspace)


def _aparse_design_objs(
    objs: list[dict[str, Any]], app: PuakmaApplication
) -> list[DesignObject]:
    ret: list[DesignObject] = []
    for obj in objs:
        design_type_id = int(obj["type"])
        name = obj["name"]
        id_ = int(obj["id"])
        try:
            type_ = DesignType(design_type_id)
        except ValueError:
            logger.debug(
                f"Skipped Design Object '{name}' [{obj['id']}]: "
                f"Invalid Design Type [{design_type_id}]"
            )
            continue
        ret.append(
            DesignObject(
                id_,
                name,
                app,
                type_,
                obj["ctype"],
                obj["data"],
                obj["src"],
            )
        )
    return ret


def _parse_app_xml(
    server: PuakmaServer, app_xml: ET.Element, app_id: int
) -> tuple[PuakmaApplication, ET.Element]:
    app_ele = app_xml.find("puakmaApplication", namespaces=None)
    if not app_ele:
        raise ValueError(f"Application [{app_id}] does not exist")

    java_version_ele = app_xml.find('.//sysProp[@name="java.class.version"]')
    if java_version_ele is None or java_version_ele.text is None:
        raise ValueError("Java class version not specified")
    major, minor = (int(v) for v in java_version_ele.text.split(".", maxsplit=1))
    version: JavaClassVersion = (major, minor)
    app = PuakmaApplication(
        id=int(app_ele.attrib["id"]),
        name=app_ele.attrib["name"],
        group=app_ele.attrib["group"],
        inherit_from=app_ele.attrib["inherit"],
        template_name=app_ele.attrib["template"],
        java_class_version=version,
        host=server.host,
    )
    return app, app_ele


def _validate_crc32_checksum(obj: DesignObject, ele: dict[str, str]) -> bool:
    data = obj.design_source if obj.do_save_source else obj.design_data
    crc32_xml_key = "sourceCrc32" if obj.do_save_source else "dataCrc32"
    crc32_checksum = int(ele.get(crc32_xml_key, 0))
    try:
        return crc32_checksum == zlib.crc32(data)
    except (TypeError, binascii.Error):
        return False


def _match_and_validate_design_objs(
    design_objs: list[DesignObject],
    design_elements: list[ET.Element],
) -> None:
    design_objs_eles = {int(ele.attrib["id"]): ele for ele in design_elements}
    for obj in reversed(design_objs):
        ele = design_objs_eles.get(obj.id)
        if ele is not None:
            obj.is_jar_library = ele.attrib.get("library", "false") == "true"

            package = ele.attrib.get("package", None)
            obj.package_dir = Path(*package.split(".")) if package else None

            open_action_param_ele = ele.find('.//designParam[@name="OpenAction"]')
            if open_action_param_ele is not None:
                obj.open_action = open_action_param_ele.attrib["value"]

            save_action_param_ele = ele.find('.//designParam[@name="SaveAction"]')
            if save_action_param_ele is not None:
                obj.save_action = save_action_param_ele.attrib["value"]

            parent_page_param_ele = ele.find('.//designParam[@name="ParentPage"]')
            if parent_page_param_ele is not None:
                obj.parent_page = parent_page_param_ele.attrib["value"]

        if ele is None or not _validate_crc32_checksum(obj, ele.attrib):
            design_objs.remove(obj)
            logger.warning(
                f"Unable to validate Design Object {obj}. It will not be saved."
            )
