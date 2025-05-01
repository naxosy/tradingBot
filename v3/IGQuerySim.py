import pandas as pd
import config
import logging
import pickle
import os
from datetime import datetime
from Order import Order
from Trade import Trade

logger = logging.getLogger(__name__)

# === Fichiers ===
CANDLE_FILE = "backtest_candles.pkl"
TRADES_FILE = r"C:\Users\Flo\PycharmProjects\tradingBot\v3\open_trades.pkl"
ORDER_LOG = "orders.log"

# === Variables internes ===
candle_df = pd.read_pickle(CANDLE_FILE)
candle_pointer = config.max_points if hasattr(config, 'max_points') else 15

# === Fonctions internes ===
def load_open_trades():
    if os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def save_open_trades(trades_dict):
    with open(TRADES_FILE, "wb") as f:
        pickle.dump(trades_dict, f)

def log_order(action, order):
    with open(ORDER_LOG, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%d/%m %H:%M")
        f.write(f"[{timestamp}] {action.upper()}: {order}\n")

# === Fonctions publiques ===
def fetch_initial_candles():
    global candle_pointer
    prices = candle_df.iloc[:candle_pointer]
    return prices

def update_candles(df):
    global candle_pointer
    if candle_pointer >= len(candle_df):
        logger.warning("Fin des données de backtest atteinte.")
        return df

    new_row = candle_df.iloc[[candle_pointer]]  # [[...]] pour conserver DataFrame
    candle_pointer += 1

    timestamp = new_row.index[0]
    if timestamp not in df.index:
        df = pd.concat([df, new_row])
        df = df.iloc[1:]
        logger.debug(f"✅ Nouvelle ligne ajoutée : {timestamp}")
    else:
        logger.debug(f"⚠️ Ligne ignorée (doublon) : {timestamp}")
    return df

def fetch_current_trades():
    logger.info("(SIM) Récupération des trades ouverts depuis le fichier .pkl")
    trades = load_open_trades()
    for deal_id, trade in trades.items():
        logger.info(f"(SIM) Trade simulé trouvé ouvert -> {trade}")
    return trades

def fetch_funds_summary():
    logger.debug("(SIM) Données de compte simulées envoyées.")
    accounts_data = [
        {
            'accountId': config.ACC_ID,
            'accountName': "CFD",
            'accountAlias': "SimAccount",
            'status': "ENABLED",
            'accountType': "CFD",
            'preferred': True,
            'currency': "EUR",
            'canTransferFrom': False,
            'canTransferTo': False,
            'available': 10000.0,
            'balance': 10000.0,
            'deposit': 0.0,
            'profitLoss': 0.0
        }
    ]
    accounts = pd.DataFrame(accounts_data)
    account = accounts[accounts["accountId"] == config.ACC_ID]
    return account.iloc[0].to_dict()

def open_position(order: Order):
    logger.info(f"(SIM) Ouverture de position simulée : {order}")
    log_order("open", order)

    trades = load_open_trades()
    deal_id = f"SIM-{len(trades)+1}"  # id fictif
    trade = Trade(
        order.direction,
        order.sl,
        order.tp,
        datetime.now(),
        None,
        0.0,
        None,
        order.size,
        "EUR/USD",
        config.EPIC
    )
    trades[deal_id] = trade
    #debug
    import pprint

    print("=== DEBUG: trades dict ===")
    pprint.pprint(trades)
    print("=== tentative de sauvegarde ===")

    try:
        save_open_trades(trades)
        print("✅ Sauvegarde OK")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")
    ###
    save_open_trades(trades)
    return {"status": "SUCCESS"}

def update_position(order: Order):
    logger.info(f"(SIM) Mise à jour de position simulée : {order}")
    log_order("update", order)

    trades = load_open_trades()
    if order.trade_id in trades:
        trade = trades[order.trade_id]
        trade.sl = order.sl
        trade.tp = order.tp
        save_open_trades(trades)
        return {"status": "SUCCESS"}
    else:
        logger.warning(f"(SIM) Trade {order.trade_id} non trouvé pour update.")
        return {"status": "FAILURE", "reason": "Trade not found"}

def calculate_position_size(amount: float, direction: str = 'BUY'):
    return config.DEFAULT_SIZE

def simulate_server_closing_trades(df, current_trades):
    candle=df.iloc[-1]
    for trade in current_trades.values():
        order = None
        match trade.kind :
            case "BUY":
                low = candle['ask']['Low']
                high = candle['ask']['High']
                if low <= trade.sl :
                    trade.close(trade.sl, df.index[-1], "SL")
                    order = Order("CLOSE", trade_id=trade.id, origin="SL")
                elif high >= trade.tp :
                    trade.close(trade.tp, df.index[-1], "TP")
                    order = Order("CLOSE", trade_id=trade.id, origin="TP")
            case "SELL":
                low = candle['bid']['Low']
                high = candle['bid']['High']
                if low <= trade.tp:
                    trade.close(trade.tp, df.index[-1], "TP")
                    order = Order("CLOSE", trade_id=trade.id, origin="TP")
                elif high >= trade.sl:
                    trade.close(trade.sl, df.index[-1], "SL")
                    order = Order("CLOSE", trade_id=trade.id, origin="SL")

        if order:
            logger.info(f"💥 Fermeture du trade {trade.id} par {order.origin} à {df.index[-1]}")
            log_order("close", order)

        open_trades = {k: v for k, v in current_trades.items() if not v.closed}
        save_open_trades(open_trades)
        return open_trades

