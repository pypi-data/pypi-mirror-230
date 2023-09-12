from rich.console import Group
from rich.panel import Panel
from rich.table import Table

DESCRIPTION = """
[underline]splitn[/underline] - a CLI application that generates combinations of chars being a result of splitting strings
"""

USAGE = """
[yellow]Usage:[/yellow]  [b]splitn \\[options] \\[strings... | regexes... | files...]
        splitn \\[options] \\[strings... | regexes... | files...] --pattern | -p <regexes...>
        splitn \\[--times <integer>] \\[--secondary-separator <string>] --pattern | -p <regexes...>[/b]"""

EXAMPLE = """
$ splitn abc "\\d{2}"
abc
a bc
ab c
a b c
---
60
6 0"""

EPILOG = "For options, use 'splitn --help'."

ARGUMENTS = Table(box=None)
ARGUMENTS.add_column(justify="left")
ARGUMENTS.add_column(justify="left", style="yellow")
ARGUMENTS.add_column(justify="left")
ARGUMENTS.add_row(
    "operands",
    "\\[strings... | regexes... | files...]",
    "List of strings, regular expressions or files.\nProvided files should contain a list of strings or regular expressions.\nRegular expressions should have \"\\\" escaped (eg. \"\\d\") or be inside quotes.\nGiven operands are treated as regular expressions by default."
)

OPTIONS = Table(box=None)
OPTIONS.add_column(justify="left", style="green")
OPTIONS.add_column(justify="left", style="cyan")
OPTIONS.add_column(justify="left", style="yellow")
OPTIONS.add_column(justify="left")
OPTIONS.add_row(
    "-s",
    "--separator",
    "<string>",
    "Separator used in splitting generated sequences. \\[default:' ']"
)
OPTIONS.add_row(
    "-t",
    "--times",
    "<int>",
    "Number of times splitn generates sequences for each specification. Applied only for regular expressions. \\[default: 1]"
)
OPTIONS.add_row(
    "",
    "--secondary-separator",
    "<string>",
    "Separator used to separate outputs from different provided specifications. Use empty string for having new line. \\[default: ---]"
)
OPTIONS.add_row(
    "",
    "--as-string",
    "",
    "Interpret provided operands as simple strings."
)
OPTIONS.add_row(
    "-p",
    "--pattern",
    "<regexes...>",
    "Use this option to either generate random sequence from regular expressions without splitting, or to narrow down sequences generated from given operands to those matching provided regular expressions. \\[default: None]"
)
OPTIONS.add_row(
    "-v",
    "--version",
    "",
    "Show version of splitn."
)
OPTIONS.add_row(
    "-h",
    "--help",
    "",
    "Show this message."
)

CONCISE_HELP = Group(
    DESCRIPTION,
    USAGE,
    "\n",
    Panel(
        EXAMPLE,
        title="Example",
        title_align="left"
    ),
    EPILOG
)

HELP = Group(
    DESCRIPTION,
    USAGE,
    "\n",
    Panel(
        ARGUMENTS,
        title="Arguments",
        title_align="left"
    ),
    Panel(
        OPTIONS,
        title="Options",
        title_align="left"
    )
)
