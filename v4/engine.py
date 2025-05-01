import ta
import pandas as pd
import IGQuery, config
from typing import List
from Trade import Trade

def open_position_if_signal(df: pd.DataFrame, current_trades:List[Trade]):

    # ===================== Change here to switch between opening strats

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

    if last_ema_5 < last_ema_13 and ema_5 > ema_13:  # BUY signal
        new_trade = Trade("BUY", config.DEFAULT_POS_SIZE, price, date)

    # Check for SELL trades
    last_ema_5 = last['bid']['ema_5']
    last_ema_13 = last['bid']['ema_13']
    ema_5 = current['bid']['ema_5']
    ema_13 = current['bid']['ema_13']
    price = current['bid']['Close']

    if last_ema_5 > last_ema_13 and ema_5 < ema_13:  # SELL signal
        new_trade = Trade("SELL", config.DEFAULT_POS_SIZE, price, date)

    # ======================================================================

    if not new_trade is None:
        response = IGQuery.open_position(new_trade)
        current_trades.append(new_trade)

    return new_trade

def update_current_positions(df: pd.DataFrame, current_trades:List[Trade],
                             closed_trades:List[Trade]):

    date = df.index[-1]
    for trade in current_trades[:]:
        ema_5_ask = df.iloc[-1]['ask']['ema_5']
        ema_13_ask = df.iloc[-1]['ask']['ema_13']
        ema_5_bid = df.iloc[-1]['bid']['ema_5']
        ema_13_bid = df.iloc[-1]['bid']['ema_13']
        closing_ask = df.iloc[-1]['ask']['Close']
        closing_bid = df.iloc[-1]['bid']['Close']

        if trade.direction == "BUY" and ema_5_ask <= ema_13_ask :
            print("pong")
            trade.close(date, closing_ask, "STRAT")
            current_trades.remove(trade)
            closed_trades.append(trade)
            IGQuery.close_position(trade)

        if trade.direction == "SELL" and ema_5_bid >= ema_13_bid:
            print("pang")
            trade.close(date, closing_bid, "STRAT")
            current_trades.remove(trade)
            closed_trades.append(trade)
            IGQuery.close_position(trade)

    return current_trades, closed_trades