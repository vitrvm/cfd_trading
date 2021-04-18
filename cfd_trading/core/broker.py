from cfd_trading.core.errors import AuthenticationError
from cfd_trading.core.errors import NotSupported
from cfd_trading.core.account import Accounts

import pandas as pd


__all__ = ['Broker',]

class Broker(object):

    name = None
    version = None

    session = None
    timeframes = None
    symbols = None

    requiredCredentials = {
        'apiKey': False,
        'login': False,
        'password': False,
        'account': False,
        'accType': False
    }

    # Accounts
    accounts = None
    current_account = None

    currencies = None


    # API for brokers
    api = {
        ''
    }

    def __init__(self, config={}):
        """
        Each broker has a unique config configuration. Referr to class.__doc__ for more information.
        """

        settings = self.load_config(self.describe(), config)

        for key in settings:
            if hasattr(self, key) and isinstance(getattr(self, key), dict):
                setattr(self, key, self.load_config(getattr(self, key), settings[key]))
            else:
                setattr(self, key, settings[key])

        
        self.session = self.start_session()

    def __str__(self):
        return self.name

    def describe(self):
        return {}

    def load_accounts(self, refresh=False, params={})->Accounts:
        if refresh:
            self.accounts = self.fetch_accounts(params)
        else:
            if self.accounts is not None:
                return self.accounts
            else:
                self.accounts = self.fetch_accounts(params)
        return self.accounts

    def check_required_credentials(self, error=True):
        keys = list(self.requiredCredentials.keys())
        for key in keys:
            try:
                self.requiredCredentials[key] and not getattr(self, key)
            except:
                raise AuthenticationError(f'requires `{key}`')
        return True

    def start_session(self):
        raise NotSupported(f'{self.name} start_session() pure method must be redefined in derived classes')

    def fetch_accounts(self)->Accounts:
        raise NotImplementedError(f'fetch_accounts not implemented in derived class')

    def fetch_balance(self, account=None, refresh=False)->dict:
        """
        Returns dict {'balance'
        """
        raise NotImplementedError(f'fetch_accounts not implemented in derived class')

    def fetch_ohlcv(self, symbol, timeframe='1m', limit=20, params={})->pd.DataFrame:
        raise NotImplementedError(f'fetch_ohlcv not implemented in derived class')

    def handle_errors(self, e):
        raise NotImplementedError(f'handle_errors not implemented in derived class')

    @staticmethod
    def load_config(*args):
        result = None
        for arg in args:
            if isinstance(arg, dict):
                if not isinstance(result, dict):
                    result = {}
                for key in arg:
                    result[key] = Broker.load_config(result[key] if key in result else None, arg[key])
            else:
                result = arg
        return result