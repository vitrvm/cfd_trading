from cfd_trading.core.broker import Broker
from cfd_trading.core.monitor import BasicMonitor
from cfd_trading.core.account import Account, Accounts
from cfd_trading.core.order import Order

from trading_ig import IGService

import pandas as pd


class IG(Broker):

    """
    A class for IG Trading Broker ig.com. 

    To init class must pass config param:
    
    Example:
        config = {
        'login': your_login,
        'password': your_password,
        'apiKey': your_apiKey,
        'accType': 'DEMO' or 'LIVE',
        'account': your_account_number
        }

        cfd_trading.IG(config)

    Methods
    -------

    load_accounts(refresh=False, params={})
        Returns accounts as a list. If refresh true, reloads account data from broker. This is the preferred way to access Accounts.
    fetch_accounts()
        Returns Accounts class.
    fetch_ohlcv(symbol, timeframe='1m', limit=20)
        Returns pandas.Dataframe with open/high/low/close/volume for a given symbol and timeframe
    """
    
    session: IGService

    def describe(self):
        return self.load_config(super(IG, self).describe(), {
            'name': 'IG',
            'version': 'v0.1',

            'requiredCredentials':  {
                'login': True,
                'password': True,
                'apiKey': True,
                'account': True,
                'accType': True
            },

            'timeframes': {
                '1m': '1Min',
                '3m': '3Min',
                '5m': '5Min',
                '15m': '15Min',
                '30m': '30Min',
                '1h': '1H',
                '2h': '2H',
                '4h': '4H',
                '1d': '1D',
                '1w': '1W'
            },

            'symbols': {
                'BTC': 'CS.D.BITCOIN.CFD.IP',
                'DAX30': 'IX.D.DAX.IFMM.IP',
                'DJI': 'IX.D.DOW.IFE.IP',
                'NDX100': 'IX.D.NASDAQ.IFE.IP',
                'SP500': 'IX.D.SPTRD.IFE.IP',
                'EURUSD': 'CS.D.EURUSD.MINI.IP'
            },

            'currencies': {
                'EUR': 'EUR',
                'USD': 'USD'
            }

        })

    def create_order(self, symbol: str, type_:Order.Type, action: Order.Action, quantity:float, level=None, stop_distance=None, stop_level=None, limit_distance=None, limit_level=None, trailing_stop=False, trailing_stop_increment=None, guaranteed_stop=False, good_till_date=None, quote_id=None, force_open=False):

        #force_open = True if limit_distance is not None or limit_level is not None or stop_distance is not None or stop_level is not None else False
        
        if limit_distance is not None or limit_level is not None or stop_distance is not None or stop_level is not None:
            assert(force_open)
        if guaranteed_stop:
            assert((stop_level is None and type(stop_distance) in [float, int]) or (stop_distance is None and type(stop_level) in [float, int]))
        if type_ is Order.Type.LIMIT:
            assert(quote_id is None)
            assert(type(level) is float)
        if type_ is Order.Type.MARKET:
            assert(level is None)
            assert(quote_id is None)
        if not trailing_stop:
            assert(trailing_stop_increment is None)
        if trailing_stop:
            assert(stop_level is None)
            assert(not guaranteed_stop)
            assert(type(stop_distance) is float and type(trailing_stop_increment) is float)
        #set only one
        assert(limit_distance is None or limit_level is None)
        assert(stop_distance is None or stop_level is None)

        instrument = self.session.fetch_market_by_epic(epic=self.symbols[symbol])

        if type_ is Order.Type.MARKET:
            params = {
                "currency_code": instrument['instrument']['currencies'][0]['code'],
                "direction": action,
                "epic": self.symbols[symbol],
                "expiry": instrument['instrument']['expiry'],
                "force_open": force_open,
                "guaranteed_stop": guaranteed_stop,
                "level": level,
                "limit_distance": limit_distance,
                "limit_level": limit_level,
                "order_type": type_,
                "quote_id": quote_id,
                "size": quantity,
                "stop_distance": stop_distance,
                "stop_level": stop_level,
                "trailing_stop": trailing_stop,
                "trailing_stop_increment": trailing_stop_increment,
            }
            print(params)
            return self.session.create_open_position(**params)

    def fetch_accounts(self, params={}):
        accounts = Accounts()
        response = self.session.fetch_accounts()
        for i, v in response.iterrows():
            acc = Account()
            acc.alias = v['accountAlias']
            acc.id = v['accountId']
            acc.name = v['accountName']
            acc.status = v['status']

            if v['accountType'] == 'CFD':
                acc.accType = Account.Type.CFD
            elif v['accountType'] == 'PHYSICAL':
                acc.accType = Account.Type.PHYSICAL
            elif v['accountType'] == 'SPREADBET':
                acc.accType = Account.Type.SPREADBET
            else:
                acc.accType = Account.Type.UNKNOWN
            
            acc.balance = v['balance']
            acc.currency = v['currency']
            accounts.add_account(acc)
        return accounts

    def fetch_balance(self, account=None, refresh=False) -> dict:
        if account is None:
            if self.current_account is None or self.accounts is None:
                self.load_accounts()    
            acc = self.current_account
        
        return_acc = self.accounts.get_account_by_id(id=acc)
        
        params = {
            'balance': return_acc.balance,
            'currency': self.currencies[return_acc.currency]
        }

        return params
        

    def fetch_ohlcv(self, symbol, timeframe='1m', limit=20, params={})->pd.DataFrame:
        bars = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
        
        symbol = self.symbols[symbol]
        resolution = self.timeframes[timeframe]
        limit = limit
        
        response = self.session.fetch_historical_prices_by_epic_and_num_points(epic=symbol, resolution=resolution, numpoints=limit)
        
        df = response['prices']
        
        bars['open'] = (df['bid']['Open']+df['ask']['Open'])/2
        bars['high'] = (df['bid']['High']+df['ask']['High'])/2
        bars['low'] = (df['bid']['Low']+df['ask']['Low'])/2
        bars['close'] = (df['bid']['Close']+df['ask']['Close'])/2
        bars['volume'] = df['last']['Volume']
        bars.index.names = ['datetime']
        
        return bars

    def start_session(self)->IGService:   
        self.check_required_credentials() 
        session = IGService(self.login, self.password, self.apiKey, self.accType)
        session.create_session()
        self.current_account = session.ig_session['currentAccountId']
        return session


