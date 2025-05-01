import math
import pandas as pd
import ta
from typing import List
from Trade import Trade
import config
import log

def update_trades(df:pd.DataFrame, current_trades:List[Trade], closed_trades:List[Trade]) -> List[Trade]:
    updated_trade_list = []
    date = df.index[-1]
    for trade in current_trades[:]:
        ema_5_ask = df.iloc[-1]['ask']['ema_5']
        ema_13_ask = df.iloc[-1]['ask']['ema_13']
        ema_5_bid = df.iloc[-1]['bid']['ema_5']
        ema_13_bid = df.iloc[-1]['bid']['ema_13']
        closing_ask = df.iloc[-1]['ask']['Close']
        closing_bid = df.iloc[-1]['bid']['Close']

        if trade.direction == "BUY" and ema_5_ask <= ema_13_ask :
            trade.close(date, closing_ask, "STRAT")
            current_trades.remove(trade)
            closed_trades.append(trade)
            log.log_closed_trade(trade)

        if trade.direction == "SELL" and ema_5_bid >= ema_13_bid:
            trade.close(date, closing_bid, "STRAT")
            current_trades.remove(trade)
            closed_trades.append(trade)
            log.log_closed_trade(trade)

    return updated_trade_list

def process_new_trades(df:pd.DataFrame, current_trades:List[Trade]) -> List[Trade]:
    new_trade = None

    date = df.index[-1]
    current = df.iloc[-1]
    last = df.iloc[-2]

    # Check for BUY trades
    last_ema_5 = last['ask']['ema_5']
    last_ema_13 = last['ask']['ema_13']
    ema_5 = current['ask']['ema_5']
    ema_13 = current['ask']['ema_13']
    price = current['ask']['Close']

    print(f"For date {date} : Last EMA_5 : {last_ema_5:.5f} Last EMA_13 : {last_ema_13:.5f} - Current EMA 5"
          f": {ema_5:.6f} Current EMA_13 : {ema_13:.6f}")

    if last_ema_5 < last_ema_13 and ema_5 > ema_13: # BUY signal
        new_trade = Trade("BUY", config.SIZE, price, date)

        
    # Check for SELL trades
    last_ema_5 = last['bid']['ema_5']
    last_ema_13 = last['bid']['ema_13']
    ema_5 = current['bid']['ema_5']
    ema_13 = current['bid']['ema_13']
    price = current['bid']['Close']
        
    if last_ema_5 > last_ema_13 and ema_5 < ema_13 : # SELL signal
        new_trade = Trade("SELL", config.SIZE, price, date)

    if not new_trade is None:
        current_trades.append(new_trade)
        log.log_new_trade(new_trade)

    return current_trades


def calc_EMA(df):

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