class DuplicateKnowledgeBaseError(Exception):
    pass


class DuplicateDocumentContentError(Exception):
    pass


class DocumentLengthError(Exception):
    pass


class AuthenticationFailedError(Exception):
    pass


class InternalServerError(Exception):
    pass


class InvalidRequestError(Exception):
    pass


class TimeoutError(Exception):
    pass


class NotFoundError(Exception):
    pass

