import pandas as pd
import pickle
from datetime import datetime, timedelta, timezone
from trading_ig import IGService

USERNAME = "naxosy_demo"
PASSWORD = "$$deR69me5"
API_KEY = "9744350976c271ef25e9c241338c1695f23a1e91"
ACC_TYPE = "demo"
ACC_ID = "Z5YW5L"

# ⚙️ Paramètres IG
ig_service = IGService(USERNAME, PASSWORD, API_KEY, ACC_TYPE, acc_number=ACC_ID)
ig_service.create_session(version='3')

# ⚙️ Paramètres du téléchargement
epic = 'CS.D.EURUSD.CFD.IP'
resolution = '1Min'
n_bars = 1200

# 📅 Calcul de la période
end_date = datetime.now(timezone.utc)
start_date = end_date - timedelta(minutes=n_bars)

# 📅 Conversion en chaînes ISO 8601
start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

# 📥 Téléchargement
response = ig_service.fetch_historical_prices_by_epic_and_num_points(
    epic=epic,
    resolution=resolution,
    numpoints=n_bars
)

df = response['prices']

# 💾 Sauvegarde dans un fichier .pkl
with open("21avril-23avril_soir.pkl", "wb") as f:
    pickle.dump(df, f)

print("✅ Données téléchargées et sauvegardées dans 21avril-23avril_soir.pkl")
