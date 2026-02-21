class ProcessingNotCompletedException(Exception):
    def __init__(self):
        super().__init__("Processing not completed yet")
        