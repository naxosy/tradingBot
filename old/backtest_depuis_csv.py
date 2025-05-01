import pandas as pd
import ta
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# === Chargement des données depuis CSV ===
csv_filename = "eurusd_m1_6000.csv"
df = pd.read_csv(csv_filename)

if 'DateTime' in df.columns:
    df.rename(columns={'DateTime': 'timestamp'}, inplace=True)
else:
    print("⚠️ La colonne 'DateTime' n'existe pas dans le CSV.")
    print("Colonnes disponibles :", df.columns.tolist())
    exit()

# === Calcul des indicateurs ===
df['rsi'] = ta.momentum.RSIIndicator(close=df['bid_Close'], window=14).rsi()
df['ema'] = ta.trend.EMAIndicator(close=df['bid_Close'], window=20).ema_indicator()
df['atr'] = ta.volatility.AverageTrueRange(
    high=df['bid_High'], low=df['bid_Low'], close=df['bid_Close'], window=14
).average_true_range()

# === Paramètres backtest ===
capital = 50000
risk_per_trade = 0.01
cooldown = 3
cooldown_counter = 0
last_trade_direction = None
balance = [capital]
trades = []

print("📊 Données prêtes :")
print(df[['timestamp', 'bid_Close', 'rsi', 'ema', 'atr']].dropna().head(10))
print(f"Nombre de lignes avec tous les indicateurs valides : {df.dropna().shape[0]}")

# === Boucle sur les bougies ===
for i in range(len(df) - 1):
    if cooldown_counter > 0:
        cooldown_counter -= 1
        continue

    row = df.iloc[i]
    next_row = df.iloc[i + 1]

    price = row['bid_Close']
    rsi = row['rsi']
    ema = row['ema']
    atr = row['atr']

    if np.isnan(rsi) or np.isnan(ema) or np.isnan(atr):
        continue

    direction = None
    entry_price = price

    if rsi < 30 and price > ema and last_trade_direction != "BUY":
        print(f"{row['timestamp']} | 📈 SIGNAL BUY : RSI={rsi:.2f}, Price={price:.5f}, EMA={ema:.5f}")
        direction = "BUY"
        stop_loss = entry_price - atr
        take_profit = entry_price + 1.5 * atr
    elif rsi > 70 and price < ema and last_trade_direction != "SELL":
        print(f"{row['timestamp']} | 📉 SIGNAL SELL : RSI={rsi:.2f}, Price={price:.5f}, EMA={ema:.5f}")
        direction = "SELL"
        stop_loss = entry_price + atr
        take_profit = entry_price - 1.5 * atr
    else:
        continue

    exit_price = next_row['bid_Close']
    hit_tp = (exit_price >= take_profit) if direction == "BUY" else (exit_price <= take_profit)
    hit_sl = (exit_price <= stop_loss) if direction == "BUY" else (exit_price >= stop_loss)

    current_capital = balance[-1]
    risk_amount = current_capital * risk_per_trade
    pip_value = 10
    sl_pips = abs(entry_price - stop_loss) * 10000
    lot_size = risk_amount / (sl_pips * pip_value) if sl_pips > 0 else 0

    if hit_tp:
        result = (take_profit - entry_price) * lot_size * pip_value if direction == "BUY" else (entry_price - take_profit) * lot_size * pip_value
    elif hit_sl:
        result = -risk_amount
    else:
        result = 0

    new_balance = balance[-1] + result
    balance.append(new_balance)
    last_trade_direction = direction
    cooldown_counter = cooldown

    trades.append({
        'timestamp': row['timestamp'],
        'direction': direction,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'lot_size': lot_size,
        'result': result,
        'balance': new_balance
    })
    print(f"✅ Trade ajouté | Direction: {direction} | Entry: {entry_price:.5f} | Exit: {exit_price:.5f} | Résultat: {result:.2f} €")

# === Résultats ===
trades_df = pd.DataFrame(trades)
trades_df.to_csv("backtest_ig_csv_results.csv", index=False)
print("✅ Backtest terminé. Résultats enregistrés dans 'backtest_ig_csv_results.csv'")
