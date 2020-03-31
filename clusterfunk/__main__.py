import argparse
import sys

import clusterfunk
import clusterfunk.subcommands


def main(args=None):
    parser = argparse.ArgumentParser(
        prog="clusterfunk",
        usage="clusterfunk <subcommand> <options>",
        description="Miscellaneous clustering tools",
    )

    parser.add_argument("--version", action="version", version=clusterfunk.__version__)
    subparsers = parser.add_subparsers(
        title="Available subcommands", help="", metavar=""
    )

    # _____________________________ phylotype ______________________________#
    subparser_phylotype = subparsers.add_parser(
        "phylotype",
        aliases=['phylotype_dat_tree'],
        usage="clusterfunk phylotype [--threshold] <input> <output> ",
        help="Assigns phylotypes to a tree based on a branch length threshold",
    )

    subparser_phylotype.add_argument(
        "input",
        metavar='input',
        type=str,
        help='The input file currently must be a nexus')

    subparser_phylotype.add_argument(
        "output",
        metavar='output',
        type=str,
        help='The output file currently must be a nexus')
    subparser_phylotype.add_argument(
        '-t',
        '--threshold',
        dest='threshold',
        action='store',
        default=5E-6,
        type=float,
        help='branch threshold used to distinguish new phylotype (default: 5E-6)')

    subparser_phylotype.add_argument(
        '-csv',
        '--csv',
        dest='csv',
        action='store_true',
        default=False,
        help='Boolean flag, should the output be a csv of tips instead of an annotated tree file')

    subparser_phylotype.set_defaults(func=clusterfunk.subcommands.phylotype.run)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
