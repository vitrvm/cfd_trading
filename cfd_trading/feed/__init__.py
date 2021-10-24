import os
import datetime as dt
import sqlite3
import pandas as pd

from findatapy.market import Market, MarketDataRequest, MarketDataGenerator


class Feeder(object):

    name = None
    version = None

    data_path = './data/nq100'
    extensions = {'sqlite3':'db', 'csv':'csv'}
    filename = None

    format = None
    formats = ['sqlite3', 'csv']

    start_date = None
    finish_date = None

    epics = None
    epic = None
    ticker = None
    fields = None
    field = None
    vendor_fields = None
    vendor_field = None
    freq = None
    
    def __init__(self, config={}) -> None:
        
        """
        Each feeder has a unique config configuration. Referr to class.__doc__ for more information.
        """

        settings = self.load_config(self.describe(), config)

        for key in settings:
            if hasattr(self, key) and isinstance(getattr(self, key), dict):
                setattr(self, key, self.load_config(getattr(self, key), settings[key]))
            else:
                setattr(self, key, settings[key])

        self.set_format()

        self.epic = self.epics[self.ticker]

        if self.format == 'csv':
            self.__conn = open(self.file_path(), 'a')
        if self.format == 'sqlite3':
            self.__conn = sqlite3.connect(self.file_path())
        
        # Set dates
        if self.start_date is None:
            self.start_date = self.format_date((self.get_last_date() + pd.DateOffset(1)))
        else:
            self.start_date = self.format_date(self.start_date)
        
        if self.finish_date is None:
            self.finish_date = dt.date.today().strftime('%d %b %Y')
        else:
            self.finish_date = self.format_date(self.finish_date)

        assert(self.str_to_date(self.start_date) < self.str_to_date(self.finish_date))

        # Set fields, freq
        if self.freq not in ['tick', 'candle']:
            raise Exception(f"Freq type is not in {['tick', 'candle']}")

    def update(self):
        self.save(self.start())

    def __str__(self):
        return self.name

    def describe(self):
        return {}

    @property
    def info(self) -> str:
        return f"Feeder name: {self.name} Version: {self.version}"

    def format_date(self, date:str)->str:
        pass

    def get_last_date(self):
        if self.format == 'sqlite3':
            query = f'SELECT * FROM {self.ticker} WHERE ROWID = (SELECT MAX(ROWID) FROM {self.ticker})'
            
            df = pd.read_sql_query(query, self.__conn, parse_dates='Date')
            assert(type(df['Date'][0]) is pd.Timestamp)

            return df['Date'][0]

    def save(self, df:pd.DataFrame):
        print(f"Saving data to {self.format}")
        if self.format == 'sqlite3':
            df.to_sql(f'{self.ticker}', self.__conn, if_exists='append')
        if self.format == 'csv':
            df.to_csv(f'{self.ticker}')

    def set_format(self):
        if self.format is None:
            self.format = 'csv'
        if self.format not in self.formats:
            raise Exception(f"Format is not a valid type. Values accepted {str(self.formats)}")
    
    def str_to_date(self, date:str)->dt.datetime:
        return dt.datetime.strptime(date, '%d %b %Y')

    def file_path(self):
        return os.path.join(self.data_path, f"{self.filename}.{self.extensions[self.format]}")

    def start(self)->pd.DataFrame:
        market = Market(market_data_generator=MarketDataGenerator())

        md_request = MarketDataRequest(
            start_date=self.start_date, 
            finish_date=self.finish_date, 
            fields=self.fields[self.freq],  
            vendor_fields=self.vendor_fields[self.freq], 
            freq=self.freq,
            data_source=self.name.lower(), 
            tickers=[self.ticker], 
            vendor_tickers=[self.epic])

        df = market.fetch_market(md_request)
        
        return self._clean_df(df)

    def _clean_df(self, df:pd.DataFrame)->pd.DataFrame:
        pass

    @staticmethod
    def load_config(*args):
        result = None
        for arg in args:
            if isinstance(arg, dict):
                if not isinstance(result, dict):
                    result = {}
                for key in arg:
                    result[key] = Feeder.load_config(result[key] if key in result else None, arg[key])
            else:
                result = arg
        return result