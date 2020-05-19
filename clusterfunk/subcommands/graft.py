from clusterfunk.graft import RootStock
from clusterfunk.utils import prepare_tree, write_tree, SafeNodeAnnotator

nodeAnnotator = SafeNodeAnnotator(safe=True)

def run(options):
    guide_tree = prepare_tree(options)
    root_stock = RootStock(guide_tree)

    i = 0
    for path in options.scions:
        scion_tree = prepare_tree(options, path)
        if options.annotate_scions is not None:
            annotate_nodes(scion_tree, options.scion_annotation_name, options.annotate_scions[i])
        try:
            root_stock.graft(scion_tree)
        except KeyError as e:
            raise Exception('No tips shared between guide tree and scion %s' % path).with_traceback(e.__traceback__)
        i += 1

    if options.full_graft:
        root_stock.remove_left_over_tips()

    write_tree(root_stock.tree, options)


def annotate_nodes(tree, trait_name, trait_value):
    for node in tree.postorder_node_iter():
        nodeAnnotator.annotate(node, trait_name, trait_value)
