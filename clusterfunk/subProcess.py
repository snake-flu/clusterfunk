class SubProcess:
    def __init__(self, options):
        self.options = options
        self.handleOwnOutput = False

    def run(self, tree):
        return True
