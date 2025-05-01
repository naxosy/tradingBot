
from datetime import datetime, timedelta
import pandas as pd
import ta
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# === Génération de données simulées (mock) ===
np.random.seed(42)
base_price = 1.1000
timestamps = [datetime.utcnow() - timedelta(minutes=2000 - i) for i in range(2000)]
prices = base_price + np.cumsum(np.random.normal(0, 0.0005, 2000))

df = pd.DataFrame({
    'timestamp': timestamps,
    'bid_Close': prices
})

# === Calcul des indicateurs ===
rsi_window = 14
ema_window = 20
df['rsi'] = ta.momentum.RSIIndicator(close=df['bid_Close'], window=rsi_window).rsi()
df['ema'] = ta.trend.EMAIndicator(close=df['bid_Close'], window=ema_window).ema_indicator()
df['atr'] = ta.volatility.AverageTrueRange(high=df['bid_Close'], low=df['bid_Close'], close=df['bid_Close'], window=14).average_true_range()

# === Paramètres backtest ===
capital = 50000
risk_per_trade = 0.01
cooldown = 3
cooldown_counter = 0
last_trade_direction = None
balance = [capital]
trades = []

# === Boucle sur les bougies historiques ===
for i in range(20, len(df) - 1):
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
    stop_loss = None
    take_profit = None
    result = 0

    if rsi < 30 and price > ema and last_trade_direction != "BUY":
        direction = "BUY"
        stop_loss = entry_price - atr
        take_profit = entry_price + 1.5 * atr
    elif rsi > 70 and price < ema and last_trade_direction != "SELL":
        direction = "SELL"
        stop_loss = entry_price + atr
        take_profit = entry_price - 1.5 * atr

    if direction:
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

# === Résultats ===
trades_df = pd.DataFrame(trades)
trades_df.to_csv("backtest_mock_results.csv", index=False)
print("✅ Résultats exportés dans 'backtest_mock_results.csv'")
