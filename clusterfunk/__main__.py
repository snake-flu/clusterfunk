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

    shared_arguments_parser = argparse.ArgumentParser(add_help=False)

    shared_arguments_parser.add_argument(
        "-i"
        "--input",
        metavar='input.tree',
        dest="input",
        type=str,
        required=True,
        help='The input tree file. Format can be specified with the format flag.')
    shared_arguments_parser.add_argument(
        "-o"
        "--output",
        metavar='output.*',
        dest="output",
        type=str,
        required=True,
        help='The output file')

    shared_arguments_parser.add_argument(
        '--format',
        metavar="nexus, newick",
        dest='format',
        action='store',
        default="nexus",
        help='what format is the tree file. This is passed to dendropy. default is \'nexus\'')

    shared_arguments_parser.add_argument(
        "-c",
        "--collapse_to_polytomies",
        dest='collapse',
        action='store_true',
        default=False,
        help='A boolean flag to collapse branches with length 0. Before running the rule.')

    subparsers = parser.add_subparsers(
        title="Available subcommands", help="", metavar=""
    )

    # _____________________________ phylotype ______________________________#
    subparser_phylotype = subparsers.add_parser(
        "phylotype",
        aliases=['phylotype_dat_tree'],
        usage="clusterfunk phylotype [--threshold] -i my.tree -o my.phylotyped.tree",
        help="Assigns phylotypes to a tree based on a branch length threshold",
        parents=[shared_arguments_parser]
    )


    subparser_phylotype.add_argument(
        '-t',
        '--threshold',
        dest='threshold',
        action='store',
        default=5E-6,
        type=float,
        help='branch threshold used to distinguish new phylotype (default: 5E-6)')


    subparser_phylotype.set_defaults(func=clusterfunk.subcommands.phylotype.run)
    # _____________________________ tree annotator ______________________________#
    subparser_annotate = subparsers.add_parser(
        "annotate_tree",
        aliases=['annotate_dat_tree'],
        usage="clusterfunk annotate [--acctran/--deltran] [--ancestral_state UK] --traits country -i my.tree -o my.annotated.tree ",
        help="Annotates a tree. Can annotate tips from a csv, and/or annotate internal nodes from tips based on parsimony",
        parents=[shared_arguments_parser]
    )

    subparser_annotate.add_argument(
        "-t",
        "--traits",
        metavar='traits',
        required=True,
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
        '--indices',
        dest='indices',
        action='store',
        type=int,
        nargs="+",
        help='optional indices for use in getting traits from tip labels')

    subparser_annotate.add_argument(
        "-s",
        "--separator",
        dest="separator",
        type=str,
        help="optional separator used to get trait"
    )

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

    subparser_annotate.add_argument(
        '-a',
        '--ancestral_state',
        metavar='ancestral_state',
        action='store',
        nargs="+",
        help="Option to Set the ancestral state for the tree. In same order of traits")

    subparser_annotate.set_defaults(func=clusterfunk.subcommands.annotate_tree.run)

    # _____________________________ extract_tip_annotations ______________________________#
    subparser_extract_tip_annotations = subparsers.add_parser(
        "extract_tip_annotations",
        aliases=['extract_dat_tree'],
        usage="clusterfunk extract_annotations --traits country -i my.annotated.tree -o annotations.csv",
        help="extracts annotations from tips in a tree",
    )

    subparser_extract_tip_annotations.add_argument(
        "-t",
        "--traits",
        metavar='traits',
        type=str,
        required=True,
        nargs="+",
        help='Space separated list of traits to extract from tree')

    subparser_extract_tip_annotations.set_defaults(func=clusterfunk.subcommands.extract_tip_annotations.run)
    # _____________________________ get_taxa ______________________________#

    subparser_get_taxa = subparsers.add_parser(
        "get_taxa",
        aliases=['get_dat_taxa'],
        usage="clusterfunk get_taxa  -i input.tree -o taxa.txt",
        help="extracts taxa labels from tips in a tree",
    )

    subparser_get_taxa.set_defaults(func=clusterfunk.subcommands.get_taxa.run)

    # _____________________________ label_transitions ______________________________#

    subparser_label_transitions = subparsers.add_parser(
        "label_transitions",
        aliases=['label_dat_transition'],
        usage="clusterfunk label_transitions --trait UK --parent False --child True <input> <output>",
        help="counts and labels transitions of binary traits on a tree",
    )

    subparser_label_transitions.add_argument(
        "-t",
        "--trait",
        metavar='trait',
        type=str,
        help=' Trait whose transitions are begin put on tree')

    subparser_label_transitions.add_argument(
        "--from",
        dest='From',
        type=str,
        help='Label transitions from this state. Can be combined with to.')
    subparser_label_transitions.add_argument(
        "--to",
        dest='to',
        type=str,
        help='Label transitions to this state. Can be combined with from.')
    subparser_label_transitions.add_argument(
        "--transition_name",
        dest='transition_name',
        type=str,
        help='The name of the annotation that will hold transitions. This also will form the base of the transition '
             'label.')

    subparser_label_transitions.add_argument(
        "-e",
        "--exploded_trees",
        dest='exploded_trees',
        action='store_true',
        default=False,
        help='A boolean flag to output a nexus for each transition. In this case the ouput argument is treated as a directory and made if it doesn\'t exist')

    subparser_label_transitions.add_argument(
        "-ip",
        "--include_parent",
        dest='include_parent',
        action='store_true',
        default=False,
        help='A boolean flag to inlcude transition parent node in exploded trees')

    subparser_label_transitions.set_defaults(func=clusterfunk.subcommands.label_transitions.run)

    # _____________________________ subtype ______________________________#
    subparser_subtyper = subparsers.add_parser(
        "subtype",
        aliases=['subtype_dat_sample'],
        usage="clusterfunk subtype [--separator] [--index] [--taxon] <input> <output> ",
        help="Annotates a specified tip with a specified trait ",
    )
    subparser_subtyper.add_argument(
        "-i",
        "--index",
        dest="index",
        type=int,
        help="The index of the trait to reconstruct when the tip label is split by the  separator"
    )

    subparser_subtyper.add_argument(
        "-s",
        "--separator",
        dest="separator",
        type=str,
        help="optional separator used to get trait"
    )

    subparser_subtyper.add_argument(
        "-t",
        "--taxon",
        dest='taxon',
        type=str,
        help='The tip label to get')


    subparser_subtyper.set_defaults(func=clusterfunk.subcommands.subtyper.run)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
