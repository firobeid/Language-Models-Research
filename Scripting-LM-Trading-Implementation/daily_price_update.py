
import sys
import pandas as pd
import eikon as ek
import numpy as np
import os
from time import sleep
from tqdm import tqdm
import datetime
import json
from pytz import timezone # set timezone
# Ignore harmless warnings
import warnings
warnings.filterwarnings("ignore")
ek.set_app_key('b3128062087743ed9ccc1b11527f589a9841f6fa')

if ek.get_port_number() == '9000':
    pass
else:
    print('No Connection with Eikon! RESTART THAT BITCH!')
    sleep(100)
    
sp500_symbols = list(ek.get_data(['0#.SPX'], 'TR.RIC')[0]['RIC'])
dowjones_symboles = list(ek.get_data(['0#.DJI'], 'TR.RIC')[0]['RIC'])  
nasdaq100_symbols = list(ek.get_data(['0#.NDX'], 'TR.RIC')[0]['RIC'])
unique_index_symbols = list(np.unique(sp500_symbols + dowjones_symboles + nasdaq100_symbols))

stock_universe = [i.split('.')[0] for i in list(np.unique(sp500_symbols + dowjones_symboles + nasdaq100_symbols))]
with open('../stock_universe.json', 'w', encoding='utf-8') as f:
        json.dump(stock_universe, f, ensure_ascii=False, indent=4)


DATA_PATH = '../models_DB.h5'

def update_prices():
    prices = pd.DataFrame()
    with pd.HDFStore(DATA_PATH, mode = 'r+') as store:
        print(store.keys()) 
        #table = str(input('Enter table key printed above: '))
        df = store['prices/daily'].sort_index()
        max_date = df.index.get_level_values(0).max()
        start = max_date + datetime.timedelta(1)
        start = start.strftime('%Y-%m-%d')
        now = datetime.datetime.now(timezone('US/Eastern'))
        now = now.strftime('%Y-%m-%d') 
        while True:
            if max_date.strftime('%Y-%m-%d') != now:
                print('Price update found from %s to %s !' % (start, now))
                for symbol in tqdm(unique_index_symbols):
                    try:
                        df = ek.get_timeseries([symbol],
                                            start_date=start,
                                            end_date=now,
                                            normalize= True,
                                            fields= '*',
                                            calendar = 'tradingdays',
                                            interval = 'daily')# end date is included in output
                    except ek.EikonError:
                        sleep(5)
                    except (Exception, ek.eikonError.EikonError) as error:
                        print("EIKON error: {0}".format(error))
                        sleep(5)
                    except ValueError:
                        raise
                    except:
                        print("Unexpected error:", sys.exc_info()[0])
                        raise
                    if len(df) != 0:
                        df0 = df.loc[df.Security == symbol, ['Date','Field', 'Value']]
                        columns_name = {'CLOSE': 'close','OPEN': 'open', 'VOLUME': 'volume',
                                        'HIGH': 'high', 'LOW': 'low','Date': 'date', 'Security': 'ticker'}
                        df_pivot = df0.pivot(index ='Date', columns='Field', values='Value').reset_index().rename(columns = columns_name)
                        df_pivot['ticker'] = symbol.split('.')[0]
                        # Join to main dataframe
                        prices = prices.append(df_pivot, ignore_index=True)
                        print(symbol+':'+start+':'+now)
                        sleep(0.2)
                    else: 
                        sleep(0.2)
                        pass
                prices = prices.set_index(['date', 'ticker'])
                prices = prices[['open', 'close', 'high', 'low', 'volume']]
                prices.columns.names = ['']
                store.put('/prices/daily', prices, encoding = 'UTF-8',format = 'table',append = True)
                print('++++++++++++++++ALL DONE!++++++++++++++++++++')
                print('Upload Completed on:', datetime.datetime.now(timezone('US/Eastern')).strftime('%Y-%m-%dT%H:%M:%S'))
                print('Moving on to next task')
                break
            else:
                print('Prices already Up to Date!')
                print('System will exit now!')
                print('Moving on to next task')
                break
def pct_change(df):
    return (df.close.shift(-1) - df.close)/ df.close

def get_true_labels():
    #Get todays prices to get true label
    today = (datetime.datetime.now()).strftime('%Y-%m-%d')
    with pd.HDFStore(DATA_PATH, 'r+') as store:
        daily = store['prices/daily'].sort_index()
        daily = daily[~daily.index.duplicated()] # added this when removed sys.exit() fro previous func and while loop kept uploading same data
        daily.sort_index(level=[0, 1], ascending=[1, 0], inplace=True)
        max_prices = daily.index.get_level_values(0).max()
        max_prices = (pd.to_datetime(max_prices)).strftime('%Y-%m-%d')
        store.close()
        if (max_prices == today): 
            pass
        else: 
            print("Please Upload today's closing Prices!")
            sys.exit()
    if (len(daily) > 0): 
        with pd.HDFStore(DATA_PATH) as store:
            print(store.keys())
            df = store['predictions/news/daily'].sort_index()
            store.close()
#             max_date = df.index.get_level_values(0).max() # the prediction date awaiting validating if correct
#             max_date = (pd.to_datetime(max_date)).strftime('%Y-%m-%d')
#             today = (datetime.datetime.now()).strftime('%Y-%m-%d')
# #             if (max_date == today):
#             df = df.loc[today]
# #             else: 
# #                 print('Predictions for today are not avialable!')
# #                 sys.exit()  
        #Get rutrns and encode them
        daily['returns'] = daily.groupby('ticker', group_keys=False).apply(pct_change).shift(1)
        daily['label'] = daily.returns.where(daily.returns > 0, 0).where(daily.returns < 0, 1)
        daily.dropna(subset=['returns'], inplace = True)
        #fix index format to join tables on intersection
        new_tuples = df.index.map(lambda x: (pd.to_datetime(x[0]), x[1]))
        df.index = pd.MultiIndex.from_tuples(new_tuples, names=["date", "ticker"])
        #Join on intersection
        intersect = daily.index.intersection(df.index)
        df = df.loc[intersect, :].sort_index()
        daily = daily.loc[intersect, :].sort_index()
        daily = daily.join(df[['Predictions_V1', 'Predictions_V2', 'BUY_V1','BUY_V2']])
        daily = daily.loc[today]
        store.close()
        with pd.HDFStore(DATA_PATH, 'r+') as store:
            labels = store['predictions/news/true_daily']
            max_date = labels.index.get_level_values(0).max()
            if max_date.strftime('%Y-%m-%d') != today:
                store.put('predictions/news/true_daily', daily, encoding = 'UTF-8',format = 'table',append = True)
                print('+++++++++All Done!+++++++++')
                print('True stock price labels has been uploaded for %s!' % today)
            else: print('Labels already update!')
        sys.exit()
    else:sys.exit()

if __name__ == '__main__':
    update_prices()
    get_true_labels()
                