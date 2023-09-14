#!/usr/bin/env python3
import argparse
from importlib.metadata import version

from . import spider


def formatter(prog): return argparse.HelpFormatter(prog, max_help_position=52)


parser = argparse.ArgumentParser(
    formatter_class=formatter, prog='refrot',
    usage='%(prog)s [options]')
parser.add_argument(dest='url')
parser.add_argument('--ignore-external-links', '-i',
                    action='store_true',
                    help='ignore external links')
parser.add_argument('--user-agent', '-u', metavar='AGENT',
                    help='user agent')
parser.add_argument('-v', '--version',
                    action='version',
                    version='refrot version ' + version('refrot'))


def main():
    args = parser.parse_args()
    spider.main(args)

