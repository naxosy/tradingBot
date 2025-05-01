import time
import server, engine
import log
from typing import List
from Trade import Trade

def print_current_candle(df):
    c = df.iloc[-1]['ask']
    date = df.index[-1].strftime("%d/%m/%Y - %H:%M")
    print(f"-------------------------")
    print(f"Bougie actuelle : {date}")
    print(f"High {c['High']:.5f}, Low {c['Low']:.5f}, Open {c['Open']:.5f}, Close {c['Close']:.5f}")

def print_results(trades:List[Trade]):
    print("Fin des données atteinte, fermeture de l'application.")
    total_profit = 0
    for trade in trades:
        total_profit += trade.profit
    print(f"Trades fermés : {len(closed_trades)}. Profit total : {total_profit:.1f} pips")
    exit()

log.clear_log()
df = server.fetch_initial_candles()
df = engine.calc_EMA(df)

current_trades = []
closed_trades = []

while(True):

    print_current_candle(df)
    server.check_for_closed_trades(df, current_trades, closed_trades) # mime l'action du serveur/ ferme selon les SL/TP
    engine.update_trades(df, current_trades, closed_trades) # update les trades existant
    engine.process_new_trades(df, current_trades) # cherche de nouveaux trades et les crée
    df = server.update_candles(df)
    if df is None :
        print_results(closed_trades)

    #time.sleep(0.1)