import os
import sqlite3 as sql


class DataBase(object):
    def __init__(self, params):
        self.__filename = params.filename
        if params.path:
            self.__path = params.path
        self.__ticker = params.ticker

        self.__conn = None
        try:
            self.__conn = sql.connect(os.path.join())
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
        self.__conn.commit(query)


    def get_last_entry(self, ticker):
        query = f'SELECT * FROM {ticker} WHERE ROWID = (SELECT MAX(ROWID) FROM {ticker})'

        self.__c.execute(query)

        result = self.__c.fetchall()

        return result

