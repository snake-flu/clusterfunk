from clusterfunk.annotate_tree import *
import dendropy
import csv

from clusterfunk.utils import check_str_for_bool, prepare_tree


def run(options):
    if options.deltran and options.acctran:
        raise ValueError("Can not use both acctran and deltran flags")
    if options.traits_file is not None and options.indices is not None:
        raise ValueError("Can annotate from a file and tip labels at the same time. Run as two separate steps")

    tree = prepare_tree(options)
    annotator = TreeAnnotator(tree)

    if options.traits_file is not None:
        with open(options.traits_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            annotations = get_annotations("taxon", reader)
        annotator.annotate_tips(annotations)

    if options.indices is not None and options.separator is not None:
        for i in range(0, len(options.traits)):
            annotator.annotate_tips_from_label(options.traits[i], options.index[i], options.separator)

    if options.acctran or options.deltran:
        acctran = True if options.acctran else False

        if len(options.traits) > 0:
            i = 0
            for annotation in options.traits:
                ancestral_state = check_str_for_bool(options.ancestral_state[i]) if len(
                    options.ancestral_state) > i else None
                annotator.annotate_nodes_from_tips(annotation, acctran, ancestral_state)
                i += 1

    tree.write(path=options.output, schema=options.format)
