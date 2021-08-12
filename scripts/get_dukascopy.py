import pandas as pd
import os
import sqlite3 as sql

from datetime import date
from findatapy.market import Market, MarketDataRequest, MarketDataGenerator


class DukasCopy:

    EXTENTION = '.gzip'
    PATH = './data'

    def __init__(self, 
    freq:str, 
    tickers:str, 
    vendor_tickers:str,
    start_date=None, 
    finish_date=None,
    fields=['Bid', 'Ask', 'AskVolume', 'BidVolume'],
    vendor_fields=['ask', 'bid', 'askv', 'bidv'],
    filename=None):

        self.__start_date = start_date
        self.__finish_date = finish_date
        self.__freq = freq
        self.__tickers = tickers
        self.__vendor_tickers = vendor_tickers
        self.__fields = fields
        self.__vender_fields = vendor_fields

        self.__file_name = f"{self.__tickers}{self.EXTENTION}" if filename is None else f"{filename}{self.EXTENTION}"

        self.__last_df = pd.DataFrame()

        self.__conn = self.init_sql_conn()

        if self.__start_date is None:
            last_date = self.get_last_date()
            self.__start_date = (last_date + pd.DateOffset(1)).strftime("%d %b %Y")
        if self.__finish_date is None:
            self.__finish_date = date.today().strftime('%d %b %Y')

        self.__df = self.start()

        self.save_df(self.__df)

    def get_df(self):
        return self.__df

    def get_last_date(self):
        df = pd.read_sql_query(f'SELECT * FROM {self.__tickers} WHERE ROWID = (SELECT MAX(ROWID) FROM {self.__tickers})', self.__conn, parse_dates='Date')
        assert(type(df['Date'][0]) is pd.Timestamp)
        return df['Date'][0]

    def init_sql_conn(self):
        return sql.connect(os.path.join(self.PATH, f'{self.__tickers}.db')) 

    def save_df(self, df:pd.DataFrame):
        df.to_sql(f'{self.__tickers}', self.__conn, if_exists='append')

    def start(self)->pd.DataFrame:
        market = Market(market_data_generator=MarketDataGenerator())

        md_request = MarketDataRequest(
            start_date=self.__start_date, 
            finish_date=self.__finish_date, 
            fields=self.__fields,  
            vendor_fields=self.__vender_fields, 
            freq=self.__freq,
            data_source='dukascopy', 
            tickers=[self.__tickers], 
            vendor_tickers=[self.__vendor_tickers])

        df = market.fetch_market(md_request)
        
        return self.clean_df(df)

    def clean_df(self, df):
        df_temp = pd.DataFrame()
        df = df.dropna()
        df_temp['Ask'] = df['NASDAQ.Ask'].div(1000).apply(lambda x: round(x, 2))
        df_temp['Bid'] = df['NASDAQ.Bid'].div(1000).apply(lambda x: round(x, 2))
        df_temp['AskVolume'] = round(df['NASDAQ.AskVolume']*1000000)
        df_temp['BidVolume'] = round(df['NASDAQ.BidVolume']*1000000)
        return df_temp


if __name__ == '__main__':
    #dc = DukasCopy(freq='tick', tickers='NASDAQ', vendor_tickers='USATECHIDXUSD', start_date='01 Jan 2021', finish_date='04 Jan 2021', filename='NASDAQ')
    dc = DukasCopy(freq='tick', tickers='NASDAQ', vendor_tickers='USATECHIDXUSD', filename='NASDAQ')
    #dc = DukasCopy(freq='tick', tickers='NASDAQ', vendor_tickers='USATECHIDXUSD', start_date='03 Aug 2021', finish_date='04 Aug 2021')
    #dc = DukasCopy(freq='tick', tickers='NASDAQ', vendor_tickers='USATECHIDXUSD')