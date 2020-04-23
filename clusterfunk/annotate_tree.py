import re
import warnings
from collections import Counter

from clusterfunk.utils import check_str_for_bool


def push_trait_to_tips(node, trait_name, value, predicate=lambda x: True):
    def action(n):
        if n.is_leaf():
            setattr(n, trait_name, value)
            n.annotations.add_bound_attribute(trait_name)

    traverse_and_annotate = TraversalAction(predicate, action)
    if predicate(node):
        traverse_and_annotate.run(node)


class TraversalAction:
    def __init__(self, predicate, action):
        self.predicate = predicate
        self.action = action

    def run(self, node):
        for child in node.child_node_iter():
            if self.predicate(child):
                self.action(child)
                self.run(child)


class TreeAnnotator:
    def __init__(self, tree, taxon_regex=re.compile("(.*)"), majority_rule=False):
        self.tree = tree
        self.root = tree.seed_node
        self.majority_rule = majority_rule
        self.taxon_regex = taxon_regex
        pass

    def taxon_parser(self, taxon_label):
        match = self.taxon_regex.match(taxon_label)
        if not match:
            raise ValueError("taxon name %s in tree file does not match regex pattern" % taxon_label)
        return "".join(match.groups())

    def annotate_tips_from_label(self, trait_name, regex):
        annotations = {}
        for tip in self.tree.leaf_node_iter():
            trait = {}
            value_match = regex.match(tip.taxon.label)
            if value_match is None:
                raise ValueError("taxon name %s in tree does not match annotation regex pattern" % tip.taxon.label)
            else:
                value = "".join(value_match.groups())
            trait[trait_name] = value if len(value) > 0 or value is None else None
            annotations[tip.taxon.label] = trait

        self.annotate_tips(annotations)

    def add_boolean_trait(self, trait, boolean_trait_name, regex):
        for node in self.tree.postorder_node_iter():
            self.add_boolean(node, trait, boolean_trait_name, regex)

    def annotate_tips(self, annotations):
        for tip_label in annotations:
            self.annotate_node(tip_label, annotations[tip_label])

    def add_boolean(self, node, trait, boolean_trait_name, regex):
        if node.annotations.get_value(trait) is not None:
            if regex.match(str(node.annotations.get_value(trait))):
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

        node = self.tree.find_node_with_taxon(
            lambda taxon: True if self.taxon_parser(taxon.label) == tip_label else False)
        if node is None:
            warnings.warn("Taxon: %s not found in tree" % tip_label, UserWarning)
        else:
            for a in annotations:
                if annotations[a] and (type(annotations[a]) is str and len(annotations[a]) > 0) or type(
                        annotations[a]) is not str:
                    setattr(node, a, check_str_for_bool(annotations[a]))
                    node.annotations.add_bound_attribute(a)

    def annotate_mrca(self, trait_name, value):
        taxon_set = [tip.taxon for tip in
                     self.tree.leaf_node_iter(lambda node: node.annotations.get_value(trait_name) == value)]
        mrca = self.tree.mrca(taxa=taxon_set)

        current_annotation = mrca.annotations.get_value("%s-mrca" % trait_name)
        if current_annotation is not None:
            print("common mrca concatenating %s and %s" % (current_annotation, value))
            setattr(mrca, "%s-mrca" % trait_name, current_annotation + "-" + value)
        else:
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


def get_annotations(annotation_list, index_column, data_name_matcher, traits):
    """
    :param annotation_list: list of dictionaries that hold annotatations
    :param index_column: the key in the dictionary used to identify the taxon
    :param data_name_matcher: regex to parse the entries in the index column into groups to match taxon name g
    :param traits: name of trait keys to annotate
    :return: a dictionary keyed by parsed index column entries. Entries are dictionaries with trait and value pairs
    """
    annotation_dict = {}
    for row in annotation_list:
        annotations = {}
        taxon_name_match = data_name_matcher.match(row[index_column])
        if not taxon_name_match:
            raise ValueError("taxon name %s in input file does not match regex pattern" % row[index_column])
        key_name = "".join(taxon_name_match.groups())
        for trait in traits:
            annotations[trait] = row[trait]
        annotation_dict[key_name] = annotations
    return annotation_dict
