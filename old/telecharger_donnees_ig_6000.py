
from trading_ig import IGService
import pandas as pd
from datetime import datetime
import logging

# === Connexion IG ===
username = "naxosy_demo"
password = "$$deR69me5"
api_key = "af500f4cc415bc83819895ebf3f96469bd1ec1b0"
acc_type = "demo"
account_id = "Z5YW5L"

logging.basicConfig(level=logging.INFO)

ig_service = IGService(username, password, api_key, acc_type, acc_number=account_id)
ig_service.create_session(version='3')

# === Paramètres de téléchargement ===
epic = "CS.D.EURUSD.MINI.IP"
resolution = "1Min"
numpoints = 6000  # ⚠️ 6000 bougies ≈ 100 heures

print("📥 Téléchargement de 6000 bougies M1...")
response = ig_service.fetch_historical_prices_by_epic_and_num_points(
    epic=epic,
    resolution=resolution,
    numpoints=numpoints
)

df = response['prices']
df.columns = ['_'.join(col).strip() for col in df.columns]
df.reset_index(inplace=True)

# Ajout des colonnes de temps si absentes
if 'date' in df.columns:
    df.rename(columns={'date': 'timestamp'}, inplace=True)

# Sauvegarde dans un CSV
csv_filename = "eurusd_m1_6000.csv"
df.to_csv(csv_filename, index=False)
print(f"✅ Données enregistrées dans {csv_filename}")
