import logging
logger = logging.getLogger(__name__)

import ta
import pandas as pd
from Trade import Trade
from Order import Order
import IGQuery

import config

def tick(df, current_trades, account_status):
    #check_for_closed_trades(df, current_trades, account_status) ## todo (logs)
    df = calc_EMA(df)
    update_order = update_trades(df, current_trades, account_status)
    create_order = check_for_new_trades(df, current_trades, account_status)

    if update_order :
        logger.debug(f"Update order généré : {update_order}")
        process_order(update_order)

    if create_order :
        logger.debug(f"Open order généré : {create_order}")
        process_order(create_order)

    return None

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

def update_trades(df, current_trades, account_status):
    new_order = None
    if current_trades :
        if len(current_trades) > 1 :
            logger.error("ERREUR : plus d'un trade ouvert")
        else :
            deal_id, trade = next(iter(current_trades.items()))
            ema_13 = df.iloc[-1][('bid', 'bid_ema_13')] if trade.kind == "BUY" else df.iloc[-1][('ask', 'ask_ema_13')]
            new_order = Order("UPDATE", trade_id=deal_id, sl=ema_13, tp=trade.tp)

    return new_order

def check_for_new_trades(df, current_trades, account_status):
    new_order = None
    # BUY trades
    last_ema_5 = df.iloc[-2][('ask', 'ask_ema_5')]
    last_ema_13 = df.iloc[-2][('ask', 'ask_ema_13')]

    price = df.iloc[-1][('ask', 'Close')]
    ema_5 = df.iloc[-1][('ask', 'ask_ema_5')]
    ema_13 = df.iloc[-1][('ask', 'ask_ema_13')]

    if last_ema_5 < last_ema_13 and ema_5 > ema_13:
        sl = last_ema_13
        tp = price + (price - sl) * 3
        size_in_EUR = account_status['balance']*config.RISK
        size_in_lot = IGQuery.calculate_position_size(size_in_EUR, "BUY")
        new_order = Order("OPEN", size=size_in_lot, sl=sl, tp=tp, direction="BUY")

    # SELL trades
    last_ema_5 = df.iloc[-2][('bid', 'bid_ema_5')]
    last_ema_13 = df.iloc[-2][('bid', 'bid_ema_13')]

    price = df.iloc[-1][('bid', 'Close')]
    ema_5 = df.iloc[-1][('bid', 'bid_ema_5')]
    ema_13 = df.iloc[-1][('bid', 'bid_ema_13')]

    if last_ema_5 > last_ema_13 and ema_5 < ema_13:
        sl = last_ema_13
        tp = price + (price - sl) * 3
        size_in_EUR = account_status['balance']*config.RISK
        size_in_lot = IGQuery.calculate_position_size(size_in_EUR, "SELL")
        new_order = Order("OPEN", size=size_in_lot, sl=sl, tp=tp, direction="SELL")

    return new_order

def process_order(order : Order):
    match order.order_type:
        case "OPEN":
            IGQuery.open_position(order)
        case "UPDATE":
            IGQuery.update_position(order)

def print_last_candle(df:pd.DataFrame):
    c = df.iloc[-1]['ask']
    output = f"Dernière bougie récupérée (Achat/Ask) à {df.index[-1].strftime("%d/%m - %H:%M")} :\n"
    output += f"High {c['High']:.5f}, Low {c['Low']:.5f}, Open {c['Open']:.5f}, Close {c['Close']:.5f}"

    return output
