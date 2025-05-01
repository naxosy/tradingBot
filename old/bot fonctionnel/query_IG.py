from trading_ig import IGService
import pandas as pd

username =
password =
api_key =
acc_type = "demo"
account_id =

epic = "CS.D.EURUSD.MINI.IP"
resolution = "1Min"
max_points = 30

def fetch_initial_candles():
    # === Récupération initiale des bougies ===
    ig_service = IGService(username, password, api_key, acc_type, acc_number=account_id)
    ig_service.create_session(version='3')

    print("📥 Téléchargement initial des bougies...")
    response = ig_service.fetch_historical_prices_by_epic_and_num_points(
        epic=epic,
        resolution=resolution,
        numpoints=max_points
    )

    return response['prices']

def update_candles(df):
    # === Récupération initiale des bougies ===
    ig_service = IGService(username, password, api_key, acc_type, acc_number=account_id)
    ig_service.create_session(version='3')

    print("📥 Téléchargement initial des bougies...")
    response = ig_service.fetch_historical_prices_by_epic_and_num_points(
        epic=epic,
        resolution=resolution,
        numpoints=1
    )
    new_row = response['prices']

    timestamp = new_row.index[0]
    if timestamp not in df.index:
        df = pd.concat([df, new_row])
        print(f"✅ Nouvelle ligne ajoutée : {timestamp}")
    else:
        print(f"⚠️ Ligne ignorée (doublon) : {timestamp}")

    return df