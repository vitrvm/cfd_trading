import pandas as pd


def vwap(df:pd.DataFrame):
    q = df['Volume'].values
    p = (df['Low'] + df['Close'] + df['High']).div(3).values
    return df.assign(vwap=(p * q).cumsum() / q.cumsum())
