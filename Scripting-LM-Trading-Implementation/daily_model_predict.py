from functions import *
from email_predictions import send_email
import os
import pandas as pd
import numpy as np
import tensorflow as tf
import tensorflow.keras
from pytz import timezone # set timezone
# from tensorflow.keras.utils import to_categorical, plot_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow.keras.backend as K
import datetime
import sys
from pathlib import Path
from tqdm import tqdm
# Ignore harmless warnings
import warnings
warnings.filterwarnings("ignore")


os.environ['TF_XLA_FLAGS'] = "--tf_xla_cpu_global_jit"
# os.environ['XLA_FLAGS'] = "--xla_hlo_profile"

# fix random seed for reproducibility
K.clear_session()
tf.keras.backend.clear_session()
np.random.seed(42)
tf.random.set_seed(42)
# ../:to run from terminal -- ./: to run from jupyter
news_db = Path("..","news_db.h5")
DATA_PATH = "../models_DB.h5"
daily_V1 = Path('..','CharModelDev','CharModel-v1','daily.h5')
daily_V2 = Path('..','CharModelDev','CharModel-v2','daily.h5')

#Set Processor to Run computations in
print(tf.config.list_physical_devices(device_type=None))
tf.config.optimizer.set_jit(True)
gpus = tf.config.list_physical_devices('XLA_CPU')
if gpus:
  # Restrict TensorFlow to only use some XLA_CPU
    try:
        tf.config.experimental.set_visible_devices(gpus[:], 'XLA_CPU')
        logical_gpus = tf.config.experimental.list_logical_devices('XLA_CPU')
        print(len(gpus), "Physical GPU,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
    # Visible devices must be set at program startup
        print(e)

#Load the models and accesories
with tf.device(tf.config.experimental.list_logical_devices()[1]):
    daily_V1 = tf.keras.models.load_model(daily_V1, compile=False)
    HeNormal = tf.keras.initializers.he_normal()
    daily_V2 = tf.keras.models.load_model(daily_V2, custom_objects={'HeNormal': HeNormal},compile=False)


def predict_news():
    with pd.HDFStore(DATA_PATH) as store:
        #check max date of prediction to run or kill
        df = store['predictions/news/daily'].sort_index()
        max_date = df.index.get_level_values(0).max()
    with pd.HDFStore(news_db, mode = 'r+') as store:
        final_df = pd.DataFrame()
        if datetime.date.today().isoweekday() == 5: predict_date = (datetime.datetime.now() + datetime.timedelta(3)).strftime('%Y-%m-%d')
        else: predict_date = (datetime.datetime.now() + datetime.timedelta(1)).strftime('%Y-%m-%d')
        while True:
            if pd.to_datetime(max_date).strftime('%Y-%m-%d') != predict_date:
                print('Predicting for %s news headlines!' % (predict_date))
                for i in tqdm(store.keys()):
                    df = store[i]
                    today = (datetime.datetime.now(timezone('US/Eastern'))).strftime('%Y-%m-%d')
                    news_today = df.loc[df.loc[:, 'versionCreated'].apply(lambda x: x.strftime('%Y-%m-%d')) == today]
                    news_today = news_today[~news_today.text.duplicated()]
                    if len(news_today) > 0:
                        sample = news_today.text.str.cat(sep=' ')
                        if len(sample) > 1000: sample = sample[:500] + "..." + sample[-500:]
                        else: pass   
                        temp_df = pd.DataFrame.from_dict({i.strip('/'): sample}, orient='index').rename(columns={0:'Headlines'})
                        final_df = final_df.append(temp_df)
                        final_df['date'] = predict_date
                        final_df = final_df[~final_df.Headlines.duplicated()]
                    else: pass
                final_df['Headlines'].replace('', np.nan, inplace=True)
                final_df['News Date'] = today
                final_df.dropna(subset=['Headlines'], inplace=True)
                final_df = final_df.reset_index().rename(columns={'index':'ticker'})
                final_df = final_df.set_index((['date', 'ticker'])).sort_index(level = 0, sort_remaining=0)
                print('Data has been loaded!\nPredicting.....')
                memory()
                X = encode2bytes(final_df.Headlines.apply(lambda x: '<s>' + x + '<\s'))
                X = pad_sequences(X, maxlen =  max(map(len, X)), padding = 'post', truncating='post')
                memory()
                predictions = daily_V1.predict(X)
                print('Model 1 Done!')
                X_2 = [i.encode('utf-8') for i in final_df.Headlines.apply(lambda x: '<s>' + x + '<\s')] # encode
                tokenizer = tokenize() #tokenize
                X_2 = tokenizer.texts_to_sequences(X_2)    #pad
                X_2 = pad_sequences(X_2, maxlen =  max(map(len, X_2)), padding = 'post', truncating='post') #pad
                predictions2 = daily_V2.predict(X_2)    #predict
                memory()
                print('Model 2 Done!')
                final_df['Headlines'] = final_df['Headlines'].apply(lambda x: extract_end(x, 450)) #limit to 1000
                final_df['Predictions_V1'] = np.squeeze(predictions)
                final_df['Predictions_V2'] = np.squeeze(predictions2)
                final_df['BUY_V1'] = np.squeeze((predictions > 0.5).astype("int32"))
                final_df['BUY_V2'] = np.squeeze((predictions2 > 0.5).astype("int32"))
                final_df = final_df.round({'Predictions_V1': 5, 'Predictions_V2': 5})
                final_df['News Date'] = pd.to_datetime(final_df['News Date'])
                final_df = final_df.astype({'Predictions_V1': 'float32', 'Predictions_V2': 'float32', 'BUY_V1': 'int32', 'BUY_V2': 'int32'})
                new_tuples = final_df.index.map(lambda x: (pd.to_datetime(x[0]), x[1]))
                final_df.index = pd.MultiIndex.from_tuples(new_tuples, names=["date", "ticker"])
                with pd.HDFStore(DATA_PATH) as store:
                    store.put('predictions/news/daily', final_df,  encoding = 'UTF-8',format = 'table',append = True,
                              min_itemsize={'Headlines': 2000})
                print('++++++++++++++++ALL DONE!++++++++++++++++++++')
                print('Upload Completed on:', datetime.datetime.now(timezone('US/Eastern')).strftime('%Y-%m-%dT%H:%M:%S'))
                break
            else:
                print('Predictions are Up to Date!')
                print('System will exit now!')
                break

if __name__ == '__main__':
    predict_news()
    send_email()
    sys.exit('ALL DONE!')


