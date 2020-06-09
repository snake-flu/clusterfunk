import os

from clusterfunk.label_transitions import *
from clusterfunk.subProcess import SubProcess
from clusterfunk.utils import check_str_for_bool


class TranistionLabeler(SubProcess):
    """
    The logic of running the transition labeler.
    """

    def __init__(self, options):
        super().__init__(options)
        self.handleOwnOutput = True if options.exploded_trees else False
        self.annotator = TransitionAnnotator(options.trait,
                                             options.include_parent,
                                             options.transition_name,
                                             options.transition_prefix,
                                             options.include_root,
                                             options.stubborn)

    def run(self, tree):

        if self.options.exploded_trees:

            trees = self.annotator.split_at_transitions(tree,
                                                        check_str_for_bool(self.options.From),
                                                        check_str_for_bool(self.options.to))
            print(len(trees))
            if not os.path.exists(self.options.output):
                os.makedirs(self.options.output)

            i = 1
            for tree in trees:
                if self.options.out_format == "newick":
                    tree["tree"].write(path=self.options.output + "/" + tree["id"] + '.tree',
                                       schema=self.options.out_format,
                                       suppress_rooting=True)
                else:
                    tree["tree"].write(path=self.options.output + "/" + tree["id"] + '.tree',
                                       schema=self.options.out_format)

                i += 1

        else:
            count = self.annotator.annotate_transitions(tree,
                                                        check_str_for_bool(self.options.From),
                                                        check_str_for_bool(self.options.to))
            print(count)
