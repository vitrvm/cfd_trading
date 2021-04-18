class BaseError(Exception):
    pass

class BrokerError(BaseError):
    pass

class AuthenticationError(BrokerError):
    pass
        

class NotSupported(BrokerError):
    pass

__all__ = [
    'BaseError',
    'BrokerError',
    'AuthenticationError',
    'NotSupported'
]