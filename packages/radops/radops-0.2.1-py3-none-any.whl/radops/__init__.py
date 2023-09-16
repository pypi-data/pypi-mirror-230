import datetime
from importlib.metadata import PackageNotFoundError, version

from radops.settings import settings

try:
    __version__ = version("radops")
except PackageNotFoundError:
    __version__ = ""


def radops_print(msg):
    if not settings.verbose:
        return
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    BLUE = "\033[38;5;67m"
    ENDC = "\033[0m"

    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"{BLUE}{BOLD}radops{ENDC} {GRAY}[{time}]{ENDC} {msg}")
