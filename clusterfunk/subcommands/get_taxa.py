from clusterfunk.get_taxa import *


def run(options):
    getter_writer = TaxaGetter(options.input, options.output)
    getter_writer.run()
