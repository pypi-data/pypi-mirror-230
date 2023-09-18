from loguru._logger import Logger, Core
from typing import Union
import sys
import re

def multilogger(
        sink = sys.stdout,
        name: str = "这个是日志输出中的名字",
        payload: str = "",
        format: str = "<!time>[<level>{level}</level>] <cyan><!name></cyan> | <!payload><!module><level>{message}</level>",
        colorize: bool = True,
        level: str = "INFO",
        notime: bool = False,
        *args,
        **kwargs
) -> Logger:
    module = "" if level != "DEBUG" else "<cyan>{module}</cyan>.<cyan>{name}</cyan>:{line} | "
    payload = f"<red>{payload}</red> | " if payload else ""
    time = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> " if not notime else ""

    for match in re.findall(r"(<!.*?>)", format):
        value = re.match(r"^<!(.*?)>$", match)[1]
        format = re.sub(match, eval(value), format)

    logger_instance = Logger(
        core=Core(),
        exception=None,
        depth=0,
        record=False,
        lazy=False,
        colors=False,
        raw=False,
        capture=True,
        patchers=[],
        extra={},
    )
    logger_instance.configure(handlers=[
        {
            "sink": sink,
            "format": format,
            "colorize": colorize,
            "level": level,
        },
    ])
    return logger_instance

if __name__ == "__main__":
    log = multilogger()
    log.info("第一个模式的logger")
    log2 = multilogger(payload="某个包中用于区分不同的日志", notime=True)#notime不输出时间
    log2.info("第二个logger的输出模式")
    log.info("第一个logger的输出模式")