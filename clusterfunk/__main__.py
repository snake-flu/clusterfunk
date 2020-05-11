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
            '--in-format',
            dest='in_format',
            action='store',
            default="nexus",
            choices=['nexus', 'newick', 'nexml'],
            help='what format is the tree file. This is passed to dendropy. default is \'nexus\'')

    shared_arguments_parser.add_argument(
            '--out-format',
            dest='out_format',
            action='store',
            default="nexus",
            choices=['nexus', 'newick', 'nexml'],
            help='what format is the tree file. This is passed to dendropy. default is \'nexus\'. Note newick trees '
                 ' can not contain annotations')

    shared_arguments_parser.add_argument(
            "-c",
            "--collapse_to_polytomies",
            dest='collapse',
            type=float,
            help='A optional flag to collapse branches with length <= the input before running the rule.')
    shared_arguments_parser.add_argument(
            "-v",
            "--verbose",
            dest="verbose",
            action='store_true',
            default=False)

    subparsers = parser.add_subparsers(
            title="Available subcommands", help="", metavar=""
    )

    # _____________________________ phylotype ______________________________#
    subparser_phylotype = subparsers.add_parser(
            "phylotype",
            aliases=['phylotype_dat_tree'],
            usage="clusterfunk phylotype [--threshold] [---prefix] --inputmy.tree --output my.phylotyped.tree",
            help="Assigns phylotypes to a tree based on a branch length threshold",
            parents=[shared_arguments_parser]
    )

    subparser_phylotype.add_argument(
            '--threshold',
            dest='threshold',
            action='store',
            default=5E-6,
            type=float,
            help='branch threshold used to distinguish new phylotype (default: 5E-6)')

    subparser_phylotype.add_argument(
            '--prefix',
            default="p",
            type=str,
            help='prefix for each phylotype. (default:p)'
    )

    subparser_phylotype.set_defaults(func=clusterfunk.subcommands.phylotype.run)
    # _____________________________ tree annotator ______________________________#
    subparser_annotate = subparsers.add_parser(
            "annotate_tips",
            aliases=['annotate_dat_tips'],
            usage="clusterfunk annotate  --input my.tree --output my.annotated.tree ",
            help="Annotates the tips of tree. Can annotate tips from a csv/tsv and/or taxon labels",
            parents=[shared_arguments_parser]
    )

    subparser_annotate.add_argument(
            '--boolean-for-trait',
            dest="boolean_for_trait",
            metavar="<trait>_<qualifier>=<regex>",
            nargs="+",
            help=" A boolean annotation will be added for each node "
                 "with the new trait specifying whether the annotation <trait> not it matches this value.")

    subparser_annotate.add_argument(
            '--boolean-trait-names',
            dest="boolean_trait_names",
            metavar="<trait_name>",
            nargs="+",
            help=" A names of the boolean annotations added by boolean-for-trait option in order.")

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
            "--from-taxon",
            nargs="+",
            dest="from_taxon",
            metavar="<trait>=<regex>",
            help="Space separated list of regex group(s) parsing trait values from taxon label"
    )

    from_meta_data.add_argument(
            '--in-metadata',
            dest='traits_file',
            action='store',
            type=str,
            help='optional csv file with tip annotations')
    from_meta_data.add_argument(
            "--trait-columns",
            dest="trait_columns",
            type=str,
            nargs="+",
            help='Space separated list of columns to annotate on tree')

    from_meta_data.add_argument(
            '--index-column',
            dest="index_column",
            default="taxon",
            help="What column in the csv should be used to match the tip names."
    )

    from_meta_data.add_argument(
            "--parse-data-key",
            dest="parse_data",
            metavar="<regex>",
            default="(.*)",
            help="regex defined group(s) to construct keys from the data file to match the taxon labels"
    )
    from_meta_data.add_argument(
            "--parse-taxon-key",
            dest="parse_taxon",
            metavar="<regex>",
            default="(.*)",
            help="regex defined group(s) to construct keys from the taxon labels to match the data file keys"
    )
    subparser_annotate.set_defaults(func=clusterfunk.subcommands.annotate_tips.run)
    # _____________________________ rename tips ______________________________#
    subparser_relabel = subparsers.add_parser(
            "relabel_tips",
            usage="clusterfunk relabel_tips  --input my.tree --output my.annotated.tree ",
            help="relabels the tips of tree. Can relable tips from a csv/tsv and/or annotations labels",
            parents=[shared_arguments_parser]
    )

    subparser_relabel.add_argument(
            "--separator",
            type=str,
            default="|",
            help="separate feilds in name"
    )

    subparser_relabel.add_argument(
            "--replace",
            action="store_true",
            default=False,
            help="replace tip label instead of appending to it, default is False"
    )

    from_annotations_group = subparser_relabel.add_argument_group("Renaming with annotations")
    from_metadata = subparser_relabel.add_argument_group("Renaming from metadata file")

    from_annotations_group.add_argument(
            "--from-traits",
            nargs="+",
            dest="from_traits",
            metavar="<[traits]>",
            help="Space separated list of traits."
    )

    from_metadata.add_argument(
            '--in-metadata',
            dest='traits_file',
            action='store',
            type=str,
            help='optional csv file with tip annotations')
    from_metadata.add_argument(
            "--trait-columns",
            dest="trait_columns",
            type=str,
            nargs="+",
            help='Space separated list of columns to annotate on tree')

    from_metadata.add_argument(
            '--index-column',
            dest="index_column",
            default="taxon",
            help="What column in the csv should be used to match the tip names."
    )

    from_metadata.add_argument(
            "--parse-data-key",
            dest="parse_data",
            metavar="<regex>",
            default="(.*)",
            help="regex defined group(s) to construct keys from the data file to match the taxon labels"
    )
    from_metadata.add_argument(
            "--parse-taxon-key",
            dest="parse_taxon",
            metavar="<regex>",
            default="(.*)",
            help="regex defined group(s) to construct keys from the taxon labels to match the data file keys"
    )
    subparser_relabel.set_defaults(func=clusterfunk.subcommands.relabel_tips.run)

    # _____________________________ Ancestral reconstruction ______________________________#

    subparser_ancestral_reconstruction = subparsers.add_parser(
            "ancestral_reconstruction",
            usage="clusterfunk ancestral_reconstruction --acctran/--deltran/--maxtran [--ancestral_state] [--majority_rule] "
                  "--traits country -i my.tree -o my.annotated.tree ",
            help="Reconstructs ancestral states on internal nodes using Fitch parsimony algorithm",
            parents=[shared_arguments_parser]
    )

    reconstruction_options = subparser_ancestral_reconstruction.add_mutually_exclusive_group()

    reconstruction_options.add_argument(
            '-acc',
            '--acctran',
            dest='acctran',
            action='store_true',
            help="Boolean flag to use acctran reconstruction")

    reconstruction_options.add_argument(
            '-del',
            '--deltran',
            dest='deltran',
            action='store_true',
            help="Boolean flag to use deltran reconstruction")

    reconstruction_options.add_argument(
            '--maxtran-with-value',
            dest='maxtran',
            metavar="<values>",
            nargs="+",
            help="use acctran except at polytomy if multiple children have <value> then the polytomy "
                 "node is included. values are in the same order as traits")

    subparser_ancestral_reconstruction.add_argument(
            "--traits",
            nargs="+",
            help="the traits whose values will be reconstructed"
    )
    subparser_ancestral_reconstruction.add_argument(
            '--ancestral_state',
            metavar='ancestral_state',
            action='store',
            nargs="+",
            help="Option to set the ancestral state for the tree. In same order of traits")
    subparser_ancestral_reconstruction.add_argument(
            '--majority_rule',
            action='store_true',
            default=False,
            help="A Boolean flag. In first stage of the Fitch algorithm, at a polytomy, when there is no intersection of traits from all children"
                 "should the trait that appears most in the children"
                 "be assigned. Default:False - the union of traits are assigned"
    )
    subparser_ancestral_reconstruction.set_defaults(func=clusterfunk.subcommands.ancestral_reconstruction.run)

    # _____________________________ push annotations to tips ______________________________#
    subparser_push_annotations_to_tips = subparsers.add_parser(
            "push_annotations_to_tips",
            usage="clusterfunk annotate_tips_from_nodes  --traits country -i my.tree -o my.annotated.tree ",
            help="This funk pushes annotations to tips. It identifies the  mrca of nodes with each value of the trait"
                 " provided and pushes the annotation up to any descendent tip",
            parents=[shared_arguments_parser]
    )

    subparser_push_annotations_to_tips.add_argument(
            "-t",
            "--traits",
            metavar='traits',
            required=True,
            type=str,
            nargs="+",
            help='Space separated list of discrete traits to annotate on tree')

    subparser_push_annotations_to_tips.add_argument(
            '--stop-where-trait',
            dest='stop_where_trait',
            metavar="<trait>=<regex>",
            type=str,
            help='optional filter for when to stop pushing annotation forward in preorder traversal from mrca.')

    subparser_push_annotations_to_tips.set_defaults(func=clusterfunk.subcommands.push_annotations_to_tips.run)

    # _____________________________ extract_tip_annotations ______________________________#
    subparser_extract_tip_annotations = subparsers.add_parser(
            "extract_tip_annotations",
            aliases=['extract_dat_tree'],
            usage="clusterfunk extract_annotations --traits country -i my.annotated.tree -o annotations.csv",
            help="extracts annotations from tips in a tree and ouputs a csv",
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
            help="counts and labels transitions of traits on a tree",
            parents=[shared_arguments_parser]

    )

    subparser_label_transitions.add_argument(
            "--trait",
            metavar='trait',
            type=str,
            required=True,
            help=' Trait whose transitions are being put on tree')

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
            "--transition-name",
            dest='transition_name',
            type=str,
            required=True,
            help='The name of the annotation that will hold transitions.')
    subparser_label_transitions.add_argument(
            '--transition-prefix',
            type=str,
            help='prefix for each transition value'
    )


    subparser_label_transitions.add_argument(
            "-e",
            "--exploded_trees",
            dest='exploded_trees',
            action='store_true',
            default=False,
            help='A boolean flag to output a nexus for each transition. In this case the ouput argument is treated as '
                 'a directory and made if it doesn\'t exist')

    subparser_label_transitions.add_argument(
            "--include_parent",
            dest='include_parent',
            action='store_true',
            default=False,
            help='A boolean flag to include transition parent node in exploded trees')

    subparser_label_transitions.add_argument(
            "--include_root",
            dest='include_root',
            action='store_true',
            default=False,
            help='A boolean flag that when used with --to will count the root node as the first transition if it is '
                 'annotated with the --to value')

    subparser_label_transitions.set_defaults(func=clusterfunk.subcommands.label_transitions.run)

    # _____________________________ prune ______________________________#

    subparser_prune = subparsers.add_parser(
            "prune",
            aliases=['prune_dat_tree'],
            usage="clusterfunk prune --extract [--fasta file.fas] [--taxon taxon.set.txt] [--metadata metadata.csv/tsv --index-column taxon] [--where-trait <trait>=<regex> ] -i my.tree -o my.smaller.tree ",
            help="Prunes a tree either removing the specified taxa or keeping only those specified. "
                 "Taxa can be specified from a fasta file, text file, metadata file, or by an annotation.",
            parents=[shared_arguments_parser]
    )
    taxon_set_master = subparser_prune.add_argument_group("Defining the taxon set")
    taxon_set_files = taxon_set_master.add_mutually_exclusive_group(required=True)

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
    taxon_set_files.add_argument(
            "--trait",
            dest="trait",
            help="A discrete trait. The tree will be pruned the tree for each value of the trait. In this case the"
                 " output will be interpreted as a directory."
    )

    taxon_set_files.add_argument(
            "--where-trait",
            nargs="+",
            dest="where_trait",
            metavar="<trait>=<regex>",
            help="Taxa defined by annotation value"
    )

    meta_data_options = subparser_prune.add_argument_group("metadata options")

    meta_data_options.add_argument(
            "--index-column",
            dest="index_column",
            help="column of metadata that holds the taxon names"
    )
    subparser_prune.add_argument(
            "--parse-data-key",
            dest="parse_data",
            metavar="<regex>",
            default="(.*)",
            help="regex defined group(s) to construct keys from the data file to match the taxon labels"
    )
    subparser_prune.add_argument(
            "--parse-taxon-key",
            dest="parse_taxon",
            metavar="<regex>",
            default="(.*)",
            help="regex defined group(s) to construct keys from the taxon labels to match the data file keys"
    )

    subparser_prune.add_argument(
            "--extract",
            action="store_true",
            dest="extract",
            default=False,
            help="Boolean flag to extract and return the subtree defined by the taxa"
    )

    subparser_prune.add_argument(
            "-t", "--threads",
            dest="threads",
            type=int,
            default=1,
            help="Number of threads to parallelize over"
    )

    subparser_prune.set_defaults(func=clusterfunk.subcommands.prune.run)

    # ------------------------------reformat-----------------------------#
    subparser_reformat = subparsers.add_parser(
            "reformat",
            usage="clusterfunk reformat -i my.guide.tree -o my.combined.tree --in-format nexus --out-format newick",
            help="This function reformats a tree file",
            parents=[shared_arguments_parser]
    )
    subparser_reformat.set_defaults(func=clusterfunk.subcommands.reformat.run)

    # _____________________________ graft ______________________________#
    subparser_gaft = subparsers.add_parser(
            "graft",
            aliases=['graft_dat_tree'],
            usage="clusterfunk graft --scion [trees1.tree tree2.tree] -i my.guide.tree -o my.combined.tree ",
            help="This function grafts trees (scions) onto a guide tree (input). The scion tree is grafted onto "
                 "the guide tree at the MRCA of the tips shared between the two. Any shared tips originally in the guide tree "
                 "are then removed. All incoming trees must be in the same format [nexus,newick,ect.]",
            parents=[shared_arguments_parser]
    )

    subparser_gaft.add_argument(
            "--scions",
            required=True,
            nargs="+",
            help="The incoming trees that will be grafted onto the input tree"
    )

    subparser_gaft.add_argument(
            "--full-graft",
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
    subparser_gaft.set_defaults(func=clusterfunk.subcommands.graft.run)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
