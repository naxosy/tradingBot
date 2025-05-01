import pandas as pd

backtest_path = r"C:\Users\Flo\PycharmProjects\tradingBot\backtesting.pkl"


# Charger toutes les bougies depuis le pickle une seule fois
full_data = pd.read_pickle(backtest_path)

# Fonction de démarrage : prendre les 30 premières
def fetch_initial_candles(n=30):
    return full_data.iloc[:n].copy()

current_index = 30
def update_candles(df):
    global current_index
    if current_index < len(full_data):
        # Supprimer la première ligne
        df = df.iloc[1:].copy()
        # Ajouter la ligne suivante depuis full_data
        next_row = full_data.iloc[[current_index]]  # gardez le double [ [i] ] pour conserver la structure DataFrame
        df = pd.concat([df, next_row])
        current_index += 1
    else:
        print("⛔ Plus de bougies disponibles.")
    return df