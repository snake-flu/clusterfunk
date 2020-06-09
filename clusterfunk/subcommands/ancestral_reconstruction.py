from clusterfunk.annotate_tree import TreeAnnotator
from clusterfunk.subProcess import SubProcess
from clusterfunk.utils import check_str_for_bool


class AncestorReconstructor(SubProcess):
    """
    Ancestor reconstructor process. Makes calls to TreeAnnotator annotate nodes from tips
    In the future the these methods might be added to this class
    """

    def __init__(self, options):
        super().__init__(options)
        self.acctran = True if options.acctran else False

    def run(self, tree):
        """
        Annotate from tips for each trait provided at construction
        :param tree:
        :return:
        """
        annotator = TreeAnnotator(tree)

        if len(self.options.traits) > 0:
            i = 0
            for trait in self.options.traits:
                # Get ancestral state if provided at command line
                ancestral_state = (check_str_for_bool(self.options.ancestral_state[i]) if len(
                        self.options.ancestral_state) > i else None) if self.options.ancestral_state is not None else None

                annotator.annotate_nodes_from_tips(trait, self.acctran, ancestral_state)
                i += 1
