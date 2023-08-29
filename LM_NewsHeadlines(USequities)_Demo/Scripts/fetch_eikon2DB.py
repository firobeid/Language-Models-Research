import eikon as ek
import pandas as pd
import numpy as np
import psycopg2
import os
from io import StringIO
from time import sleep
from tqdm import tqdm
import sys
import datetime
from pytz import timezone # set timezone
# Ignore harmless warnings
import warnings
warnings.filterwarnings("ignore")
ek.set_app_key('#####')

param_dic = {
    "host"      : "####",
    "database"  : "####",
    "user"      : "postgres",
    "password"  : "#####"
}


if ek.get_port_number() == '9000':
    pass
else:
    print('No Connection with Eikon!')
    sys.exit()

sp500_symbols = list(ek.get_data(['0#.SPX'], 'TR.RIC')[0]['RIC'])
dowjones_symboles = list(ek.get_data(['0#.DJI'], 'TR.RIC')[0]['RIC'])  
nasdaq100_symbols = list(ek.get_data(['0#.NDX'], 'TR.RIC')[0]['RIC'])
unique_index_symbols = list(np.unique(sp500_symbols + dowjones_symboles + nasdaq100_symbols))

def get_prices(n_days, index, symbols, rename_index):
    end = datetime.datetime.now(timezone('US/Eastern'))
    start = end - datetime.timedelta(hours = n_days)
    hourly_prices = ek.get_timeseries([index],
                                    start_date=start,
                                    end_date=end,
                                    normalize= True,
                                    fields= ['High', 'Low', 'Open', 'Close', 'Volume'],
                                    calendar = 'tradingdays',
                                    interval = 'hour')
    hourly_prices.Security = str(rename_index)
    
    
    if symbols != None:
        for symbol in tqdm(symbols):
            df_temp = ek.get_timeseries([symbol],
                                        start_date=start,
                                        end_date=end,
                                        normalize= True,
                                        fields= ['High', 'Low', 'Open', 'Close', 'Volume'],
                                        calendar = 'tradingdays',
                                        interval = 'hour')

            # Join the two dataframes
            hourly_prices = hourly_prices.append(df_temp, ignore_index=True)
            sleep(0.5)
    hourly_prices.Date = hourly_prices.Date.apply(lambda dt: int((dt - datetime.datetime(1970,1,1)).total_seconds()))
    return hourly_prices

def final_data(n_days, index, symbols, rename_index):
    df = get_prices(n_days, index, symbols, rename_index)
    columns_name = {'CLOSE': 'close','OPEN': 'open', 'VOLUME': 'volume','HIGH': 'high', 'LOW': 'low','Date': 'time'}
    data = pd.DataFrame()
    for i in tqdm(df.Security.unique()):
        df0 = df.loc[df.Security == i, ['Date','Field', 'Value']]
        df_pivot = df0.pivot(index ='Date', columns='Field', values='Value').reset_index().rename(columns = columns_name)
        df_pivot['symbol'] = i
        data= data.append(df_pivot)
    data.symbol = data.symbol.apply(lambda x:x.split('.')[0])
    data.columns.name = None
    data = data[['symbol', 'close', 'open', 'volume', 'high', 'low', 'time']] # reorder columns for db purpose
    data = data.fillna(-1)
    data['volume'] = data['volume'].astype('int64')
    data = data.reset_index(drop = True)
    return data

def connect(params_dic):
    '''Connect to the PostgreSQL database server''' 
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print("Connection not successful!")
        sys.exit(1)
    print("Connection Successful!")
    return conn

def copy_to_db(conn, df, table):
    """
    save the dataframe in memory and use copy_from() to copy it to the table in the db
    """
    # save dataframe to an object in memory buffer
    buffer = StringIO()
    df.to_csv(buffer, header=False, index = False)
    buffer.seek(0)
    
    cursor = conn.cursor()
    try:
        cursor.copy_from(buffer, table, sep=",")
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("Done!")
    cursor.close()
    conn.close()

if __name__ == '__main__':
    copy_to_db(conn=connect(param_dic), df = final_data(24,'.DJI', None, 'dow'), table = 'hourly_price')
    copy_to_db(conn=connect(param_dic), df = final_data(24,'.SPX', None, 'spy500'), table = 'hourly_price')
    copy_to_db(conn=connect(param_dic), df = final_data(24,'.NDX', None, 'nasdaq'), table = 'hourly_price')