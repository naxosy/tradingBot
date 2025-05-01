import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from ta.trend import ema_indicator
from mplfinance.original_flavor import candlestick_ohlc
from engine import calc_EMA
import config

# Chargement des données
df = pd.read_pickle("21avril-23avril_soir.pkl")
df = calc_EMA(df)  # EMA déjà calculées sur l'historique complet dans cette fonction

# Récupération des données ask uniquement
ask_df = df['ask'].copy()

# Utilisation directe des EMA déjà présentes dans df
ask_df['EMA_5'] = df[('ask', 'ema_5')]
ask_df['EMA_13'] = df[('ask', 'ema_13')]

# === Préparation des données OHLC ===
ohlc = ask_df[['Open', 'High', 'Low', 'Close']].copy()
ohlc['Date'] = df.index
ohlc.reset_index(drop=True, inplace=True)
ohlc['Date'] = mdates.date2num(ohlc['Date'])

# === Création du graphique ===
fig, ax = plt.subplots(figsize=(14, 7))

# Chandeliers
candlestick_ohlc(ax, ohlc[['Date', 'Open', 'High', 'Low', 'Close']].values,
                 width=0.0005, colorup='green', colordown='red')

# Tracé des EMA (déjà calculées dans le backtest)
ax.plot(ohlc['Date'], ask_df['EMA_5'], label='EMA 5', linewidth=1.0)
ax.plot(ohlc['Date'], ask_df['EMA_13'], label='EMA 13', linewidth=1.3)

# Mise en forme
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%M'))
plt.xticks(rotation=25)
plt.xlabel("Temps")
plt.ylabel("Prix (Ask)")
plt.title("Graphique en chandeliers - EMA 5 & 13 (full historique)")
plt.legend()
plt.tight_layout()
plt.grid(True)
plt.show()
