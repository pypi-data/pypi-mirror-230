class UserError(Exception):
    pass


class TryAgain(Exception):
    pass


class Timeout(Exception):
    pass


class InvalidTag(UserError):
    def __init__(self, message):
        self.message = message


class SearchError(Exception):
    def __init__(self, message):
        self.message = message


class AWSError(Exception):
    def __init__(self, message):
        self.message = message


class OpenAIAuthenticationError(UserError):
    pass
