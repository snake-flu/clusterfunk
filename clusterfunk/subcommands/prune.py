import copy
import os
from clusterfunk.prune import parse_taxon_set, prune_tree, parse_taxon_sets_by_trait
from clusterfunk.utils import prepare_tree


def run(options):
    tree = prepare_tree(options, options.input)
    taxa = []
    if options.fasta is not None:
        taxa = parse_taxon_set(options.fasta, "fasta")

    elif options.taxon is not None:
        taxa = parse_taxon_set(options.taxon, "txt")
    elif options.metadata is not None:
        if options.index is not None:
            taxa = parse_taxon_set(options.metadata, "metadata", index_column=options.index)

    if len(taxa) == 0:
        print("No taxa found in input files")
        return
    if not options.metadata or options.traits is None:
        prune_tree(tree, taxa, options.extract)
        tree.write(path=options.output, schema=options.format)
    else:
        if not os.path.exists(options.output):
            os.makedirs(options.output)
        taxa = parse_taxon_sets_by_trait(options.metadata, tree, options.traits)
        for taxon_set in taxa:
            tree_copy = copy.deepcopy(tree)
            prune_tree(tree_copy, taxon_set["tip_labels"], options.extract)
            tree.write(path=options.output + "/" + options.traits + "_" + taxa["value"], schema=options.format)
