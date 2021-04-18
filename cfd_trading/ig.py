from cfd_trading.core.broker import Broker
from cfd_trading.core.monitor import BasicMonitor
from cfd_trading.core.account import Account, Accounts

from trading_ig import IGService

import pandas as pd


class IG(Broker):
    
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
            }

        })

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
            elif v['accoundType'] == 'PHYSICAL':
                acc.accType = Account.Type.PHYSICAL
            elif v['accoundType'] == 'SPREADBET':
                acc.accType = Account.Type.SPREADBET
            else:
                acc.accType = Account.Type.UNKNOWN
            
            acc.balance = v['balance']
            acc.currency = v['currency']
            accounts.add_account(acc)
        return accounts
            
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

    def __init__(self, broker:IG, symbols:list, timeframe='1m') -> None:
        
        self.broker = broker
        
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
        utm = int(data['UTM'])
        open = (float(data['BID_OPEN'])+float(data['OFR_OPEN']))/2
        high = (float(data['BID_HIGH'])+float(data['OFR_HIGH']))/2
        low = (float(data['BID_LOW'])+float(data['OFR_LOW']))/2
        close = (float(data['BID_CLOSE'])+float(data['OFR_CLOSE']))/2
        volume = float(data['LTV'])
        
        df = pd.DataFrame({'datetime': utm, 'open': open, 'high': high, 'low': low, 'close': close, 'volume': volume}, index=[0])
        pd.to_datetime(df['datetime'],unit='ms')
        df.set_index(['datetime'], inplace=True)
        
        self.__last_tick = df
        
        if int(data['CONS_END']):
            if isinstance(self.__bars, pd.DataFrame) and isinstance(df, pd.DataFrame):
                self.__bars = self.__bars.append(df)
            if self.__bars is None:
                self.__bars = df
            
        
        
    



