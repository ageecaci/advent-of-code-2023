[aoc.2023]: https://adventofcode.com/2023

# Advent of Code 2023

Solutions for [Advent of Code 2023][aoc.2023].

## Requirements

- VS Code with Dev Containers extension **or** Python 3 (developed against 3.11)

## Puzzle Input

Puzzle examples are included with each puzzle problem statement.
The solutions here assume these will be in files named
`<day>[sub-problem]-examples[optional-suffix].txt`
in the respective subdirectories,
where:

- `<day>` should be replaced with the name of the directory;
- `[sub-problem]` can either be omitted
  (if all problems share the same example)
  or should use the same suffix as the script being run;
- `optional-suffix` can be anything,
  but will need to be specified at the command line when running the script.

Puzzle inputs are generated on a per-user basis.
To get your puzzle inputs, please sign in to the AoC site.
The solutions here assume these will be in files named
`<day>[sub-problem]-input[optional-suffix].txt`
in the respective subdirectories,
similarly to the above.

## Run the Code

Make sure to setup any necessary example or input data first.
For every solution,
running the script without arguments will use a relevant `-input.txt` file.
The `-e` parameter can be specified on the command line
to instead have the script search for a relevant `-examples.txt` file.
Any text specified without a leading dash (`-`)
will be assumed to be a filename suffix.

The `-v` parameter will enable debug logging - where available.
This mode provides additional hints as to the steps taken while solving.
Setting the parameter multiple times increases the verbosity of the logging.
(Up to 3 levels currently supported by some scripts.)

Some solutions (from day 3 onwards) make use of external libraries.
To execute these, the configured virtual environment must first be configured then activated.
The setup script assumes a UNIX virtual environment will be created.

```sh
./setup.sh
. ./.venv/bin/activate
DAY=1
"${DAY}/${DAY}a.py" -vvve # can use `${DAY}/${DAY}a-examples.txt` as input
"${DAY}/${DAY}a.py" -ve 2 # can use `${DAY}/${DAY}a-examples2.txt` as input
"${DAY}/${DAY}a.py"       # can use `${DAY}/${DAY}a-input.txt` as input
"${DAY}/${DAY}b.py"       # can use `${DAY}/${DAY}b-input.txt` as input
```

To validate several days' worth of solutions
(for example to validate expected behaviour after refactoring)
a template "validate" shell script is included.
If given the expected solutions,
this simply runs each script in turn.
Make a copy of the template,
insert any appropriate solutions,
and uncomment the respective lines.
