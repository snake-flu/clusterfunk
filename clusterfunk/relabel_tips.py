import re
import warnings


class TipLabeler:
    def __init__(self, tree, taxon_regex=re.compile("(.*)"), separator="|", replace=False):
        self.tree = tree
        self.taxon_regex = taxon_regex
        self.separator = separator
        self.replace = replace
        pass

    def taxon_parser(self, taxon_label):
        match = self.taxon_regex.match(taxon_label)
        if not match:
            raise ValueError("taxon name %s in tree file does not match regex pattern" % taxon_label)
        return "".join(match.groups())

    def relabel_tips_from_traits(self, traitNames):
        annotations = {}
        for tip in self.tree.leaf_node_iter():
            annotations[tip.taxon.label] = [
                    tip.annotations.get_value(trait) if tip.annotations.get_value(trait) is not None else "" for trait
                    in traitNames]

        self.relabel_tips(annotations)

    def relabel_tips(self, annotations):
        for tip_label in annotations:
            self.relabel_tip(tip_label, annotations[tip_label])

    def relabel_tip(self, tip_label, annotations):

        node = self.tree.find_node_with_taxon(
                lambda taxon: True if self.taxon_parser(taxon.label) == tip_label else False)
        if node is None:
            warnings.warn("Taxon: %s not found in tree" % tip_label, UserWarning)
        else:
            new_label = self.separator.join([str(x) for x in annotations]) if self.replace else self.separator.join(
                    [str(x) for x in [node.taxon.label] + annotations])
            node.taxon.label = new_label


# TODO add this to class and make metadata parser class

def get_traits_from_metadata(annotation_list, index_column, data_name_matcher, traits):
    """
    :param annotation_list: list of dictionaries that hold annotatations
    :param index_column: the key in the dictionary used to identify the taxon
    :param data_name_matcher: regex to parse the entries in the index column into groups to match taxon name g
    :param traits: name of trait keys to annotate
    :return: a dictionary keyed by parsed index column entries with a list of value names
    """
    annotation_dict = {}
    for row in annotation_list:
        taxon_name_match = data_name_matcher.match(row[index_column])
        if not taxon_name_match:
            raise ValueError("taxon name %s in input file does not match regex pattern" % row[index_column])
        key_name = "".join(taxon_name_match.groups())
        annotation_dict[key_name] = [
                row[trait] if row[trait] is not None else "" for trait
                in traits]
    return annotation_dict
