import pandas as pd
import numpy as np

def vpoc(df:pd.DataFrame, grouper='D'):
    #df_group = df.groupby(pd.Grouper(freq=grouper))

    price_max = round(df['Bid'].max())
    price_min = round(df['Ask'].min())
    vol_profile = np.arange(101)
    vol_profile.fill(0.0)

    for index, row in df.iterrows():
        avg_price = round((row['Ask']+row['Bid'])/2)

        price = round(((avg_price-price_min)/(price_max-price_min))*100)

        vol_profile[price] = vol_profile[price] + round(row['BidVolume'])
        vol_profile[price] = vol_profile[price] + round(row['AskVolume'])

        vpoc = (vol_profile.argmax() * (price_max-price_min)/100) + price_min
        
        df.at[index, 'VPOC'] = vpoc

    return df
