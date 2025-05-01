import time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import query_IG_backtest as query_IG
tick = 1

import engine
from plot import build_plot

# Récupération des 30 bougies initiales (taille dans query_IG)
df = query_IG.fetch_initial_candles(50)
trade_list = []

build_plot(df, "candle")

while(True):
    # Récupération de la dernière bougie
    input("Appuyer sur entrée pour continuer ... ")
    df = query_IG.update_candles(df)

    # Verbose timer
    print(f"Timestamp {df.index[-1]}")

    # On vérifie si on doit fermer ou ouvrir des trades
    engine.update_trades(df, trade_list)

    time.sleep(tick)







