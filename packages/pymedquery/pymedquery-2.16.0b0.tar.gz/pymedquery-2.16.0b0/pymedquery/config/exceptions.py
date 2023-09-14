class NoRecordsFound(Exception):
    """Throw this error when no records were returned"""

class CommitBouncedError(Exception):
    """Throw this error when the transaction failed and you were not able to commit"""

class ExtractError(Exception):
    """Throw this error when failed to extract data"""
