import pandas as pd
from typing import List
from Trade import Trade
import config
import log
import engine
# === Variables internes ===
candle_df = pd.read_pickle(config.CANDLE_FILE)
candle_pointer = config.BUFFER_SIZE
candle_df = engine.calc_EMA(candle_df)

def fetch_initial_candles() -> pd.DataFrame | None:
    global candle_pointer
    df = candle_df.iloc[:candle_pointer].copy()
    return df

def update_candles(df:pd.DataFrame) -> pd.DataFrame | None :
    #penser à recalculer les EMA

    global candle_pointer
    if candle_pointer >= len(candle_df):
        print("Fin des données de backtest atteinte.")
        return None

    new_row = candle_df.iloc[[candle_pointer]]  # [[...]] pour conserver DataFrame
    candle_pointer += 1

    timestamp = new_row.index[0]
    if timestamp not in df.index:
        df = pd.concat([df, new_row])
        df = df.iloc[1:]
    else:
        print(f"⚠️ Ligne ignorée (doublon) : {timestamp}")
    return df

def check_for_closed_trades(df:pd.DataFrame, current_trades:List[Trade], closed_trades:List[Trade]) -> List[Trade]:

    date = df.index[-1]
    new_candle = df.iloc[-1]

    for trade in current_trades[:]:
        if trade.sl is None and trade.tp is None:
            continue
        match trade.direction:
            case "BUY":
                if trade.tp < new_candle['ask']['High'] :
                    trade.close(date, trade.tp, "TP")
                if trade.sl > new_candle['ask']['Low'] :
                    trade.close(date, trade.sl, "SL")
            case "SELL":
                if trade.tp > new_candle['bid']['Low']:
                    trade.close(date, trade.tp, "TP")
                if trade.sl < new_candle['ask']['High']:
                    trade.close(date, trade.sl, "SL")
        if trade.closed:
            log.log_closed_trade(trade)
            closed_trades.append(trade)
            current_trades.remove(trade)

    return current_trades