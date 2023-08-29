import sys
import pandas as pd
import eikon as ek
import numpy as np
import os
from time import sleep
from tqdm import tqdm
import datetime
import json
from pathlib import Path
from pytz import timezone # set timezone
# Ignore harmless warnings
import warnings
warnings.filterwarnings("ignore")
ek.set_app_key('******')

if ek.get_port_number() == '9000':
    pass
else:
    print('No Connection with Eikon! RESTART THAT BITCH!')
    
    
sp500_symbols = list(ek.get_data(['0#.SPX'], 'TR.RIC')[0]['RIC'])
dowjones_symboles = list(ek.get_data(['0#.DJI'], 'TR.RIC')[0]['RIC'])  
nasdaq100_symbols = list(ek.get_data(['0#.NDX'], 'TR.RIC')[0]['RIC'])
unique_index_symbols = list(np.unique(sp500_symbols + dowjones_symboles + nasdaq100_symbols))

stock_universe = [i.split('.')[0] for i in list(np.unique(sp500_symbols + dowjones_symboles + nasdaq100_symbols))]
with open('stock_universe.json', 'w', encoding='utf-8') as f:
        json.dump(stock_universe, f, ensure_ascii=False, indent=4)
        
# https://github.com/Refinitiv-API-Samples/Article.EikonAPI.Python.NewsSentimentAnalysis
#LMITS : https://developers.refinitiv.com/eikon-apis/eikon-data-api/docs?content=49692&type=documentation_item
# 10,000 reuests per day --- 5 requests per second --- 50 MB per minute ---
news_db = Path("..","news_db.h5")
db = pd.HDFStore(news_db, mode = 'r+') # 'r+' = File must already exist
if db.is_open == False:
    db.open()
    
unique_index_symbols.reverse()

def news_update():
    api_calls = 0
    for t in tqdm(unique_index_symbols):
        if '/'+ t.split('.')[0] in db.keys(): 
            df = db[t.split('.')[0]]
#             end_at = (df.loc[:, 'versionCreated'].min()  - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
#             begin_from = (df.loc[:, 'versionCreated'].min() - datetime.timedelta(days=18)).strftime('%Y-%m-%d')
            end_at = (datetime.datetime.now()).strftime('%Y-%m-%d')
            begin_from = (df.loc[:, 'versionCreated'].max() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            end_at = (datetime.datetime.now()  - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            begin_from = (datetime.datetime.now() - datetime.timedelta(days = 30)).strftime('%Y-%m-%d')
        for start in pd.date_range(start = begin_from, end = end_at,normalize=True, tz = 'US/Eastern',freq = 'D'):
            if api_calls >= int(9900): break
            else: api_calls+=1
            print('API REQUEST #:  ', api_calls)
            end = start + datetime.timedelta(days=1)
            start = start.strftime('%Y-%m-%dT%H:%M:%S')
            end = end.strftime('%Y-%m-%dT%H:%M:%S') 
            try:
                news = ek.get_news_headlines('R:%s AND Language:LEN' % t, 
                                                  count= 100,
                                                  date_from= start,
                                                  date_to= end) #Up too but not including end date!
            except ek.EikonError:
                sleep(5)
            except (Exception, ek.eikonError.EikonError) as error:
                print("EIKON error: {0}".format(error))
                sleep(5)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
            if len(news) != 0:
                news['ticker'] = t.split('.')[0]
                db.put(t.split('.')[0], news, format = 'table',append = True, 
                       data_columns = True, 
                       min_itemsize={'text': 1000, 'sourceCode': 1000, 'storyId': 100},
                       encoding = 'UTF-8')
                print(t+':'+start+':'+end)

                sleep(0.25)
            else:
                print('No News Found: '+t+':'+start+':'+end)
                pass
                sleep(0.25)

        sleep(0.25)

    db.close()
    print('++++++++++++++++ALL DONE!++++++++++++++++++++')
    print('Upload Completed on:', datetime.datetime.now(timezone('US/Eastern')).strftime('%Y-%m-%dT%H:%M:%S'))
    sys.exit()

if __name__ == '__main__':
    news_update() 