__all__ = [
    "ServiceNotFound",
    "AuthenticationRequired",
]


class ServiceNotFound(Exception):
    pass


class AuthenticationRequired(Exception):
    pass


class ClientLoginFailed(Exception):
    pass
