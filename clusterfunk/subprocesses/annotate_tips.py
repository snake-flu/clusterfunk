import re

from clusterfunk.subProcess import SubProcess
from clusterfunk.utilities.treeAnnotator import TreeAnnotator
from clusterfunk.utilities.utils import MetadataParser


class TipAnnotator(SubProcess):
    """
    A subprocess that handles the logic of how to annotate the tips of a tree and then
    calls the required methods of the TreeAnnotator class.
    """

    def __init__(self, options):
        super().__init__(options)
        self.parser = MetadataParser()

    def run(self, tree):

        if self.options.parse_taxon is not None:
            annotator = TreeAnnotator(tree, re.compile(self.options.parse_taxon))
        else:
            annotator = TreeAnnotator(tree)

        """
        Annotations will be coming from a traits file (tsv or csv)
        """
        if self.options.traits_file is not None:
            annotations = self.parser.parse_dsv(self.options.traits_file, self.options.index_column,
                                                self.options.trait_columns, self.options.parse_data)
            annotator.annotate_tips(annotations)

        """
        Getting annotations from taxon names
        """
        if self.options.from_taxon:
            for string in self.options.from_taxon:
                trait, regex = string.split("=")
                annotator.annotate_tips_from_label(trait, re.compile(regex))

        """
        Creating boolean annotations from a trait name / value pair
        """
        i = 0
        if self.options.boolean_for_trait is not None:
            for string in self.options.boolean_for_trait:
                trait_name, regex = string.split("=")
                boolean_trait_name = self.options.boolean_trait_names[i] if len(
                        self.options.boolean_trait_names) > i else trait_name + "_boolean"
                annotator.add_boolean_trait(trait_name, boolean_trait_name, re.compile(regex))
                i += 1

        """
        Annotate the mrca of all values of the provided annotation
        """
        if self.options.mrca is not None:
            for trait_name in self.options.mrca:
                #         get values of traits
                values = list(set([node.annotations.get_value(trait_name) for node in
                                   tree.leaf_node_iter(lambda tip: tip.annotations.get_value(trait_name) is not None)]))
                values.sort()
                for value in values:
                    annotator.annotate_mrca(trait_name, value)
