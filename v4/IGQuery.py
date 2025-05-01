from datetime import datetime
from trading_ig import IGService
import pandas as pd
import config
from Trade import Trade
import utils

def fetch_initial_candles():
    # === Récupération initiale des bougies ===
    ig_service = IGService(config.USERNAME, config.PASSWORD, config.API_KEY, config.ACC_TYPE, acc_number=config.ACC_ID)
    ig_service.create_session(version='3')

    print("📥 Téléchargement initial des bougies...")
    response = ig_service.fetch_historical_prices_by_epic_and_num_points(
        epic=config.EPIC,
        resolution=config.RES,
        numpoints=config.INITIAL_NUMPOINTS
    )

    return response['prices']


def update_candles(df):
    # === Récupération des deux dernières bougies ===
    ig_service = IGService(config.USERNAME, config.PASSWORD, config.API_KEY,
                           config.ACC_TYPE, acc_number=config.ACC_ID)
    ig_service.create_session(version='3')

    print("📥 Mise à jour : récupération des deux dernières bougies...")
    response = ig_service.fetch_historical_prices_by_epic_and_num_points(
        epic=config.EPIC,
        resolution=config.RES,
        numpoints=2
    )
    new_rows = response['prices']

    # === On prend l'avant-dernière bougie ===
    if len(new_rows) < 2:
        print(
            "⚠️ Pas assez de données récupérées pour ajouter l'avant-dernière bougie.")
        return df

    before_last_row = new_rows.iloc[
                      0:1]  # On garde uniquement la première ligne

    # === Vérification doublon ===
    timestamp = before_last_row.index[0]
    if timestamp not in df.index:
        df = pd.concat([df, before_last_row])
        df = df.iloc[1:]
        df = utils.calc_EMA(df)
        print(f"✅ Nouvelle ligne (avant-dernière) ajoutée : {timestamp}")
    else:
        print(f"⚠️ Ligne ignorée (doublon) : {timestamp}")

    return df

def fetch_current_trades():
    print("Récupération des trades déjà ouverts ...")
    fetched_list = []
    ig_service = IGService(config.USERNAME, config.PASSWORD, config.API_KEY, config.ACC_TYPE, acc_number=config.ACC_ID)
    ig_service.create_session(version='3')
    open_positions = ig_service.fetch_open_positions()
    open_trade_count = len(open_positions)
    print(f"{open_trade_count} position(s) retournée(s) par le serveur")

    for index, row in open_positions.iterrows():
        opened_trade = Trade(
            row['direction'],
            row['size'],
            row['level'],
            opening_date=datetime.strptime(
                row['createdDate'],
                "%Y/%m/%d %H:%M:%S:%f"
            ),
            sl=row['stopLevel'],
            tp=row['limitLevel'],
            dealId=row['dealId']
        )

        fetched_list.append(opened_trade)
        print(f"Le trade suivant est en cours -> {str(opened_trade)}")

    return fetched_list

def update_trade_lists(df, current_trades, closed_trades):
    return current_trades, closed_trades

def open_position(trade:Trade):
    ig_service = IGService(config.USERNAME, config.PASSWORD, config.API_KEY,
                           config.ACC_TYPE, acc_number=config.ACC_ID)
    ig_service.create_session(version='3')

    print(f"Tentative d'ouverture de position")
    response = ig_service.create_open_position(
        currency_code='USD',
        direction=trade.direction,
        epic='CS.D.EURUSD.MINI.IP',
        expiry='-',
        force_open=True,
        guaranteed_stop=False,
        level=None,
        limit_distance=None,
        stop_distance=None,
        limit_level=trade.tp,
        stop_level=trade.sl,
        order_type='MARKET',
        quote_id=None,
        size=trade.size,
        trailing_stop=False,
        trailing_stop_increment=None
    )

    if response.get("reason") == "SUCCESS":
        trade.dealId = response['dealId']
        print(f"✅ Query accepted, following position opened : {trade}")

    else:
        print(
            f"❌ Create position query failed: {response.get('reason', 'Unknown reason')}")

    return response

def close_position(trade :Trade):
    ig_service = IGService(config.USERNAME, config.PASSWORD, config.API_KEY,
                           config.ACC_TYPE, acc_number=config.ACC_ID)
    ig_service.create_session(version='3')

    direction = "BUY" if trade.direction == "SELL" else "SELL" #direction of
    # closing order has to be the opposite of the direction of the position
    response = ig_service.close_open_position(trade.dealId, direction,
                                              epic=None,
                                              expiry=None,
                                              level=None,
                                              order_type="MARKET",
                                              quote_id=None,
                                              size=trade.size,
                                              session=None)

    if response.get("reason") == "SUCCESS":
        trade.dealId = response['dealId']
        print(f"✅ Query accepted, following position closed : {trade}")

    else:
        print(
            f"❌ Query failed : {response.get('reason', 'Unknown reason')} ("
            f"trying to close position)")

    return response