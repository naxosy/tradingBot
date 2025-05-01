from trading_ig import IGService

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


ig_service = IGService(username, password, api_key, acc_type, acc_number=account_id)
ig_service.create_session(version='3')

epic = 'CS.D.EURUSD.MINI.IP'
resolution = '1Min'
max_points = 600

# === Récupération initiale des bougies ===
print(f"📥 Téléchargement des {max_points} bougies passées...")
response = ig_service.fetch_historical_prices_by_epic_and_num_points(
    epic=epic,
    resolution=resolution,
    numpoints=max_points
)
df = response['prices']
df.columns = ['_'.join(col).strip() for col in df.columns]
df.reset_index(inplace=True)

# Ajout des colonnes de temps si absentes
if 'date' in df.columns:
    df.rename(columns={'date': 'timestamp'}, inplace=True)

# Sauvegarde dans un CSV
csv_filename = "eurusd_m1_last.csv"
df.to_csv(csv_filename, index=False)
print(f"✅ Données enregistrées dans {csv_filename}")
