from collections import Counter

from clusterfunk.utils import check_str_for_bool


class TreeAnnotator:
    def __init__(self, tree):
        self.tree = tree
        self.root = tree.seed_node
        pass

    def annotate_tips_from_label(self, traitName, index, separator):
        annotations = {}
        for tip in self.tree.leaf_node_iter():
            trait = {}
            value = tip.taxon.label.split(separator)[index]
            trait[traitName] = value if len(value)>0 else None
            annotations[tip.taxon.label] = trait

        self.annotate_tips(annotations)

    def annotate_tips(self, annotations):
        for tip in annotations:
            self.annotate_node(tip, annotations[tip])

    def annotate_nodes_from_tips(self, name, acctran, parent_state=None):
        if parent_state is None:
            parent_state = []
        self.fitch_parsimony(self.root, name)

        if parent_state is None:
            self.reconstruct_ancestors(self.root, [], acctran, name)
        else:
            self.reconstruct_ancestors(self.root, [parent_state], acctran, name)

    def annotate_node(self, tip_label, annotations):
        node = self.tree.find_node_with_taxon(lambda taxon: True if taxon.label == tip_label else False)
        if node is None:
            raise KeyError("Taxon %s not found in tree" % tip_label)
        for a in annotations:
            if a != "taxon":
                setattr(node, a, check_str_for_bool(annotations[a]))
                node.annotations.add_bound_attribute(a)

    def fitch_parsimony(self, node, name):
        if len(node.child_nodes()) == 0:
            tip_annotation = node.annotations.get_value(name) if node.annotations.get_value(name) is not None else []
            return tip_annotation if isinstance(tip_annotation, list) else [tip_annotation]

        union = set()
        intersection = set()

        i = 0
        for child in node.child_node_iter():
            child_states = self.fitch_parsimony(child, name)
            union = union.union(child_states)
            intersection = set(child_states) if i == 0 else intersection.intersection(child_states)
            i += 1

        value = list(intersection) if len(intersection) > 0 else list(union)
        setattr(node, name, value[0] if len(value) == 1 else value)

        node.annotations.add_bound_attribute(name)

        return value

    def reconstruct_ancestors(self, node, parent_states, acctran, name):
        node_states = node.annotations.get_value(name) if isinstance(node.annotations.get_value(name), list) else [
            node.annotations.get_value(name)]

        if node.taxon is not None and len(node_states) == 1 and node_states[0] is not None:
            assigned_states = node_states
        else:
            assigned_states = list(set(node_states).intersection(parent_states)) if len(
                set(node_states).intersection(parent_states)) > 0 else list(set(node_states).union(parent_states))

        if len(assigned_states) > 1:
            if acctran:
                assigned_states = [state for state in assigned_states if state not in parent_states]
            else:
                # can we delay
                child_states = []
                for child in node.child_node_iter():
                    child_states += child.annotations.get_value(name) if isinstance(child.annotations.get_value(name),
                                                                                    list) else [
                        child.annotations.get_value(name)]

                assigned_states = [state for state in assigned_states if
                                   state in parent_states and state in child_states] if len(
                    set(parent_states).intersection(child_states)) > 0 else [state for state in assigned_states if
                                                                             state in child_states]

        setattr(node, name, assigned_states[0] if len(assigned_states) == 1 else assigned_states)

        for child in node.child_node_iter():
            self.reconstruct_ancestors(child, assigned_states, acctran, name)


def get_annotations(taxon_key, annotation_list):
    annotation_dict = {}
    for row in annotation_list:
        annotation_dict[row[taxon_key]] = row
    return annotation_dict
