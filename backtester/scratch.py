import pickle
import pandas as pd
from engine import calc_EMA
data = pd.read_pickle(r"C:\Users\Flo\PycharmProjects\tradingBot\backtester\backtest_candles.pkl")

data = calc_EMA(data)

print(data.iloc[-1]['ask']['ema_5'])