import os
import sqlite3 as sql

from dotmap import DotMap

from cfd_trading import DukasCopy


def init_ddbb(conn:sql.connect, params):
    c = conn.cursor()

    query = f'''CREATE TABLE IF NOT EXISTS "{params.ticker}" (
                "Date" TIMESTAMP,
                "Ask" REAL,
                "Bid" REAL,
                "AskVolume" REAL,
                "BidVolume" REAL
            )'''

    c.execute(query)

    query = '''CREATE TABLE IF NOT EXISTS "VPOC" (
                "Date" TIMESTAMP,
                "VPOC" REAL,
                "yVPOC" REAL
            )'''
    c.execute(query)

    conn.commit()

def start_app(params:DotMap):
    conn = sql.connect(os.path.join(params.path, f'{params.filename}.db'))

    init_ddbb(conn, params)

    # Update database
    if params.update_ddbb:
        config = {'format':params.format,'filename' : params.filename,'ticker': params.ticker,'freq': 'tick'}
        if params.start_date:
            config['start_date'] = params.start_date
        if params.finish_date:
            config['finish_date'] = params.finish_date
        dc = DukasCopy(config=config)
        dc.update()

if __name__ == '__main__':
    params = DotMap()

    params.format = 'sqlite3'
    params.path = './data/dax40'
    params.filename = 'DAX40'
    params.ticker = 'DAX40'
    params.start_date = '2021-01-01'
    params.finish_date = '2021-02-01'
    params.update_ddbb = True

    start_app(params)