class IGMonitor(BasicMonitor):

    __bars = None

    __last_tick = None

    timeframes = {
            '1s': 'SECOND',
            '1m': '1MINUTE',
            '5m': '5MINUTE',
            '1h': 'HOUR',
            'tick': 'TICK'
            }
    
    mode = None

    fields = None
    fields_timeframe = [
            'LTV',
            'TTV',
            'UTM',
            'DAY_OPEN_MID',
            'DAY_NET_CHG_MID',
            'DAY_PERC_CHG_MID',
            'DAY_HIGH',
            'DAY_LOW',
            'OFR_OPEN',
            'OFR_HIGH',
            'OFR_LOW',
            'OFR_CLOSE',
            'BID_OPEN',
            'BID_HIGH',
            'BID_LOW',
            'BID_CLOSE',
            'LTP_OPEN',
            'LTP_HIGH',
            'LTP_LOW',
            'LTP_CLOSE',
            'CONS_END',
            'CONS_TICK_COUNT'
        ]
    fields_tick = [
            'BID',
            'OFR',
            'LTP',
            'LTV',
            'TTV',
            'UTM',
            'DAY_OPEN_MID',
            'DAY_NET_CHG_MID',
            'DAY_PERC_CHG_MID',
            'DAY_HIGH',
            'DAY_LOW'
            ]

    def __init__(self, broker:IG, symbols:list, timeframe='1m', bars:pd.DataFrame=None) -> None:
        
        self.broker = broker

        if type(bars) is pd.DataFrame:
            self.__bars = bars[:-1]
        
        for i in symbols:
            self.items.append(f"CHART:{self.broker.symbols[i]}:{self.timeframes[timeframe]}")

        if timeframe == 'tick':
            self.mode = 'DISTINCT'
            self.fields = self.fields_tick
        else:
            self.mode = 'MERGE'
            self.fields = self.fields_timeframe

        super().__init__()

    def getBars(self) -> pd.DataFrame:
        return self.__bars

    def getLastTick(self) -> pd.DataFrame:
        return self.__last_tick

    def on_update(self, items):
        data = items['values']
        #['open', 'high', 'low', 'close', 'volume']
        try:
            if self.mode == 'MERGE':
                    utm = int(data['UTM'])
                    open = (float(data['BID_OPEN'])+float(data['OFR_OPEN']))/2
                    high = (float(data['BID_HIGH'])+float(data['OFR_HIGH']))/2
                    low = (float(data['BID_LOW'])+float(data['OFR_LOW']))/2
                    close = (float(data['BID_CLOSE'])+float(data['OFR_CLOSE']))/2
                    volume = float(data['LTV'])
                    df = pd.DataFrame({'datetime': utm, 'open': open, 'high': high, 'low': low, 'close': close, 'volume': volume}, index=[0])
            if self.mode == 'DISTINCT':
                utm = int(data['UTM']) if data['UTM'] is not None else None
                bid = float(data['BID']) if data['BID'] is not None else None
                ask = float(data['OFR']) if data['OFR'] is not None else None
                ltp = float(data['LTP']) if data['LTP'] is not None else None
                ltv = float(data['LTV']) if data['LTV'] is not None else None
                df = pd.DataFrame({'datetime': utm, 'bid': bid, 'ask': ask, 'ltp': ltp, 'ltv': ltv}, index=[0])

            pd.to_datetime(df['datetime'],unit='ms')
            df.set_index(['datetime'], inplace=True)
            df.index = pd.to_datetime(df.index, unit='ms')
            
            self.__last_tick = df
            
            if ('CONS_END' in data.keys() and int(data['CONS_END'])==1) or ('CONS_END' not in data.keys()):
                if isinstance(self.__bars, pd.DataFrame) and isinstance(df, pd.DataFrame):
                    self.__bars = self.__bars.append(df)
                if self.__bars is None:
                    self.__bars = df
        except:
            pass
        
__doc__ = """
Test Documentation
"""
