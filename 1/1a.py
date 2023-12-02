import logging

NUMBERS = '0123456789'

input_path = '1-input.txt'


def find_first_number(line):
    for c in line:
        if c in NUMBERS:
            return int(c)
    raise Exception('No number found')

def find_last_number(line):
    for c in reversed(line):
        if c in NUMBERS:
            return int(c)
    raise Exception('No number found')


with open(input_path) as f:
    lines = list(f.readlines())

subtotal = 0
for line in lines:
    first = find_first_number(line)
    last = find_last_number(line)
    result = f'{first}{last}'
    logging.debug(result)
    subtotal += int(result)

print(subtotal)
