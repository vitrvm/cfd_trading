import pandas as pd
import numpy as np

from ta.volatility import AverageTrueRange


def supertrend(df:pd.DataFrame, period=10, multiplier=3)->pd.DataFrame:
    #basic upper band = (high + low)/2 + (multipler * atr)
    #basic lower band = (high + low)/2 - (multipler * atr)
    atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)

    df['atr'] = atr.average_true_range()
    df['st_upperband'] = ((df['high']+df['low'])/2 + (multiplier*df['atr']))
    df['st_lowerband'] = ((df['high']+df['low'])/2 - (multiplier*df['atr']))
    df['in_uptrend'] = True

    for current in range(1, len(df.index)):
        previous = current-1

        if df['close'][current] > df['st_upperband'][previous]:
            df['in_uptrend'][current]  = True
        elif df['close'][current] < df['st_lowerband'][previous]:
            df['in_uptrend'][current]  = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]
            if df['in_uptrend'][current] and df['st_lowerband'][current] < df['st_lowerband'][previous]:
                df['st_lowerband'][current] = df['st_lowerband'][previous]
            if not df['in_uptrend'][current] and df['st_upperband'][current] > df['st_upperband'][previous]:
                df['st_upperband'][current] = df['st_upperband'][previous]
    return df

