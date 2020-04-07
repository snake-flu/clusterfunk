
def get_annotations(tree, traits):
    tip_annotations = []
    for tip in tree.leaf_node_iter():
        row = {}
        row["taxon"] = tip.taxon.label
        for a in traits:
            row[a] = tip.annotations.get_value(a)
        tip_annotations.append(row)
    return tip_annotations
