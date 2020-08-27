import argparse

import clusterfunk
import clusterfunk.subprocesses
from clusterfunk.Main import Main


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
            default=None,
            help='A optional flag to collapse branches with length <= the input before running the rule.')
    shared_required.add_argument(
            "--tree-list",
            dest="tree_list",
            action="store_true",
            default=False,
            help='Does the input file contain multiple trees')

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

    subparser_phylotype.set_defaults(subprocess=clusterfunk.subprocesses.phylotype.Phylotype)
    # _____________________________ tree annotator ______________________________#
    subparser_annotate = subparsers.add_parser(
            "annotate_tips",
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
    subparser_annotate.set_defaults(subprocess=clusterfunk.subprocesses.annotate_tips.TipAnnotator)
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
    subparser_relabel.add_argument(
            "--parse-taxon-key",
            dest="parse_taxon",
            metavar="<regex>",
            default="(.*)",
            help="regex defined group(s) to construct keys from the taxon labels to match the data file keys"
    )
    subparser_relabel.add_argument(
            "--from-label",
            dest="from_label",
            action="store_true",
            default=False,
            help="boolean flag to replace current label with regex groups and separator defined by parse-taxon key and separator"
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

    subparser_relabel.set_defaults(subprocess=clusterfunk.subprocesses.relabel_tips.TipLabeler)

    # _____________________________ Ancestral reconstruction ______________________________#

    subparser_ancestral_reconstruction = subparsers.add_parser(
            "ancestral_reconstruction",
            usage="clusterfunk ancestral_reconstruction --acctran/--deltran [--ancestral_state] [--majority_rule] "
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

    # reconstruction_options.add_argument(
    #         '--maxtran-with-value',
    #         dest='maxtran',
    #         metavar="<values>",
    #         nargs="+",
    #         help="use acctran except at polytomy if multiple children have <value> then the polytomy "
    #              "node is included. values are in the same order as traits")

    subparser_ancestral_reconstruction.add_argument(
            "--traits",
            nargs="+",
            help="the traits whose values will be reconstructed"
    )
    subparser_ancestral_reconstruction.add_argument(
            '--ancestral-state',
            dest='ancestral_state',
            action='store',
            nargs="+",
            help="Option to set the ancestral state for the tree. In same order of traits")
    subparser_ancestral_reconstruction.add_argument(
            '--majority-rule',
            dest="majority-rule",
            action='store_true',
            default=False,
            help="A Boolean flag. In first stage of the Fitch algorithm, at a polytomy, when there is no intersection of traits from all children"
                 "should the trait that appears most in the children"
                 "be assigned. Default:False - the union of traits are assigned"
    )

    subparser_ancestral_reconstruction.add_argument(
            '--polytomy-tie-break',
            dest="polytomy_tie_break",
            nargs="+",
            default=None,
            help="A list of trait values giving the precedence for what traits should be assigned at polytomies."
                 "Values not listed will be overlooked. Default behavior is to treat polytomies like a bifurcating node "
                 "and assign the union of child sets, when no iterestion exists. "
    )

    subparser_ancestral_reconstruction.set_defaults(
            subprocess=clusterfunk.subprocesses.ancestral_reconstruction.AncestorReconstructor)

    # _____________________________ push annotations to tips ______________________________#
    subparser_push_annotations_to_tips = subparsers.add_parser(
            "push_annotations_to_tips",
            usage="clusterfunk annotate_tips_from_nodes  --traits country -i my.tree -o my.annotated.tree ",
            help="This function pushes annotations to tips. It identifies the  mrca of nodes with each value of the trait"
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

    subparser_push_annotations_to_tips.set_defaults(
            subprocess=clusterfunk.subprocesses.push_annotations_to_tips.AnnotationPusher)

    # _____________________________ extract_tip_annotations ______________________________#
    subparser_extract_tip_annotations = subparsers.add_parser(
            "extract_tip_annotations",
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

    subparser_extract_tip_annotations.set_defaults(
            subprocess=clusterfunk.subprocesses.extract_tip_annotations.AnnotationExtractor)
    # _____________________________ get_taxa ______________________________#

    subparser_get_taxa = subparsers.add_parser(
            "get_taxa",
            usage="clusterfunk get_taxa  -i input.tree -o taxa.txt",
            help="extracts taxa labels from tips in a tree",
            parents=[shared_arguments_parser]

    )

    subparser_get_taxa.set_defaults(
            subprocess=clusterfunk.subprocesses.get_taxa.TaxaGetter)
    # _____________________________ return_basal ______________________________#

    subparser_return_basal = subparsers.add_parser(
            "return_basal",
            usage="clusterfunk return_basal  -i input.tree -o taxa.txt",
            help="returns a representative basal taxon",
            parents=[shared_arguments_parser]

    )

    subparser_return_basal.set_defaults(subprocess=clusterfunk.subprocesses.return_basal.BasalReturner)

    # _____________________________ label_transitions ______________________________#

    subparser_label_transitions = subparsers.add_parser(
            "label_transitions",
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

    subparser_label_transitions.add_argument(
            "--stubborn",
            dest='stubborn',
            action='store_true',
            default=False,
            help='A boolean flag that when used with --to will label all descendent re-entries of a transition as the parent')

    subparser_label_transitions.set_defaults(subprocess=clusterfunk.subprocesses.label_transitions.TranistionLabeler)

    # _____________________________ merge transitions ______________________________#
    subparser_merge_transitions = subparsers.add_parser(
            "merge_transitions",
            usage="clusterfunk merge_transitions --trait-to-merge --merged-trait-name --prefix --max-merges -i my.tree -o my.merged.tree ",
            help="Merges transitions that share a parent. Allows 1 merge on path to root by default. Merging is not nested. transitions that are not merged are still given a merged trait name",
            parents=[shared_arguments_parser]
    )

    subparser_merge_transitions.add_argument(
            "--trait-to-merge",
            dest="trait_to_merge",
            help="name of transition trait to merge"
    )

    subparser_merge_transitions.add_argument(
            "--merged-trait-name",
            dest="merged_trait_name",
            help="name of merged trait -output"
    )
    subparser_merge_transitions.add_argument(
            "--prefix",
            dest="prefix",
            default="",
            help="output annotation value prefix, default is \'\'"
    )
    rubric = subparser_merge_transitions.add_mutually_exclusive_group(required=True)
    rubric.add_argument(
            "--max-merge",
            dest="max_merge",
            default=0,
            type=int,
            help="The number of merges allowed on the path to the root from each merger"
    )
    rubric.add_argument(
            "--merge-sibling-singletons",
            dest="merge_sibling_singletons",
            default=False,
            action="store_true",
            help="Boolean flag to merge sibling singleton tips."
    )
    rubric.add_argument(
            "--merge-siblings",
            dest="merge_siblings",
            default=False,
            action="store_true",
            help="Boolean flag to merge sibling transitions"
    )
    subparser_merge_transitions.set_defaults(subprocess=clusterfunk.subprocesses.merge_transitions.MergeTransitions)

    # _____________________________ prune ______________________________#

    subparser_prune = subparsers.add_parser(
            "prune",
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
    subparser_prune.add_argument(
            "--threshold",
            dest="threshold",
            default=2,
            type=int,
            help="If using 'trait' each subtree must have at least this many tips. Default 2."
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

    subparser_prune.set_defaults(subprocess=clusterfunk.subprocesses.prune.PruneProcess)

    # ------------------------------reformat-----------------------------#
    subparser_reformat = subparsers.add_parser(
            "reformat",
            usage="clusterfunk reformat -i my.guide.tree -o my.combined.tree --in-format nexus --out-format newick",
            help="This function reformats a tree file",
            parents=[shared_arguments_parser]
    )
    subparser_reformat.set_defaults(subprocess=clusterfunk.subprocesses.reformat.Reformat)

    # _____________________________ graft ______________________________#
    subparser_gaft = subparsers.add_parser(
            "graft",
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
            "--annotate-scions",
            nargs="+",
            help="A list of annotation values to add to the scion trees in the same order the trees are listed."
    )
    subparser_gaft.add_argument(
            "--scion-annotation-name",
            type=str,
            default='scion_id',
            help="the annotation name to be used in annotation each scion. default: scion_id"
    )
    subparser_gaft.set_defaults(subprocess=clusterfunk.subprocesses.graft.Grafter)

    # ------------------------------sort-----------------------------#
    subparser_sort = subparsers.add_parser(
            "sort",
            usage="clusterfunk sort -i my.tree -o my.sorted.tree --in-format nexus --out-format newick",
            help="This function sorts a tree at each internal node by increasing number of subtended tips",
            parents=[shared_arguments_parser]
    )
    subparser_sort.set_defaults(subprocess=clusterfunk.subprocesses.sort.Sorter)

    # ------------------------------root-----------------------------#
    subparser_root = subparsers.add_parser(
            "root",
            usage="clusterfunk root -i my.tree -o my.rooted.tree --outgroup my_outgroup_taxon --in-format nexus --out-format newick",
            help="reroot the tree such that a particular node is moved to the outgroup position",
            parents=[shared_arguments_parser]
    )
    subparser_root.add_argument(
            "--outgroup",
            type=str,
            help="the name of the taxon to move to an outgroup position")

    # subparser_root.add_argument(
    #         "--unroot",
    #         action="store_true",
    #         default=False,
    #         help="Unroot a rooted tree. Push the root to a polytomy."
    #         )
    subparser_root.set_defaults(subprocess=clusterfunk.subprocesses.root.Rooter)

    # ------------------------------focus-----------------------------#
    subparser_focus = subparsers.add_parser(
            "focus",
            usage="clusterfunk focus -i my.tree -o smaller.tree [--tsv_file <output.tsv>] [<taxon "
                  "parsing options>] ",
            help="This function takes in a tree and protected taxon list. It traverses to the tree and collapses "
                 "any clades that do not contain a protected taxon"
                 "removed nodes. Taxon defined in the list are not removed. There is an option to output a tsv "
                 "including a list of all the removed nodes ",
            parents=[shared_arguments_parser]
    )

    subparser_focus.add_argument(
            "--output-tsv",
            dest="tsv_file",
            help="output tsv file with nodes that map to each inserted node."
    )

    subparser_focus.add_argument(
            "--threshold",
            dest="collapse_threshold",
            default=1,
            type=int,
            help="collapse clades that do not include the protected taxa and have more than this number of tips. Default 1."
    )
    taxon_set_files = subparser_focus.add_mutually_exclusive_group(required=True)

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

    meta_data_options = subparser_focus.add_argument_group("metadata options")

    meta_data_options.add_argument(
            "--index-column",
            dest="index_column",
            help="column of metadata that holds the taxon names"
    )
    subparser_focus.add_argument(
            "--parse-data-key",
            dest="data_taxon_pattern",
            metavar="<regex>",
            default="(.*)",
            help="regex defined group(s) to construct keys from the data file to match the taxon labels"
    )
    subparser_focus.set_defaults(
            subprocess=clusterfunk.subprocesses.treeFocuser.TreeFocuser)

    # ------------------------------find catchments-----------------------------#
    subparser_find_catchments = subparsers.add_parser(
            "find_catchments",
            usage="clusterfunk find_catchments -i my.tree -o directory/with/ouput/trees ",
            help="This function takes in a tree and a taxon list. It searches the neighborhood of these taxa and "
                 "return subtrees containing all tips within a set threshold. Overlapping catchments are merged.",
            parents=[shared_arguments_parser]
    )

    subparser_find_catchments.add_argument(
            "--threshold",
            type=float,
            help="The patristic distance threshold that defines a catchment"
    )
    subparser_find_catchments.add_argument(
            "--include-terminal-branch",
            dest="include_terminal_branch",
            action="store_true",
            default=False,
            help="Boolean flag stating the terminal branchlengths should be included in the distances. Defualt is "
                 "False, only distances along internal branches count. "
    )
    subparser_find_catchments.add_argument(
            "--branch-count",
            dest="branch_count",
            action="store_true",
            default=False,
            help="Boolean flag stating that the threshold refers to the number of branches traversed not their length. "
    )
    taxon_set_files = subparser_find_catchments.add_mutually_exclusive_group(required=True)

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

    meta_data_options = subparser_find_catchments.add_argument_group("metadata options")

    meta_data_options.add_argument(
            "--index-column",
            dest="index_column",
            help="column of metadata that holds the taxon names"
    )
    subparser_find_catchments.add_argument(
            "--parse-data-key",
            dest="data_taxon_pattern",
            metavar="<regex>",
            default="(.*)",
            help="regex defined group(s) to construct keys from the data file to match the taxon labels"
    )
    subparser_find_catchments.add_argument(
            "--parse-taxon-key",
            dest="parse_taxon",
            metavar="<regex>",
            default="(.*)",
            help="regex defined group(s) to construct keys from the taxon labels to match the data file keys"
    )

    subparser_find_catchments.add_argument(
            "-t", "--threads",
            dest="threads",
            type=int,
            default=1,
            help="Number of threads to parallelize over"
    )

    subparser_find_catchments.set_defaults(
            subprocess=clusterfunk.subprocesses.patristicNeighbourhoodFinder.PatristicNeighbourhoodFinder)

    # # _____________________________ get height kde ______________________________#
    # subparser_get_height_kde = subparsers.add_parser(
    #         "get_height_kde",
    #         usage="clusterfunk get_height_kde --trees all_the_trees -i my.target.tree -o my.combined.tree",
    #         help="This function reformats a tree file",
    #         parents=[shared_arguments_parser]
    # )
    # subparser_get_height_kde.add_argument(
    #         "--trees",
    #         nargs="+",
    #         help="file containing the trees used to get height kde"
    # )
    # subparser_get_height_kde.add_argument(
    #         "--threshold",
    #         type=float,
    #         default=0.5,
    #         help="file containing the trees used to get height kde"
    # )
    # subparser_get_height_kde.set_defaults(func=clusterfunk.subprocesses.annotate_target_tree.run)

    # # ------------------------------reformat-----------------------------#
    # subparser_annotate_lineages = subparsers.add_parser(
    #         "annotate_lineages",
    #         usage="clusterfunk reformat -i my.guide.tree -o my.combined.tree --trait=lineage",
    #         help="This function reformats a tree file",
    #         parents=[shared_arguments_parser]
    # )
    # subparser_annotate_lineages.add_argument(
    #         "--trait",
    #         type=str,
    #         default='lineage',
    #         help="the annotation name to reconstruct"
    # )
    # subparser_annotate_lineages.set_defaults(func=clusterfunk.subprocesses.annotate_lineages.run)

    args = parser.parse_args()

    if hasattr(args, "subprocess"):
        subprocess = args.subprocess(args)

        del args.subprocess

        Main(args, subprocess)
        # args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
