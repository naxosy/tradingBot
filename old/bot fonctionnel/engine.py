import pandas as pd
from v3.Trade import Trade
from typing import List
import ta


def calc_EMA(df):
    bid_close_series = df[('bid', 'Close')]
    # Calcul des EMA
    bid_ema5 = ta.trend.ema_indicator(close=bid_close_series, window=5)
    bid_ema13 = ta.trend.ema_indicator(close=bid_close_series, window=13)
    # Insertion des bid_ema dans df
    df[('bid', 'bid_ema_5')] = bid_ema5
    df[('bid', 'bid_ema_13')] = bid_ema13
    
    ask_close_series = df[('ask', 'Close')]
    # Calcul des EMA
    ask_ema5 = ta.trend.ema_indicator(close=ask_close_series, window=5)
    ask_ema13 = ta.trend.ema_indicator(close=ask_close_series, window=13)
    # Insertion des ask_ema dans df
    df[('ask', 'ask_ema_5')] = ask_ema5
    df[('ask', 'ask_ema_13')] = ask_ema13
    return df

def check_for_signal(df : pd.DataFrame):
    new_trade = None

    # checking for LONG trade signal
    last_price = df.iloc[-2][('ask', 'Close')]
    last_ema_5 = df.iloc[-2][('ask', 'ask_ema_5')]
    last_ema_13 = df.iloc[-2][('ask', 'ask_ema_13')]

    ema_5 = df.iloc[-1][('ask', 'ask_ema_5')]
    ema_13 = df.iloc[-1][('ask', 'ask_ema_13')]

    if last_ema_5 < last_ema_13 and ema_5 > ema_13:
        price = df.iloc[-1][('ask', 'Close')]
        sl = last_ema_5
        tp = price + (price - sl) * 3
        new_trade = Trade("LONG", sl, tp, df.index[-1], None, price, None)

    # checking for SHORT trade signal
    last_price = df.iloc[-2][('bid', 'Close')]
    last_ema_5 = df.iloc[-2][('bid', 'bid_ema_5')]
    last_ema_13 = df.iloc[-2][('bid', 'bid_ema_13')]

    ema_5 = df.iloc[-1][('bid', 'bid_ema_5')]
    ema_13 = df.iloc[-1][('bid', 'bid_ema_13')]

    if last_ema_5 > last_ema_13 and ema_5 < ema_13:
        price = df.iloc[-1][('bid', 'Close')]
        sl = last_ema_5
        tp = price - (sl - price) * 3
        new_trade = Trade("SHORT", sl, tp, df.index[-1], None, price, None)

    return new_trade

def update_trades(raw_df:pd.DataFrame, trade_list:List[Trade]):
    df = calc_EMA(raw_df)
    # On vérifie si il y a des trades à fermer
    # Si oui on les ferme et on met à jour trade_list
    # Si non on update le SL
    for trade in trade_list[:] : #boucle sur une copie de la liste pour pouvoir modifier l'originale au cours de l'itération
        closed = trade.update(df.iloc[-1])
        if closed:
            trade_list.remove(trade)

    # On vérifie s'il y a des trades à ouvrir
    new_trade = check_for_signal(df)
    # Si oui on les ouvre et on les stocke dans trade_list
    if new_trade:
        new_trade.open()
        trade_list.append(new_trade)
    return trade_list
