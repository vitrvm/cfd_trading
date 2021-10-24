import datetime as dt
import pandas as pd

from cfd_trading.feed import Feeder


class DukasCopy(Feeder):
    
    """
    Retreve data from DukasCopy. Pass configuration through dictionary:
    config = {}

    :param filename: Filename
    :param format: 'sqlite', 'csv', default 'csv' 
    :param start_date: str, default None format 'YYYY-MM-DD' e.g:'2021-01-31'
    :param finish_date: str, default None format 'YYYY-MM-DD' e.g:'2021-01-31'
    :param ticker: str, default None official ticker....
    :param fields: list
    """

    def describe(self):
        return self.load_config(super(DukasCopy, self).describe(), {
            'name': 'DukasCopy',
            'version': 'v0.1',

            'epics': {
                'NASDAQ': 'USATECHIDXUSD',
                'SP500': 'USA500IDXUSD',
                'DAX40': 'DEUIDXEUR'
            },

            'fields': {
                'tick':['Bid', 'Ask', 'AskVolume', 'BidVolume'],
                'candle':['Open', 'Close', 'High', 'Low', 'Volume']
            },

            'vendor_fields': {
                'tick': ['ask', 'bid', 'askv', 'bidv'],
                'candle':['open', 'close', 'high', 'low', 'volume']
            }

        })

    def format_date(self, date):
        if date is not None:
            if isinstance(date, str):
                date = (dt.datetime.strptime(date, "%Y-%m-%d")).strftime("%d %b %Y")
            if isinstance(date, dt.datetime):
                date = date.strftime("%d %b %Y")
            if isinstance(date, pd.Timestamp):
                date = date.strftime("%d %b %Y")
        return date
        
    def _clean_df(self, df:pd.DataFrame)->pd.DataFrame:
        df_temp = pd.DataFrame()
        df = df.dropna()
        df_temp['Ask'] = df[f'{self.ticker}.Ask'].div(1000).apply(lambda x: round(x, 2))
        df_temp['Bid'] = df[f'{self.ticker}.Bid'].div(1000).apply(lambda x: round(x, 2))
        df_temp['AskVolume'] = round(df[f'{self.ticker}.AskVolume']*1000000)
        df_temp['BidVolume'] = round(df[f'{self.ticker}.BidVolume']*1000000)
        return df_temp