class ProcessingJobNotFoundException(Exception):

    def __init__(self, search_criteria: str, value: str):
        self.search_criteria = search_criteria
        self.value = value

        super().__init__(f"Processing job with {search_criteria} '{value}' not found")
        