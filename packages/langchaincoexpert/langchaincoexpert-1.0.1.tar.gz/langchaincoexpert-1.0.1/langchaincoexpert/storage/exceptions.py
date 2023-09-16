from langchaincoexpert.schema import langchaincoexpertException


class InvalidKeyException(langchaincoexpertException):
    """Raised when a key is invalid; e.g., uses incorrect characters."""
