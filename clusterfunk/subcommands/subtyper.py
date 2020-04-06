import dendropy

from clusterfunk.subtyper import Subtyper, collapse_nodes


def run(options):
    tree = dendropy.Tree.get(path=options.input, schema="nexus", preserve_underscores=True)
    if options.collapse:
        collapse_nodes(tree, lambda x: x.edge.length == 0)

    subtyper = Subtyper(tree, options.index, options.separator)
    subtype = subtyper.get_subtype(options.taxon)

    with open(options.output, "w") as output_file:
        output_file.write("%s,%s" % (options.taxon, subtype))
