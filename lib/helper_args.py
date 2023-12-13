import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--examples', action='store_true', help='use examples as input')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='include debug output; set multiple times to increase verbosity')
    parser.add_argument('file_suffix', nargs='?', help='additional file suffix to look for debug output')
    return parser.parse_args()
