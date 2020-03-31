from clusterfunk.phylotype import *


def run(options):
    phylotyper = Phylotyper(options.threshold, options.csv)
    phylotyper.run(options.input, options.output)
