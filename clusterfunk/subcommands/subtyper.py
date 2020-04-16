import dendropy

from clusterfunk.utils import prepare_tree
from clusterfunk.subtyper import Subtyper


def run(options):
    tree = prepare_tree(options, options.input)
    subtyper = Subtyper(tree, options.index, options.separator)
    subtype = subtyper.get_subtype(options.taxon)

    with open(options.output, "w") as output_file:
        output_file.write("%s,%s" % (options.taxon, subtype))
