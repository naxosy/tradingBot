from trading_ig import IGService
import logging
from datetime import datetime, timedelta
import time
import pandas as pd
import ta
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

logging.basicConfig(level=logging.INFO)

ig_service = IGService(username, password, api_key, acc_type, acc_number=account_id)
ig_service.create_session(version='3')

epic = "CS.D.EURUSD.MINI.IP"
resolution = "1Min"
size = 1
rsi_window = 14
ema_window = 20
max_points = 100

# === Récupération initiale des bougies ===
print("📥 Téléchargement initial des bougies...")
response = ig_service.fetch_historical_prices_by_epic_and_num_points(
    epic=epic,
    resolution=resolution,
    numpoints=max_points
)

df = response['prices']
df.columns = ['_'.join(col).strip() for col in df.columns]
df.reset_index(drop=True, inplace=True)

# === Fonction de mise à jour avec nouvelle bougie ===
def update_data():
    global df

    response = ig_service.fetch_historical_prices_by_epic_and_num_points(
        epic=epic,
        resolution=resolution,
        numpoints=1
    )
    new_row = response['prices']
    new_row.columns = ['_'.join(col).strip() for col in new_row.columns]
    new_row.reset_index(drop=True, inplace=True)

    # Évite les doublons si on récupère la même minute
    if not new_row.equals(df.iloc[[-1]]):
        df = pd.concat([df, new_row], ignore_index=True).iloc[-max_points:]

# === Fonction d’envoi d’ordre réel ===
def send_order(direction):
    print(f"🚀 Envoi ordre {direction.upper()}")

    response = ig_service.create_open_position(
        currency_code='EUR',
        direction=direction,
        epic=epic,
        expiry='-',
        force_open=True,
        guaranteed_stop=False,
        level=None,
        limit_distance=10,  # take profit à 10 pips
        order_type='MARKET',
        quote_id=None,
        size=size,
        stop_distance=10,   # stop loss à 10 pips
        trailing_stop=False
    )

    deal_id = response.get('dealId', 'N/A')
    status = response.get('status', 'unknown')
    print(f"✅ Ordre {direction.upper()} envoyé | dealId: {deal_id} | status: {status}")

# === Boucle du bot ===
print("🤖 Bot scalping en cours...")
while True:
    try:
        update_data()

        # Calcul indicateurs
        df['rsi'] = ta.momentum.RSIIndicator(close=df['bid_Close'], window=rsi_window).rsi()
        df['ema'] = ta.trend.EMAIndicator(close=df['bid_Close'], window=ema_window).ema_indicator()

        last = df.iloc[-1]
        rsi = last['rsi']
        price = last['bid_Close']
        ema = last['ema']

        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Prix: {price:.5f} | RSI: {rsi:.2f} | EMA: {ema:.5f}")

        # Logique scalping avec confirmation EMA
        if rsi < 30 and price > ema:
            print("📈 Signal d'achat confirmé")
            send_order("BUY")
        elif rsi > 70 and price < ema:
            print("📉 Signal de vente confirmé")
            send_order("SELL")
        else:
            print("⏳ Aucun signal - attente...")

        time.sleep(60)  # respecter la limite IG (1 call/minute)

    except Exception as e:
        print("⚠️ Erreur :", e)
        time.sleep(30)














