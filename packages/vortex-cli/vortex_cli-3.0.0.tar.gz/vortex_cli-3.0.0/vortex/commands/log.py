from __future__ import annotations

from datetime import datetime

import tabulate

from vortex import util
from vortex.models import PuakmaServer


def log(server: PuakmaServer, limit: int) -> int:
    with server as s:
        logs = s.get_last_log_items(limit)

    row_headers = ("Time", "Type", "Source", "Message")
    row_data = []
    for log in sorted(logs, key=lambda x: (x.id)):
        row = [
            datetime.strftime(log.date, "%H:%M:%S"),
            log.type,
            util.shorten_text(log.item_source),
            log.msg,
        ]
        row_data.append(row)

    print(
        tabulate.tabulate(
            row_data, headers=row_headers, maxcolwidths=[None, None, 30, 80]
        )
    )

    return 0
