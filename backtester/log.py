import config
from Trade import Trade
import os


def clear_log():
    if os.path.exists(config.LOG_FILE):
        open(config.LOG_FILE, 'w').close()

def log_new_trade(trade:Trade):
    tp = "N/A" if trade.tp is None else f"{trade.tp:.5f}"
    sl = "N/A" if trade.sl is None else f"{trade.sl:.5f}"
    with open(config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"=> {trade.opening_date} - {trade.direction} trade ouvert ({trade.dealId})"
                f"- entrée : {trade.level:.5f}, TP : {tp}, SL : {sl}\n")

def log_update_trade(date, trade:Trade):
    with open(config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{date} - Trade {trade.dealId} mis à jour :"
                f" SL modifié à {trade.sl}\n")

def log_closed_trade(trade:Trade):
    tp = "N/A" if trade.tp is None else f"{trade.tp:.5f}"
    sl = "N/A" if trade.sl is None else f"{trade.sl:.5f}"
    with open(config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"<= {trade.closing_date} - Trade {trade.dealId} fermé "
                f"({trade.closing_origin} hit à {trade.closing_level:.5f}), "
                f"Dernier TP : {tp}, profit {trade.profit:.1f}\n")

