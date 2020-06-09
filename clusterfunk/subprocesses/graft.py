from clusterfunk.subProcess import SubProcess
from clusterfunk.utilities.rootStock import RootStock
from clusterfunk.utilities.utils import prepare_tree, safeNodeAnnotator


class Grafter(SubProcess):
    def __init__(self, options):
        super().__init__(options)

    def run(self, guide_tree):
        root_stock = RootStock(guide_tree)

        i = 0
        for path in self.options.scions:
            scion_tree = prepare_tree(self.options, path)
            if self.options.annotate_scions is not None:
                self.annotate_nodes(scion_tree, self.options.scion_annotation_name, self.options.annotate_scions[i])
            try:
                root_stock.graft(scion_tree)
            except KeyError as e:
                raise Exception('No tips shared between guide tree and scion %s' % path).with_traceback(e.__traceback__)
            i += 1

        if self.options.full_graft:
            root_stock.remove_left_over_tips()

    def annotate_nodes(self, tree, trait_name, trait_value):
        for node in tree.postorder_node_iter():
            safeNodeAnnotator.annotate(node, trait_name, trait_value)
