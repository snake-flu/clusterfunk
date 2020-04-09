from clusterfunk.annotate_tree import TreeAnnotator


def check_all_the_same(l):
    currentCheck = ".".join(l[0])
    for entry in l:
        if ".".join(entry) != currentCheck:
            return False
        currentCheck = ".".join(entry)

    return True


def trim_traits(trait_list, index):
    return [l[0:index] for l in trait_list]


class Subtyper:
    def __init__(self, tree, index, separator, root_subtype="A"):
        self.tree = tree
        self.traits = []
        self.traitName = "lineage"
        self.root_subtype = "A"
        annotator = TreeAnnotator(tree)
        annotator.annotate_tips_from_label(self.traitName, index, separator)

        pass

    def get_subtype(self, taxon):
        tip = self.tree.find_node_with_taxon_label(taxon)
        if tip is None:
            raise ValueError("Taxon %s not found in tree" % taxon)

        sibling_nodes = tip.sibling_nodes()
        sibling_tips = [tip for tip in sibling_nodes if tip.is_leaf()]
        if len(sibling_tips) > 0:
            traits = list(set([tip.annotations.get_value(self.traitName) for tip in sibling_tips]))
            return traits[0]

        # If this is in a polytomy then we can impute the parent state and assign it here. so long as there are multiple
        # TODO check siblings with lineages assigned.
        # sibling lineages with assigned lineages will always be == number of siblings in guide tree

        # If there aren't any sibling tips then we have to traverse the cousins to get the traits down those lines
        parent_or_gran = tip.parent_node if len(sibling_nodes) > 1 else tip.parent_node.parent_node

        if parent_or_gran is None:
            if tip.parent_node == self.tree.seed_node:
                return self.root_subtype

        cousins_traits = list(set([leaf.annotations.get_value(self.traitName) for leaf in parent_or_gran.leaf_iter() if
                                   leaf != tip and len(leaf.annotations.get_value(self.traitName)) > 0]))

        if len(cousins_traits) == 1:
            return cousins_traits[0]

        else:
            # prune all traits to same length
            split_traits = []
            for trait in cousins_traits:
                split_traits.append(trait.split("."))
            most_ancestral_trait_length = min([len(t) for t in split_traits])
            split_traits = trim_traits(split_traits, most_ancestral_trait_length)

            keep_trimming = True
            while len(split_traits[0]) > 1 and keep_trimming:

                if check_all_the_same(split_traits):
                    keep_trimming = False
                else:
                    split_traits = trim_traits(split_traits, -1)

            split_traits.sort()
            subtype = ".".join(split_traits[0])

            return subtype
