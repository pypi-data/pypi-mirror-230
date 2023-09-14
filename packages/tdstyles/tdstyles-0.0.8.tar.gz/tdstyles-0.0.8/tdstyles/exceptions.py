class NotStyleNotebook(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class NotAnAxisObject(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
