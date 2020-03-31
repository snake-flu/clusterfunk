from clusterfunk.phylotype import *


def run(options):
    phylotyper = Phylotyper(options.threshold)
    phylotyper.run(options.input, options.output)
