import time
import engine, IGQuery, config, utils
from typing import List
from Trade import Trade
from datetime import datetime

def print_current_candle(df):
    c = df.iloc[-1]['ask']
    last = df.iloc[-2]['ask']
    date = df.index[-1].strftime("%d/%m/%Y - %H:%M")
    print(f"-------------------------")
    print(f"Dernière bougie : {date}")
    print(f"High {c['High']:.5f}, Low {c['Low']:.5f}, Open {c['Open']:.5f}, Close {c['Close']:.5f}")
    print(f"(ask) EMA 5 : {c['ema_5']:.5f}, EMA 13 : {c['ema_13']:.5f}, "
          f"Last EMA 5 : {last['ema_5']:.5f}, Last EMA 13 : {last['ema_13']} ")

df = IGQuery.fetch_initial_candles()
df = utils.calc_EMA(df)
pkl_filename = utils.init_pickle(df)

current_trades = []
closed_trades = []

# Phasing the loop
utils.set_loop_phase()

while True:
    df = IGQuery.update_candles(df)
    print_current_candle(df)
    utils.update_pkl(df, pkl_filename)
    current_trades = IGQuery.fetch_current_trades()
    current_trades, closed_trades = engine.update_current_positions(df,
                                                                  current_trades,
                                           closed_trades)
    # update
    # les
    # trades existant
    new_trade = engine.open_position_if_signal(df, current_trades)


    time.sleep(60)