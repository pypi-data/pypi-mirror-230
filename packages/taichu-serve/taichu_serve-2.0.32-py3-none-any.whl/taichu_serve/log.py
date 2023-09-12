import json
import logging
import sys
from typing import Optional

from flask import request, g
from taichu_serve.common import Local


class JsonFormatter(logging.Formatter):

    def __init__(
            self,
            fmt: Optional[str] = "%(asctime)s",
            datefmt: Optional[str] = None,
            style: Optional[str] = "%",
    ) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def formatMessage(self, record: logging.LogRecord, *args, **kwargs) -> str:
        super().formatMessage(record)

        request_id = None
        try:
            if request and request.headers:
                if 'x_request_id' in request.headers:
                    request_id = request.headers.get('x_request_id')
            if not request_id:
                request_id = g.request_id
        except Exception:
            pass

        if request_id is None:
            try:
                request_id = Local.request_id
            except Exception:
                pass

        data = {
            "time": record.asctime,
            "level": record.levelname,
            "message": record.message,
            "request_id": request_id,
            "logger": record.name,
            'log_path': f'{record.pathname}:{record.lineno}',
            'source': 0
        }

        exclude_fields = ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
                          'module', 'exc_info', 'exc_text', 'stack_info', 'lineno',
                          'funcName', 'created', 'msecs', 'relativeCreated', 'threadName',
                          'processName', 'asctime']
        for (k, v) in record.__dict__.items():
            if k not in exclude_fields:
                data[k] = v

        return json.dumps(data, ensure_ascii=False)


def init_logger(json_format: bool = False):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.handlers = []
    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    if json_format:
        consoleHandler.setFormatter(JsonFormatter(datefmt='%Y-%m-%d %H:%M:%S'))
    else:
        consoleHandler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s %(pathname)s:%(lineno)d - [PID:%(process)d] %(message)s'))
    logger.addHandler(consoleHandler)
