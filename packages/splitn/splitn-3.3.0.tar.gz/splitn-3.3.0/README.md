`splitn` is a CLI application that generates combinations of chars being a result of splitting strings provided *explicite* or randomly generated from regex patterns. It is made mainly for testing NLU applications, e.g. chatbots or tools for extracting structural data from text like [duckling](https://github.com/facebook/duckling).

# Installation
```
pipx install splitn
```

or

```
pip install splitn
```

# Examples
## Basic usage
```bash
$ splitn 486
486
48 6
4 86
4 8 6
```

## Using with regular expressions
```bash
$ splitn "\d{3"
427
4 27
42 7
4 2 7
```

## Using with file
Let's assume that file `example.txt` contains following lines.
```
abc
\d{2}
```

```bash
$ splitn example.txt
abc
a bc
ab c
a b c
---
04
0 4
```

## Options
### --separator
```bash
$ splitn abc -s -
abc
a-bc
ab-c
a-b-c
```

### --times
```bash
$ splitn "\d{2}" -t 2
59
5 9

35
3 5
```

### --secondary-separator
```bash
$ splitn abc def --secondary-separator +++
abc
a bc
ab c
a b c
+++
def
d ef
de f
d e f
```

### --as-string
```bash
$ splitn "\d{2}" --as-string
\d{2}
\ d{2}
\d {2}
\d{ 2}
\d{2 }
\ d {2}
\ d{ 2}
\ d{2 }
\d { 2}
\d {2 }
\d{ 2 }
\ d { 2}
\ d {2 }
\ d{ 2 }
\d { 2 }
\ d { 2 }
```

### --pattern
This option can be used with or without positional arguments. When used without, it makes splitn generate random sequences based on given regular expressions. When used with operands, it narrows down generated sequences to those matching provided regular expressions.

```bash
$ splitn -p "\d \d .{2}"
8 1 Ua
```

```bash
$ splitn "\d{4}" -p "\d \d .*"
5 9 20
5 9 2 0
```