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

    shared_required = shared_arguments_parser.add_argument_group("Required")
    shared_required.add_argument(
            "-i",
            "--input",
            metavar='input.tree',
            dest="input",
            type=str,
            required=True,
            help='The input tree file. Format can be specified with the format flag.')
    shared_required.add_argument(
            "-o",
            "--output",
            metavar='output.*',
            dest="output",
            type=str,
            required=True,
            help='The output file')

    shared_arguments_parser.add_argument(
            '--format',
            dest='format',
            action='store',
            default="nexus",
            choices=['nexus', 'newick', 'nexml'],
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
        parents=[shared_arguments_parser]

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
        parents=[shared_arguments_parser]

    )

    subparser_get_taxa.set_defaults(func=clusterfunk.subcommands.get_taxa.run)

    # _____________________________ label_transitions ______________________________#

    subparser_label_transitions = subparsers.add_parser(
        "label_transitions",
        aliases=['label_dat_transition'],
        usage="clusterfunk label_transitions --trait UK --from False --to True --transition_name introduction -i my.tree -o my.labeled.tree",
        help="counts and labels transitions of binary traits on a tree",
        parents=[shared_arguments_parser]

    )

    subparser_label_transitions.add_argument(
        "-t",
        "--trait",
        metavar='trait',
        type=str,
        required=True,
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
        required=True,
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
        usage="clusterfunk subtype --separator \"|\" --index 2 --taxon my|fav|taxon -i my.tree -o my.csv ",
        help="Annotates a specified tip with a specified trait ",
        parents=[shared_arguments_parser]
    )
    subparser_subtyper.add_argument(
        "--index",
        dest="index",
        type=int,
        required=True,
        help="The index of the trait to reconstruct when the tip label is split by the  separator"
    )

    subparser_subtyper.add_argument(
        "-s",
        "--separator",
        dest="separator",
        type=str,
        required=True,
        help="optional separator used to get trait"
    )

    subparser_subtyper.add_argument(
            "-t",
            "--taxon",
            dest='taxon',
            type=str,
            required=True,
            help='The tip label to get')

    subparser_subtyper.set_defaults(func=clusterfunk.subcommands.subtyper.run)

    # _____________________________ prune ______________________________#

    subparser_prune = subparsers.add_parser(
            "prune",
            aliases=['subtype_dat_tree'],
            usage="clusterfunk subtype --extract [--fasta file.fas] [--taxon taxon.set.txt] [--metadata metadata.csv/tsv --index-column taxon] -i my.tree -o my.smaller.tree ",
            help="Prunes a tree either removing the specified taxa or keeping only those specified. "
                 "Taxa can be specified from a fasta file, text file or metadata file with the taxon label indicated",
            parents=[shared_arguments_parser]
    )

    subparser_prune.add_argument(
            "--extract",
            action="store_true",
            dest="extract",
            default=False,
            help="Boolean flag to extract and return the subtree defined by the taxa"
    )

    subparser_prune.add_argument(
            "--index-column",
            dest="index",
            help="column of metadata that holds the taxon names"
    )

    taxon_set_files = subparser_prune.add_mutually_exclusive_group(required=True)

    taxon_set_files.add_argument(
            "--fasta",
            help="incoming fasta file defining taxon set"
    )
    taxon_set_files.add_argument(
            "--taxon",
            help="incoming text file defining taxon set with a new taxon on each line"
    )
    taxon_set_files.add_argument(
            "--metadata",
            help="incoming csv/tsv file defining taxon set."
    )

    subparser_subtyper.set_defaults(func=clusterfunk.subcommands.prune.run)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
