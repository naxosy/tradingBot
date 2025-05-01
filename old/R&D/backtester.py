import pandas as pd
import ta
from graphics import build_plot
from engine_old import apply_strat_to_df

# constants
max_candles = 2000

# PARAMÈTRES
csv_data_filename = "../eurusd_m1_6000.csv"
df = pd.read_csv(csv_data_filename)
# Ajout des EMAs
df['ema_5'] = ta.trend.EMAIndicator(close=df['bid_Close'], window=5).ema_indicator()
df['ema_13'] = ta.trend.EMAIndicator(close=df['bid_Close'], window=13).ema_indicator()
df.dropna(subset=['ema_5', 'ema_13'], inplace=True)
# Fenêtrage
#df.drop( df[ (df.index < (6000-max_candles+450))].index, inplace=True)

#df.drop( df[ (df.index < (6000-max_candles))].index, inplace=True)

# Conversion de la date
df['DateTime'] = pd.to_datetime(df['DateTime'])
df.set_index('DateTime', inplace=True)

# Trades simulation
profit = apply_strat_to_df(df)
print(f"Total profit :{profit}")

#Building graph
build_plot(df)
