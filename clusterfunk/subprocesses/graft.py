from clusterfunk.subProcess import SubProcess
from clusterfunk.utilities.rootStock import RootStock
from clusterfunk.utilities.utils import prepare_tree, safeNodeAnnotator


class Grafter(SubProcess):
    def __init__(self, options):
        super().__init__(options)

    def run(self, guide_tree):
        root_stock = RootStock(guide_tree)

        i = 0
        if self.options.annotate_scions is not None:
            # Handle inputs which are not quite the right format, and sort scions by annotate_scions list
            for j in range(len(self.options.annotate_scions)):
                if self.options.annotate_scions[j].startswith('['):
                    self.options.annotate_scions[j] = self.options.annotate_scions[j][1:]
                if self.options.annotate_scions[j].endswith(','):
                    self.options.annotate_scions[j] = self.options.annotate_scions[j][:-1]
                if self.options.annotate_scions[j].endswith(']'):
                    self.options.annotate_scions[j] = self.options.annotate_scions[j][:-1]
            annotate_scions = self.options.annotate_scions.copy()
            annotate_scions.reverse()
            scions = self.options.scions.copy()
            ordered_scions = []
            for scion in annotate_scions:
                for path in scions:
                    if path.startswith(scion):
                        ordered_scions.append(path)
                        scions.remove(path)
                        break
            ordered_scions.reverse()
            ordered_scions.extend(scions)
            self.options.scions = ordered_scions    

        for path in self.options.scions:
            print("Add scion %s" %path)
            scion_tree = prepare_tree(self.options, path)
            if self.options.annotate_scions is not None:
                print("Annotate nodes of scion_tree",self.options.scion_annotation_name, self.options.annotate_scions[i])
                self.annotate_nodes(scion_tree, self.options.scion_annotation_name, self.options.annotate_scions[i])
            try:
                print("Graft scion")
                root_stock.graft(scion_tree)
            except KeyError as e:
                raise Exception('No tips shared between guide tree and scion %s' % path).with_traceback(e.__traceback__)
            i += 1

        if self.options.full_graft:
            print("Remove left over tips")
            root_stock.remove_left_over_tips()

    def annotate_nodes(self, tree, trait_name, trait_value):
        for node in tree.postorder_node_iter():
            safeNodeAnnotator.annotate(node, trait_name, trait_value)
