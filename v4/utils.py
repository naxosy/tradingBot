import pandas as pd
import ta
from datetime import datetime
import time
from tqdm import tqdm
import config

def init_pickle(df:pd.DataFrame):
    pkl_filename = (f"{config.INSTRUMENT}_"
            f"{config.RES}.{datetime.now():%d.%m.%Y_%H-%M-%S}.pkl")
    df.to_pickle(pkl_filename)
    return pkl_filename

def update_pkl(df:pd.DataFrame, filename:str):
    up_df = pd.read_pickle(filename)
    last_row = df.tail(1)
    up_df = pd.concat([up_df, last_row])
    up_df.to_pickle(filename)

def calc_EMA(df: pd.DataFrame):

    bid_close_series = df[('bid', 'Close')]
    # Calcul des EMA
    bid_ema5 = ta.trend.ema_indicator(close=bid_close_series, window=5).round(5)
    bid_ema13 = ta.trend.ema_indicator(close=bid_close_series, window=13).round(5)
    # Insertion des bid_ema dans df
    df[('bid', 'ema_5')] = bid_ema5
    df[('bid', 'ema_13')] = bid_ema13

    ask_close_series = df[('ask', 'Close')]
    # Calcul des EMA
    ask_ema5 = ta.trend.ema_indicator(close=ask_close_series, window=5).round(5)
    ask_ema13 = ta.trend.ema_indicator(close=ask_close_series, window=13).round(5)
    # Insertion des ask_ema dans df
    df[('ask', 'ema_5')] = ask_ema5
    df[('ask', 'ema_13')] = ask_ema13
    return df

import pandas as pd

def compute_heikin_ashi_from_df(df, source='bid'):
    """
    Calcule les bougies Heikin-Ashi à partir des colonnes multi-indexées (type de prix, OHLC)
    :param df: DataFrame avec colonnes MultiIndex (ex: df[('bid', 'Open')])
    :param source: 'bid', 'ask' ou 'last'
    :return: DataFrame avec les colonnes Open, High, Low, Close en Heikin-Ashi
    """
    if source not in df.columns.levels[0]:
        raise ValueError(f"'{source}' n'existe pas dans les types de prix disponibles : {df.columns.levels[0].tolist()}")

    # Extraire les colonnes OHLC pour le type de prix choisi
    ohlc = df[source][['Open', 'High', 'Low', 'Close']].copy()

    ha = pd.DataFrame(index=ohlc.index, columns=['Open', 'High', 'Low', 'Close'])

    # HA-Close = moyenne des 4 prix
    ha['Close'] = (ohlc['Open'] + ohlc['High'] + ohlc['Low'] + ohlc['Close']) / 4

    # Initialisation de HA-Open avec le vrai Open
    ha.iloc[0, ha.columns.get_loc('Open')] = ohlc['Open'].iloc[0]

    # Calcul itératif de HA-Open
    for i in range(1, len(ohlc)):
        ha.iloc[i, ha.columns.get_loc('Open')] = (
            ha['Open'].iloc[i - 1] + ha['Close'].iloc[i - 1]
        ) / 2

    # HA-High et HA-Low
    ha['High'] = pd.concat([ohlc['High'], ha['Open'], ha['Close']], axis=1).max(axis=1)
    ha['Low']  = pd.concat([ohlc['Low'],  ha['Open'], ha['Close']], axis=1).min(axis=1)

    return ha



def set_loop_phase():

    waiting_time = 61 - int(datetime.now().strftime('%S'))

    for i in tqdm(range(waiting_time), desc="Phasing main loop, please "
                                            "wait ", ncols=100):
        time.sleep(1)
    print(f"Launching main loop at {datetime.now().strftime('%H:%M:%S')}")


