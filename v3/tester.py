import pickle
import sys
from pprint import pprint
from Trade import Trade
fichier = r"C:\Users\Flo\PycharmProjects\tradingBot\v3\open_trades.pkl"

def read_open_trades() :
    try:
        with open(fichier, "rb") as f:
            data = pickle.load(f)
            print(f"✅ Contenu de '{fichier}' :\n")
            pprint(data)
    except FileNotFoundError:
        print(f"❌ Le fichier '{fichier}' est introuvable.")
    except Exception as e:
        print(f"❌ Erreur lors de la lecture : {e}")

def clear_open_trades(file_path="open_trades.pkl"):
    empty_trades = {}
    with open(file_path, "wb") as f:
        pickle.dump(empty_trades, f)
    print(f"✅ '{file_path}' a été vidé.")

def clear_order_log(file_path="orders.log"):
    with open(file_path, "w", encoding="utf-8") as f:
        f.truncate(0)
    print(f"✅ '{file_path}' a été vidé.")

clear_open_trades()
clear_order_log()