import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--examples', action='store_true', help='use examples as input')
    parser.add_argument('-v', '--verbose', action='store_true', help='include debug output')
    return parser.parse_args()
