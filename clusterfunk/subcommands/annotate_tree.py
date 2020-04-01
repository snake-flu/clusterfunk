from clusterfunk.annotate_tree import *
import dendropy
import csv


def run(options):
    if (options.deltran and options.acctran):
        raise ValueError("Can not use both acctran and deltran flags")

    tree = dendropy.Tree.get(path=options.input, schema="nexus")
    annotator = TreeAnnotator(tree)

    if options.traits_file is not None:
        with open(options.traits_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            annotation_parser = AnnotationParser("taxon")
            annotations = annotation_parser.get_annotations(reader)
        annotator.annotate_tips(annotations)

    if options.acctran or options.deltran:
        acctran = True if options.acctran else False

        if len(options.traits) > 0:
            for annotation in options.traits:
                annotator.annotate_nodes_from_tips(annotation, acctran)

    tree.write(path=options.output, schema="nexus")
