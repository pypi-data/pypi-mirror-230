"""Helper functions for managing the langchainmulti API.

This module is only relevant for langchainmulti developers, not for users.

.. warning::

    This module and its submodules are for internal use only.  Do not use them
    in your own code.  We may change the API at any time with no warning.

"""

from .deprecation import (
    langchainmultiDeprecationWarning,
    deprecated,
    suppress_langchainmulti_deprecation_warning,
)

__all__ = [
    "deprecated",
    "langchainmultiDeprecationWarning",
    "suppress_langchainmulti_deprecation_warning",
]
