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
            type=float,
            help='A optional flag to collapse branches with length < the input before running the rule.')

    subparsers = parser.add_subparsers(
            title="Available subcommands", help="", metavar=""
    )

    # _____________________________ phylotype ______________________________#
    subparser_phylotype = subparsers.add_parser(
            "phylotype",
            aliases=['phylotype_dat_tree'],
            usage="clusterfunk phylotype [--threshold] [---suffix] --inputmy.tree --output my.phylotyped.tree",
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

    subparser_phylotype.add_argument(
            '-s',
            '--suffix',
            default="p",
            type=str,
            help='suffix for each phylotype'
    )

    subparser_phylotype.set_defaults(func=clusterfunk.subcommands.phylotype.run)
    # _____________________________ tree annotator ______________________________#
    subparser_annotate = subparsers.add_parser(
            "annotate_tree",
            aliases=['annotate_dat_tree'],
            usage="clusterfunk annotate [--acctran/--deltran] [--ancestral_state UK] --traits country --input my.tree --output my.annotated.tree ",
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
            '--boolean-values',
            dest="values",
            nargs="+",
            help="A list of values in order of the traits listed. A boolean annotation will be added for each node"
                 "with the trait sepecifying whether or not it equals this value")

    subparser_annotate.add_argument(
            '-mrca',
            '--mrca',
            nargs="+",
            help="An optional list of traits for which the mrca of each value in each trait"
                 "will be annotated with '[trait_name]-mrca and assigned that value"
    )

    from_tip_group = subparser_annotate.add_argument_group("Annotating from taxon labels")
    from_meta_data = subparser_annotate.add_argument_group("Annotation from metadata file")

    from_tip_group.add_argument(
            "--from-tip-labels",
            action="store_true",
            dest="from_tip_labels",
            help="Boolean flag signifying traits will come from tip labels",
            default=False
    )

    from_tip_group.add_argument(
            '--indices',
            dest='indices',
            action='store',
            type=int,
            nargs="+",
            help='optional indices for use in getting traits from tip labels')

    from_tip_group.add_argument(
            "-s",
            "--separator",
            dest="separator",
            type=str,
            help="optional separator used to split taxon label"
    )

    ancestral_reconstruction = subparser_annotate.add_argument_group("Ancestral reconstruction")

    ancestral_reconstruction.add_argument(
            '-acc',
            '--acctran',
            dest='acctran',
            action='store_true',
            help="Boolean flag to use acctran reconstruction")

    ancestral_reconstruction.add_argument(
            '-del',
            '--deltran',
            dest='deltran',
            action='store_true',
            help="Boolean flag to use deltran reconstruction")

    ancestral_reconstruction.add_argument(
            '--ancestral_state',
            metavar='ancestral_state',
            action='store',
            nargs="+",
            help="Option to Set the ancestral state for the tree. In same order of traits")
    ancestral_reconstruction.add_argument(
            '--majority_rule',
            action='store_true',
            default=False,
            help="A Boolean flag. In trait reconstruction, at a polytomy, when there is no intersection of traits from all children"
                 "should the trait that appears most in the children"
                 "be assigned. Default:False - the union of traits are assigned"
    )

    from_meta_data.add_argument(
            '--in-metadata',
            dest='traits_file',
            action='store',
            type=str,
            help='optional csv file with tip annotations ')

    from_meta_data.add_argument(
            '--index-column',
            dest="index_column",
            default="taxon",
            help="What column in the csv should be used to match the tip names."
    )

    from_meta_data.add_argument(
            '--taxon-key-index',
            dest="taxon_key_index",
            type=int,
            help="After spliting taxon names at separator which entry matches the metadata index column entry."
    )
    from_meta_data.add_argument(
            "--taxon-separator",
            dest="taxon_separator",
            type=str,
            help="optional separator used to split taxon label. To be used if only part of a taxon name is to be matched"
                 "in the metatdata file"
    )

    subparser_annotate.set_defaults(func=clusterfunk.subcommands.annotate_tree.run)

    # _____________________________ re annotator ______________________________#
    subparser_reannotate = subparsers.add_parser(
            "reannotate_tree",
            aliases=['annotate_dat_tree_again'],
            usage="clusterfunk reannotate  --traits country -i my.tree -o my.annotated.tree ",
            help="ReAnnotates a tree. It assigns a traits from a csv to tips. then grabs the mrca of those tips and"
                 " pushes the annotation up to any new tip",
            parents=[shared_arguments_parser]
    )

    subparser_reannotate.add_argument(
            "-t",
            "--traits",
            metavar='traits',
            required=True,
            type=str,
            nargs="+",
            help='Space separated list of traits to annotate on tree')

    subparser_reannotate.add_argument(
            '-tf',
            '--traits_file',
            dest='traits_file',
            action='store',
            type=str,
            help='optional csv file with tip annotations assumes taxon is the key column.')

    subparser_reannotate.add_argument(
            '-f',
            '--filter',
            dest='filter',
            metavar="<key>=<value>",
            type=str,
            help='optional filters for which tips should get annotation.')

    subparser_reannotate.set_defaults(func=clusterfunk.subcommands.reannotate_tree.run)

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
            help='Space separated list of traits to extract from tips')

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
            help='The name of the annotation that will hold transitions.')
    subparser_label_transitions.add_argument(
            '--transition_suffix',
            type=str,
            help='suffix for each transition value'
    )
    subparser_label_transitions.add_argument(
            "-e",
            "--exploded_trees",
            dest='exploded_trees',
            action='store_true',
            default=False,
            help='A boolean flag to output a nexus for each transition. In this case the ouput argument is treated as a directory and made if it doesn\'t exist')

    subparser_label_transitions.add_argument(
            "--include_parent",
            dest='include_parent',
            action='store_true',
            default=False,
            help='A boolean flag to inlcude transition parent node in exploded trees')

    subparser_label_transitions.set_defaults(func=clusterfunk.subcommands.label_transitions.run)

    # _____________________________ prune ______________________________#

    subparser_prune = subparsers.add_parser(
            "prune",
            aliases=['prune_dat_tree'],
            usage="clusterfunk prune --extract [--fasta file.fas] [--taxon taxon.set.txt] [--metadata metadata.csv/tsv --index-column taxon] -i my.tree -o my.smaller.tree ",
            help="Prunes a tree either removing the specified taxa or keeping only those specified. "
                 "Taxa can be specified from a fasta file, text file or metadata file with the taxon label indicated",
            parents=[shared_arguments_parser]
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

    meta_data_options = subparser_prune.add_mutually_exclusive_group()

    meta_data_options.add_argument(
            "--index-column",
            dest="index",
            help="column of metadata that holds the taxon names"
    )
    meta_data_options.add_argument(
            "--trait-column",
            dest="traits",
            help="column of metadata that holds the discrete trait. A tree will be output in the output directory for each"
                 "value in this trait"
    )
    subparser_prune.add_argument(
            "--extract",
            action="store_true",
            dest="extract",
            default=False,
            help="Boolean flag to extract and return the subtree defined by the taxa"
    )

    subparser_prune.set_defaults(func=clusterfunk.subcommands.prune.run)

    # _____________________________ graft ______________________________#
    subparser_gaft = subparsers.add_parser(
            "graft",
            aliases=['graft_dat_tree'],
            usage="clusterfunk graft --scion [trees1.tree tree2.tree] -i my.guide.tree -o my.combined.tree ",
            help="This function grafts trees (scion) onto a guide tree (input). The scion tree is grafted onto"
                 "the guide tree at the MRCA of the tips shared between the two. Any shared tips originally in the guide tree"
                 "are then removed. All incoming trees must be in the same format [nexus,newick,ect.]",
            parents=[shared_arguments_parser]
    )

    subparser_gaft.add_argument(
            "--scion",
            required=True,
            nargs="+",
            help="The incoming trees that will be grafted onto the input tree"
    )

    subparser_gaft.add_argument(
            "--full_graft",
            action="store_true",
            default=False,
            help="A boolean flag to remove any remaining original tips from the guide tree that were not found in any"
                 "scion tree. i.e. all tips in the output tree come from the scions"
    )
    subparser_gaft.add_argument(
            "--annotate_scions",
            nargs="+",
            help="A list of annotation values to add to the scion trees in the same order the trees are listed."
    )
    subparser_gaft.add_argument(
            "--scion_annotation_name",
            type=str,
            default='scion_id',
            help="the annotation name to be used in annotation each scion. default: scion_id"
    )
    subparser_prune.set_defaults(func=clusterfunk.subcommands.graft.run)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
