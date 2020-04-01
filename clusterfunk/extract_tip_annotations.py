class AnnotationExtractor:
    def __init__(self, tree):
        self.tree = tree
        pass

    def get_annotations(self, traits):
        tip_annotations = []
        for tip in self.tree.leaf_node_iter():
            row = {}
            row["taxon"] = tip.taxon.label
            for a in traits:
                row[a] = tip.annotations.get_value(a)
            tip_annotations.append(row)
        return tip_annotations
