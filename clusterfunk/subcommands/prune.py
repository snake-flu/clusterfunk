from clusterfunk.prune import parse_taxon_set, prune_tree
from clusterfunk.utils import prepare_tree


def run(options):
    tree = prepare_tree(options)
    taxa = []
    if options.fasta is not None:
        taxa = parse_taxon_set(options.fasta, "fasta")

    elif options.taxon is not None:
        taxa = parse_taxon_set(options.taxon, "txt")
    elif options.metadata is not None:
        taxa = parse_taxon_set(options.metadata, "metadat", options.index)

    if len(taxa) == 0:
        print("No taxa found in input files")
        return

    tree = prune_tree(tree, taxa, options.extract)

    tree.write(options.output, schema=options.format)
