import re
import sys
import warnings

from clusterfunk.subProcess import SubProcess
from clusterfunk.utilities.utils import MetadataParser


class TipLabeler(SubProcess):
    """
    TipLabeler subprocess. This relabels tips in a tree according to a metadata file or traits in the tree.
    """

    def __init__(self, options):
        super().__init__(options)
        self.taxon_regex = re.compile(options.parse_taxon) if options.parse_taxon is not None else re.compile("(.*)")
        self.separator = options.separator if options.separator is not None else "|"
        self.replace = options.replace if options.replace is not None else False
        self.parser = MetadataParser()

    def run(self, tree):

        if self.options.traits_file is not None:
            annotations = self.parser.parse_dsv(self.options.traits_file, self.options.index_column,
                                                self.options.trait_columns, self.options.parse_data)
            self.relabel_tips(tree, annotations)

        elif self.options.from_traits is not None:
            self.relabel_tips_from_traits(tree, self.options.from_traits)

        else:
            sys.exit("No trait names or meta data provided. exiting")

    def taxon_parser(self, taxon_label):
        """
        Method that converts a taxon label into the string expected in the metatdata
        :param taxon_label:
        :return: string
        """
        match = self.taxon_regex.match(taxon_label)
        if not match:
            raise ValueError("taxon name %s in tree file does not match regex pattern" % taxon_label)
        return "".join(match.groups())

    def relabel_tips_from_traits(self, tree, traitNames):
        """
        Relabel the tips in a tree witht the values of the traits provided
        :param tree:
        :param traitNames:
        """
        annotations = {}
        for tip in tree.leaf_node_iter():
            annotations[tip.taxon.label] = [
                    tip.annotations.get_value(trait) if tip.annotations.get_value(trait) is not None else "" for trait
                    in traitNames]

        self.relabel_tips(tree, annotations)

    def relabel_tips(self, tree, annotations):
        """
        Wrapper that calls tip relabeling method on each tip
        :param tree:
        :param annotations:
        :return:
        """
        for tip_label in annotations:
            self.relabel_tip(tree, tip_label, annotations[tip_label])

    def relabel_tip(self, tree, tip_label, annotation_values):
        """
        Relabel the tips in a tree with the provided annotation values
        :param tree:
        :param tip_label: - taxon label that is to be replace or appened to.
        :param annotation_values:
        :return:
        """
        node = tree.find_node_with_taxon(
                lambda taxon: True if self.taxon_parser(taxon.label) == tip_label else False)
        if node is None:
            warnings.warn("Taxon: %s not found in tree" % tip_label, UserWarning)
        else:
            new_label = self.separator.join([str(annotation_values.get(x)) for x in annotation_values])
            if self.replace:
                node.taxon.label = new_label
            else:
                node.taxon.label = node.taxon.label + self.separator + new_label
