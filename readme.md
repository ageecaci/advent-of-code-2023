[aoc.2023]: https://adventofcode.com/2023

# Advent of Code 2023

Solutions for [Advent of Code 2023][aoc.2023].

## Requirements

- VS Code with Dev Containers extension **or** Python 3 (developed against 3.11)

## Puzzle Input

Puzzle examples are included with each puzzle problem statement.
The solutions here assume these will be in files named
`<day>[sub-problem]-examples.txt`
in the respective subdirectories,
where `<day>` should be replaced with the name of the directory,
and `[sub-problem]` can either be omitted
(if all problems share the same example)
or should use the same suffix as the script being run.

Puzzle inputs are generated on a per-user basis.
To get your puzzle inputs, please sign in to the AoC site.
The solutions here assume these will be in files named
`<day>[sub-problem]-input.txt`
in the respective subdirectories,
similarly to the above.

## Run the Code

Make sure to setup any necessary example or input data first.
For every solution,
running the script without arguments will use a relevant `-input.txt` file.
The `-e` parameter can be specified on the command line
to instead have the script search for a relevant `-examples.txt` file.

The `-v` parameter will enable debug logging - where available.
This mode provides additional hints as to the steps taken while solving.

Some solutions (from day 3 onwards) make use of external libraries.
To execute these, the configured virtual environment must first be configured then activated.
The setup script assumes a UNIX virtual environment will be created.

```sh
./setup.sh
. ./.venv/bin/activate
DAY=1
"${DAY}/${DAY}a.py" -ve
"${DAY}/${DAY}a.py"
"${DAY}/${DAY}b.py"
```
