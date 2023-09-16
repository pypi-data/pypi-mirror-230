"""
contextvars 上下文变量应该在顶级模块中创建，且永远不要在闭包中创建。
Context 对象拥有对上下文变量的强引用，这可以让上下文变量被垃圾收集器正确回收。
"""
import logging
import os
import coloredlogs

from logging import Filter
from logging.handlers import RotatingFileHandler
from contextvars import ContextVar

from eai_commons import trace_id_context as eai_trace_id_context


class TraceIdFilter(Filter):
    trace_id_context: ContextVar = None

    def __init__(self, trace_id_context: ContextVar = None):
        self.trace_id_context = trace_id_context
        super().__init__()

    def filter(self, record):
        record.trace_id = (
            self.trace_id_context.get() if self.trace_id_context else "N/A"
        )
        return True


def _default_format_string():
    return "%(asctime)s|tid=%(trace_id)s|%(name)s|%(levelname)s|%(threadName)s|%(filename)s:%(funcName)s:%(lineno)s - %(message)s"


def _default_date_format_string():
    return "%Y-%m-%d %H:%M:%S %z"


def _add_file_handler(
    logger_: logging.Logger,
    dir_path: str,
    logs_path: str,
    trace_id_context: ContextVar = None,
):
    if dir_path:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        filename = f"{dir_path}/{logger_.name}.log"
    elif logs_path:
        folder_path = os.path.dirname(logs_path)
        if not os.path.exists(folder_path):
            os.makedirs(dir_path, exist_ok=True)
        filename = logs_path
    else:
        return

    file_handler = RotatingFileHandler(
        filename=filename,
        mode="a",
        maxBytes=1024 * 1024 * 100,
        backupCount=7,
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter(
            fmt=_default_format_string(), datefmt=_default_date_format_string()
        )
    )

    file_handler.addFilter(TraceIdFilter(trace_id_context))
    logger_.addHandler(file_handler)


def _terminal_file_handler(
    logger_: logging.Logger, trace_id_context: ContextVar = None
):
    terminal_handler = logging.StreamHandler()
    terminal_handler.setLevel(logging.DEBUG)
    terminal_handler.setFormatter(
        coloredlogs.ColoredFormatter(
            fmt=_default_format_string(),
            datefmt=_default_date_format_string(),
            field_styles={
                "levelname": {"color": "blue"},
                "asctime": {"color": "green"},
            },
            level_styles={"debug": {}, "error": {"color": "red"}},
        )
    )

    terminal_handler.addFilter(TraceIdFilter(trace_id_context))
    logger_.addHandler(terminal_handler)


class Logger:
    """
    输出内容类似：
    2023-09-04 12:01:01 +0800|tid=467ee7c3f9dc47ec93408f089d478699|eai_commons|INFO|MainThread|trace.py:wrapper:19 - log的内容

    Example:
        ``
        from eai_commons.logging import Logger

        logger = Logger.from_name_path("eai", "/Users/weijueye/PycharmProjects/eai_commons/logs")
        logger.info("写点日志")
        ``

        其余logger的handler:
        ``
        from eai_commons.logging import Logger

        from uvicorn import logging as uvicorn_logging  # 需要补充handler的logger

        Logger.wrap_logger(uvicorn_logging, "/Users/weijueye/PycharmProjects/eai_commons/logs")
        ``

    """

    @classmethod
    def from_name_path(
        cls,
        name: str,
        dir_path: str = None,
        logs_path: str = None,
        trace_id_context: ContextVar = eai_trace_id_context,
    ) -> logging.Logger:
        """
        :param name: log context name
        :param dir_path: log 保存的目录，如果logs_path有值，优先以{dir_path}/{name}.log保存
        :param logs_path: log 文件保存的目录，如果dir_path有值，优先以{dir_path}/{name}.log保存
        :param trace_id_context: trace_id_context
        :return:
        """

        logger_ = logging.getLogger(name)
        logger_.setLevel(logging.INFO)
        _terminal_file_handler(logger_, trace_id_context)

        if dir_path or logs_path:
            _add_file_handler(logger_, dir_path, logs_path, trace_id_context)

        return logger_

    @classmethod
    def wrap_logger(
        cls,
        logger_: logging.Logger,
        dir_path: str = None,
        logs_path: str = None,
        trace_id_context: ContextVar = eai_trace_id_context,
    ) -> None:
        """
        :param logger_: logging.Logger对象，需要被wrapper的
        :param dir_path: log 保存的目录，如果logs_path有值，优先以{dir_path}/{name}.log保存
        :param logs_path: log 文件保存的目录，如果dir_path有值，优先以{dir_path}/{name}.log保存
        :param trace_id_context: trace_id_context
        :return:
        """

        logger_.handlers.clear()
        _terminal_file_handler(logger_, trace_id_context)
        if dir_path or logs_path:
            _add_file_handler(logger_, dir_path, logs_path, trace_id_context)


logger = Logger.from_name_path("eai_commons")
