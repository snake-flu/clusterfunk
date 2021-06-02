import csv

from clusterfunk.subProcess import SubProcess


class AnnotationExtractor(SubProcess):
    def __init__(self, options):
        super().__init__(options)
        self.handleOwnOutput = True

    def get_annotations(self, tree, traits):
        tip_annotations = []
        for tip in tree.leaf_node_iter():
            row = {}
            row["taxon"] = tip.taxon.label
            for a in traits:
                row[a] = tip.annotations.get_value(a)
            tip_annotations.append(row)
        return tip_annotations

    def run(self, tree):
        annotations = self.get_annotations(tree, self.options.traits)

        with open(self.options.output, "w") as csvfile:
            fileheader = ["taxon"] + self.options.traits
            writer = csv.DictWriter(csvfile, fieldnames=fileheader, quoting=csv.QUOTE_MINIMAL, dialect = "unix")
            writer.writeheader()
            for tip_annotation in annotations:
                writer.writerow(tip_annotation)
