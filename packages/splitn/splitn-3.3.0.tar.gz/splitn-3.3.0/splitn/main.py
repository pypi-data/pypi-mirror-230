from sys import argv
from os import path
from re import fullmatch
from itertools import tee
from rich.console import Console

from typing import Generator

from loguru import logger

from help import HELP, CONCISE_HELP
from parser import parser

from utils.sequences import random_sequence
from utils.split import split_sequences

console = Console()

@logger.catch
def detect_string(
    input: str
) -> bool:
    try:
        return bool(fullmatch(input, input))
    except Exception:
        return False

@logger.catch
def generate_split_sequences(
    sequence: str,
    separator: str,
    patterns: list[str] | None
) -> Generator[str, None, None]:
    for split_sequence in split_sequences(sequence, separator):
        printable: bool = not patterns
        if patterns:
            for pattern in patterns:
                printable = fullmatch(pattern, split_sequence.strip())
                if printable:
                    break
        if printable:
            yield split_sequence

@logger.catch
def generate_output(
    operand: str,
    separator: str,
    times: int,
    as_string: bool,
    patterns: list[str] | None
) -> Generator[str, None, None]:
    try:
        if as_string or detect_string(operand):
            # handle simple strings
            yield from generate_split_sequences(operand, separator, patterns)
        else: 
            # handle regular expressions
            for counter in range(times):
                sequence = random_sequence(operand)
                yield from generate_split_sequences(sequence, separator, patterns)
                if counter < times - 1:
                    yield ""
    except Exception as e:
        parser.error(f"Program aborted with exception: {e}.")

@logger.catch
def handle_operands(
    operands: list[str],
    separator: str,
    times: int,
    secondary_separator: str,
    as_string: bool,
    patterns: list[str]
) -> Generator[str, None, None]:
    for operand, counter in zip(operands, range(len(operands), 0, -1)):
        if not path.exists(operand):
            yield from generate_output(operand, separator, times, as_string, patterns)
        else:
            with open(operand) as file:
                lines = file.readlines()
                for line, line_counter in zip(lines, range(len(lines), 0, -1)):
                    yield from generate_output(line.strip(), separator, times, as_string, patterns)
                    if line_counter > 1:
                        yield secondary_separator
        if counter > 1:
            yield secondary_separator

@logger.catch
def handle_pattern(
    patterns: list[str],
    times: int,
    secondary_separator: str
) -> Generator[str, None, None]:
    for pattern, counter in zip(patterns, range(len(patterns), 0, -1)):
        for _ in range(times):
            yield random_sequence(pattern)
    if counter > 1:
        yield secondary_separator

@logger.catch
def print_output(
    outputs: Generator
) -> None:
    (outputs_original, outputs_copy) = tee(outputs, 2)
    for _ in range(console.height):
        next_output = next(outputs_original, None)
        if next_output is None:
            break
    if next_output is None:
        for output in outputs_copy:
            console.print(output)
    else:
        with console.pager():
            for output in outputs_copy:
                console.print(output)

@logger.catch
def main(
    args: list[str]
) -> None:
    args = parser.parse_args(args)

    if args.help:
        console.print(HELP)
        parser.exit()

    if not args.operands and not args.pattern:
        console.print(CONCISE_HELP)
        parser.exit(1)
    
    if args.operands:
        print_output(
            handle_operands(args.operands, args.separator, args.times, args.secondary_separator, args.as_string, args.pattern)
        )
        parser.exit()
       
    if args.pattern:
        print_output(
             handle_pattern(args.pattern, args.times, args.secondary_separator)
        )
        parser.exit()

if __name__ == "__main__":
    main(argv[1:])