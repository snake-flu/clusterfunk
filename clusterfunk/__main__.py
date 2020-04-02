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
    # _____________________________ tree annotator ______________________________#
    subparser_annotate = subparsers.add_parser(
        "annotate_tree",
        aliases=['annotate_dat_tree'],
        usage="clusterfunk annotate  <input> <output> ",
        help="Annotates a tree. Can annotate tips from a csv, and/or annotate internal nodes from tips based on parsimony",
    )

    subparser_annotate.add_argument(
        "input",
        metavar='input',
        type=str,
        help='The input file currently must be a nexus')
    subparser_annotate.add_argument(
        "output",
        metavar='output',
        type=str,
        help='The output file currently must be a nexus')

    subparser_annotate.add_argument(
        "-t",
        "--traits",
        metavar='traits',
        type=str,
        nargs="+",
        help='Space separated list of traits to annotate on tree')

    subparser_annotate.add_argument(
        '-tf',
        '--traits_file',
        dest='traits_file',
        action='store',
        type=str,
        help='optional csv file with tip annotations ')

    subparser_annotate.add_argument(
        '-acc',
        '--acctran',
        dest='acctran',
        action='store_true',
        help="Boolean flag to use acctran reconstruction")

    subparser_annotate.add_argument(
        '-del',
        '--deltran',
        dest='deltran',
        action='store_true',
        help="Boolean flag to use deltran reconstruction")

    subparser_annotate.set_defaults(func=clusterfunk.subcommands.annotate_tree.run)

    # _____________________________ extract_tip_annotations ______________________________#
    subparser_extract_tip_annotations = subparsers.add_parser(
        "extract_tip_annotations",
        aliases=['extract_dat_tree'],
        usage="clusterfunk extract_annotations [--traits]  <input> <output> ",
        help="extracts annotations from tips in a tree",
    )

    subparser_extract_tip_annotations.add_argument(
        "input",
        metavar='input',
        type=str,
        help='The input file currently must be a nexus')

    subparser_extract_tip_annotations.add_argument(
        "output",
        metavar='output',
        type=str,
        help='The output file currently must be a csv')
    subparser_extract_tip_annotations.add_argument(
        "-t",
        "--traits",
        metavar='traits',
        type=str,
        nargs="+",
        help='Space separated list of traits to extract from tree')

    subparser_extract_tip_annotations.set_defaults(func=clusterfunk.subcommands.extract_tip_annotations.run)
    # _____________________________ get_taxa ______________________________#

    subparser_get_taxa = subparsers.add_parser(
        "get_taxa",
        aliases=['get_dat_taxa'],
        usage="clusterfunk get_taxa  <input> <output> ",
        help="extracts taxa labels from tips in a tree",
    )

    subparser_get_taxa.add_argument(
        "input",
        metavar='input',
        type=str,
        help='The input file currently must be a nexus')

    subparser_get_taxa.add_argument(
        "output",
        metavar='output',
        type=str,
        help='The output file is a text file')
    subparser_get_taxa.set_defaults(func=clusterfunk.subcommands.get_taxa.run)

    # _____________________________ label_transitions ______________________________#

    subparser_label_transitions = subparsers.add_parser(
        "label_transitions",
        aliases=['label_dat_transition'],
        usage="clusterfunk label_transitions [--trait] [--parent] [--child] <input> <output>",
        help="labels counts and labels transitions on a tree",
    )

    subparser_label_transitions.add_argument(
        "input",
        metavar='input',
        type=str,
        help='The input file currently must be a nexus')

    subparser_label_transitions.add_argument(
        "output",
        metavar='output',
        type=str,
        help='The output file is a text file')

    subparser_label_transitions.add_argument(
        "-t",
        "--trait",
        metavar='trait',
        type=str,
        help=' Trait key to extract from tree')

    subparser_label_transitions.add_argument(
        "-p",
        "--parent_state",
        metavar='parent_state',
        type=str,
        help='parent state for transitions')

    subparser_label_transitions.add_argument(
        "-c",
        "--child_state",
        metavar='child_state',
        type=str,
        help='child state for transitions')

    subparser_label_transitions.set_defaults(func=clusterfunk.subcommands.label_transitions.run)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
