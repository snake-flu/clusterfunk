import warnings
from collections import Counter

from clusterfunk.utils import check_str_for_bool


def push_trait_to_tips(node, trait_name, value, predicate=lambda x: True):
    def action(n):
        if n.is_leaf():
            setattr(n, trait_name, value)
            n.annotations.add_bound_attribute(trait_name)

    traverse_and_annotate = TraversalAction(predicate, action)
    traverse_and_annotate.run(node)


def traverse(node, predicate, action):
    for child in node.child_node_iter():
        if predicate(child):
            action(child)
            traverse(node, predicate, action)


class TraversalAction:
    def __init__(self, predicate, action):
        self.predicate = predicate
        self.action = action

    def run(self, node):
        for child in node.child_node_iter():
            if self.predicate(child):
                self.action(child)
                self.run(node)


class TreeAnnotator:
    def __init__(self, tree, majority_rule=False):
        self.tree = tree
        self.root = tree.seed_node
        self.majority_rule = majority_rule
        pass

    def annotate_tips_from_label(self, traitName, index, separator):
        annotations = {}
        for tip in self.tree.leaf_node_iter():
            trait = {}
            value = tip.taxon.label.split(separator)[index]
            trait[traitName] = value if len(value) > 0 else None
            annotations[tip.taxon.label] = trait

        self.annotate_tips(annotations)

    def add_boolean_trait(self, trait, value):
        for node in self.tree.postorder_node_iter():
            self.add_boolean(node, trait, value)

    def annotate_tips(self, annotations):
        for tip in annotations:
            self.annotate_node(tip, annotations[tip])

    def add_boolean(self, node, trait, value):
        boolean_trait_name = "%s_%s" % (trait, str(value))
        if node.annotations.get_value(trait) is not None:
            if node.annotations.get_value(trait) == value:
                setattr(node, boolean_trait_name, True)
            else:
                setattr(node, boolean_trait_name, False)
            node.annotations.add_bound_attribute(boolean_trait_name)

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
            warnings.warn("Taxon: %s not found in tree" % tip_label)
        else:
            for a in annotations:
                if a != "taxon":
                    setattr(node, a, check_str_for_bool(annotations[a]))
                    node.annotations.add_bound_attribute(a)

    def annotate_mrca(self, trait_name, value):
        taxon_set = [tip.taxon for tip in
                     self.tree.leaf_node_iter(lambda node: node.annotations.get_value(trait_name) == value)]
        mrca = self.tree.mrca(taxa=taxon_set)

        setattr(mrca, "%s-mrca" % trait_name, value)
        mrca.annotations.add_bound_attribute("%s-mrca" % trait_name)
        return mrca

    def fitch_parsimony(self, node, name):
        if len(node.child_nodes()) == 0:
            tip_annotation = node.annotations.get_value(name) if node.annotations.get_value(name) is not None else []
            return tip_annotation if isinstance(tip_annotation, list) else [tip_annotation]

        union = set()
        intersection = set()
        all_states = []

        i = 0
        for child in node.child_node_iter():
            child_states = self.fitch_parsimony(child, name)
            union = union.union(child_states)
            intersection = set(child_states) if i == 0 else intersection.intersection(child_states)
            all_states.extend(child_states)
            i += 1

        value = list(intersection) if len(intersection) > 0 else list(union)

        if self.majority_rule and len(intersection) == 0:
            if node.num_child_nodes() > 2:
                unique_states = list(union)
                state_counts = [0 for state in unique_states]
                for child_state in all_states:
                    state_counts[unique_states.index(child_state)] += 1
                cutoff = node.num_child_nodes() / 2
                majority = [state for state in unique_states if state_counts[unique_states.index(state)] > cutoff]
                value = majority if len(majority) > 0 else value
                setattr(node, "children_" + name, unique_states)
                setattr(node, "children_" + name + "_counts", state_counts)
                node.annotations.add_bound_attribute("children_" + name)
                node.annotations.add_bound_attribute("children_" + name + "_counts")

        setattr(node, name, value[0] if len(value) == 1 else value)

        node.annotations.add_bound_attribute(name)

        return value

    def reconstruct_ancestors(self, node, parent_states, acctran, name):
        node_states = node.annotations.get_value(name) if isinstance(node.annotations.get_value(name), list) else [
                node.annotations.get_value(name)]

        if node.is_leaf() and len(node_states) == 1 and node_states[0] is not None:
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
