from __future__ import annotations

import logging
import shutil

from vortex.workspace import Workspace


logger = logging.getLogger("vortex")


def clean(workspace: Workspace) -> int:
    app_dirs = workspace.listdir(strict=False)
    ret = 0
    if app_dirs:
        with workspace.exclusive_lock():
            for app_dir in app_dirs:
                shutil.rmtree(app_dir)
                logger.info(f"Deleted directory '{app_dir}'")
            ret = workspace.update_vscode_settings()
    return ret
