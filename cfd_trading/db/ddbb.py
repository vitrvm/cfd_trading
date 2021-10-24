import os
import sqlite3 as sql
import pandas as pd


class DataBase(object):
    def __init__(self, params):
        self.__filename = params.filename
        if params.path:
            self.__path = params.path
        self.__ticker = params.ticker

        self.__conn = None
        try:
            self.__conn = sql.connect(os.path.join(self.__path, f"{self.__filename}.db"))
        except Exception as e:
            print(e)

        self.__c = self.__conn.cursor()

        self.__start()

    def __start(self):
        query = f'''CREATE TABLE IF NOT EXISTS "{self.__ticker}" (
            "Date" TIMESTAMP,
            "Ask" REAL,
            "Bid" REAL,
            "AskVolume" REAL,
            "BidVolume" REAL
        )'''

        self.__execute_n_commit(query)

    def __execute_n_commit(self, query):
        self.__c.execute(query)
        self.__conn.commit()

    def get_last_row(self):
        query = f'SELECT * FROM {self.__ticker} WHERE ROWID = (SELECT MAX(ROWID) FROM {self.__ticker})'

        df = pd.read_sql_query(query, self.__conn, parse_dates='Date')

        assert(type(df['Date'][0]) is pd.Timestamp)

        return df['Date'][0]

    def add_row(self, item):
        query = f'''
            INSERT INTO "{self.__ticker}"("Date","Ask","Bid","AskVolume","BidVolume") 
            VALUES (NULL,NULL,NULL,NULL,NULL);
        '''
        pass