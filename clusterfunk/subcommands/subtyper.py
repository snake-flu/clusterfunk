import dendropy

from clusterfunk.subtyper import Subtyper


def run(options):
    tree = dendropy.Tree.get(path=options.input, schema="nexus")
    subtyper = Subtyper(tree, options.index, options.separator)
    subtype = subtyper.get_subtype(options.taxon)

    with open(options.output, "w") as output_file:
        output_file.write("%s,%s" % (options.taxon, subtype))
