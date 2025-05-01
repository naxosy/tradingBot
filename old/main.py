from trading_ig import IGService
import logging
from datetime import datetime, timedelta
import pandas as pd
import ta
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def currentState(candle) :
    prices = {'p':candle['bid_Close'], '5':candle['ema_5'], '20':candle['ema_20']}
    result = ''.join(key for key, value in sorted(prices.items(), key=lambda item: item[1]))
    return result

logging.basicConfig(level=logging.INFO)

now = datetime.now()
from_date = now - timedelta(hours=10)

ig_service = IGService(username, password, api_key, acc_type, acc_number=account_id)
ig_service.create_session(version='3')
eur_usd_epic = "CS.D.EURUSD.MINI.IP"

epic = 'CS.D.EURUSD.MINI.IP'
resolution = '1Min'
num_points = 800
query = ig_service.fetch_historical_prices_by_epic_and_num_points(epic, resolution, num_points)
df = query['prices']

df.columns = ['_'.join(col).strip() for col in df.columns]
df.reset_index(drop=True, inplace=True)

if 'bid_Close' not in df.columns:
    raise ValueError("La colonne 'bid_Close' n'existe pas. Vérifie les noms de colonnes : ", df.columns.tolist())

df['ema_5'] = ta.trend.EMAIndicator(close=df['bid_Close'], window=5).ema_indicator()
df['ema_20'] = ta.trend.EMAIndicator(close=df['bid_Close'], window=20).ema_indicator()

state = None

last_ema_5, last_ema_20, last_price = None, None, None
buying, selling = False, False
buying_price, selling_price, profit = 0, 0, 0
pip_value = 0.0001
last_state = None
total_profit = 0

for index,candle in df.iterrows():

    if np.isnan(candle['ema_20']):
        continue

    if last_ema_5 == None or last_ema_20 == None or last_price == None :
        last_ema_5 = candle['ema_5']
        last_ema_20 = candle['ema_20']
        last_price = candle['bid_Close']
        continue

    if last_ema_20 > last_price and candle['bid_Close'] > candle['ema_20'] :
        buying = True
        buying_price = candle['bid_Close']
        print(f"Minute {index} : opening long position at price {candle['bid_Close']:.4f}")

    if buying and (candle['bid_Close'] < candle['ema_5'] or candle['bid_Close'] < candle['ema_20']) :
        buying = False
        selling_price = candle['bid_Close']
        profit = (selling_price - buying_price) / pip_value
        total_profit += profit
        print(f"Minute {index} : closing long position at price {candle['bid_Close']:.4f} - Profit : {profit} pips")

    if last_ema_20 < last_price and candle['bid_Close'] < candle['ema_20']:
        selling = True
        selling_price = candle['bid_Close']
        print(f"Minute {index} : opening short position at price {candle['bid_Close']:.4f}")

    if selling and (candle['bid_Close'] > candle['ema_5'] or candle['bid_Close'] > candle['ema_20']):
        selling = False
        buying_price = candle['bid_Close']
        profit = (selling_price - buying_price) / pip_value
        total_profit += profit
        print(f"Minute {index} : closing short position at price {candle['bid_Close']:.4f} - Profit : {profit} pips")

    last_ema_5 = candle['ema_5']
    last_ema_20 = candle['ema_20']
    last_price = candle['bid_Close']

print(f"Total profit : {total_profit:.1f} pips")

plt.figure(figsize=(12, 6))

# Courbe du prix
plt.plot(df['bid_Close'], label='Prix (bid close)', linewidth=1.5)

# EMAs
plt.plot(df['ema_5'], label='EMA 5', linestyle='--')
plt.plot(df['ema_20'], label='EMA 20', linestyle='-.')

# Titre et légende
plt.title("EUR/USD - EMA 5 vs EMA 20 (bougies M1)")
plt.xlabel("Index des bougies (minutes)")
plt.ylabel("Prix")
plt.legend()

# Quadrillage affiné
plt.grid(
    which='both',      # grille principale et secondaire
    axis='both',       # sur x et y
    color='gray',
    linestyle='--',
    linewidth=0.5,
    alpha=0.5
)

# Ticks plus fréquents (si tu veux aller plus loin)
plt.minorticks_on()  # Active les ticks secondaires
plt.tick_params(which='major', length=6)
plt.tick_params(which='minor', length=3, color='lightgray')

# Layout propre
plt.tight_layout()
plt.show()














