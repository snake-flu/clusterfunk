import csv
import re
import sys
import warnings

import chardet

from clusterfunk.relabel_tips import get_traits_from_metadata, TipLabeler
from clusterfunk.utils import prepare_tree, write_tree


def run(options):
    if not options.verbose:
        warnings.filterwarnings("ignore")
    tree = prepare_tree(options)
    relabeler = TipLabeler(tree, re.compile(options.parse_taxon), options.separator, options.replace)
    if options.traits_file is not None:
        get_data_key = re.compile(options.parse_data)
        rawdata = open(options.traits_file, "rb").read()
        result = chardet.detect(rawdata)

        with open(options.traits_file, encoding=result['encoding']) as metadata:
            dialect = csv.Sniffer().sniff(metadata.readline())
            metadata.seek(0)
            reader = csv.DictReader(metadata, dialect=dialect)
            annotations = get_traits_from_metadata(reader, options.index_column, get_data_key, options.trait_columns)

        relabeler.relabel_tips(annotations)

    elif options.from_traits is not None:
        relabeler.relabel_tips_from_traits(options.from_traits)

    else:
        sys.exit("No trait names or meta data provided. exiting")

    write_tree(tree, options)
