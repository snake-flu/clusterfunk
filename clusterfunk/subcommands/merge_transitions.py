from clusterfunk.trait_merger import Merger
from clusterfunk.utils import prepare_tree, write_tree


def run(options):
    tree = prepare_tree(options, options.input)
    merger = Merger(options.trait_to_merge, options.merged_trait_name, options.prefix, options.max_merge)
    merger.merge(tree)
    write_tree(tree, options)


