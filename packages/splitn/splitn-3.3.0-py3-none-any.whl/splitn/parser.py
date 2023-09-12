import argparse
from version import __version__

parser = argparse.ArgumentParser(
        prog="splitn",
        usage="%(prog)s [options] [operands ...] [--pattern | -p <regexes> ...]",
        add_help=False,
        allow_abbrev=False
    )
parser.add_argument(
    "operands",
    nargs="*",
    type=str
)
parser.add_argument(
    "--separator", "-s",
    default=" ",
    type=str
)
parser.add_argument(
    "--times", "-t",
    default=1,
    type=int
)
parser.add_argument(
    "--secondary-separator",
    default="---",
    type=str
)
parser.add_argument(
    "--as-string",
    action="store_true"
)
parser.add_argument(
    "--pattern", "-p",
    nargs="*",
    default=None,
    type=str
)
parser.add_argument(
    "--version", "-v",
    action="version",
    version=f"%(prog)s {__version__}"
)
parser.add_argument(
    "--help", "-h",
    action="store_true"
)
