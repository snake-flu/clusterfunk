import dendropy
import csv
from clusterfunk.extract_tip_annotations import *


def run(options):
    tree = dendropy.Tree.get(path=options.input, schema="nexus", preserve_underscores=True)
    annotation_extractor = AnnotationExtractor(tree)
    annotations = annotation_extractor.get_annotations(options.traits)

    with open(options.output, "w") as csvfile:
        fileheader = ["taxon"] + options.traits
        writer = csv.DictWriter(csvfile, fieldnames=fileheader)
        writer.writeheader()
        for tip_annotation in annotations:
            writer.writerow(tip_annotation)
