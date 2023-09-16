from langchainmulti.schema import langchainmultiException


class InvalidKeyException(langchainmultiException):
    """Raised when a key is invalid; e.g., uses incorrect characters."""
