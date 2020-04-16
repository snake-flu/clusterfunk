import csv
from clusterfunk.extract_tip_annotations import *
from clusterfunk.utils import prepare_tree


def run(options):
    tree = prepare_tree(options, options.input)
    annotations = get_annotations(tree, options.traits)

    with open(options.output, "w") as csvfile:
        fileheader = ["taxon"] + options.traits
        writer = csv.DictWriter(csvfile, fieldnames=fileheader)
        writer.writeheader()
        for tip_annotation in annotations:
            writer.writerow(tip_annotation)
