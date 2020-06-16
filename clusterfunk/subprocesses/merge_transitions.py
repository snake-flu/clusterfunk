from clusterfunk.subProcess import SubProcess
from clusterfunk.utilities.merger import Merger


class MergeTransitions(SubProcess):
    """
    Merge transitions at polytomies allowing one such merge on each path to the root.
    """

    def __init__(self, options):
        super().__init__(options)

        self.merger = Merger(options.trait_to_merge,
                             options.merged_trait_name,
                             prefix=options.prefix,
                             max_merge=options.max_merge,
                             merge_identical_samples=options.merge_sibling_singletons,
                             merge_siblings=options.merge_siblings)

    def run(self, tree):
        self.merger.merge(tree)
