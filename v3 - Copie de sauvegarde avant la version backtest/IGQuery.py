import config
import warnings
from datetime import datetime

from v3.Order import Order

warnings.simplefilter(action='ignore', category=FutureWarning)

from trading_ig import IGService
import pandas as pd

max_points = 15
from Trade import Trade
import logging
logger = logging.getLogger(__name__)


def fetch_current_trades():
    logger.info("Récupération des trades déjà ouverts ...")
    fetched_dict = {}
    ig_service = IGService(config.USERNAME, config.PASSWORD, config.API_KEY, config.ACC_TYPE, acc_number=config.ACC_ID)
    ig_service.create_session(version='3')
    open_positions = ig_service.fetch_open_positions()
    open_trade_count = len(open_positions)
    logger.info(f"{open_trade_count} position(s) retournée(s) par le serveur")

    for index, row in open_positions.iterrows():
        new_trade = Trade(
            row['direction'],
            row['stopLevel'],
            row['limitLevel'],
            datetime.strptime(row['createdDate'], "%Y/%m/%d %H:%M:%S:%f"),
            None,
            row['level'],
            None,
            row['size'],
            row['instrumentName'],
            row['epic']
        )

        fetched_dict[row['dealId']] = new_trade
        logging.info(f"Le trade suivant a été trouvé ouvert -> {str(new_trade)}")

    return fetched_dict


def fetch_initial_candles():
    # === Récupération initiale des bougies ===
    ig_service = IGService(config.USERNAME, config.PASSWORD, config.API_KEY, config.ACC_TYPE, acc_number=config.ACC_ID)
    ig_service.create_session(version='3')

    logger.info("📥 Téléchargement initial des bougies...")
    response = ig_service.fetch_historical_prices_by_epic_and_num_points(
        epic=config.EPIC,
        resolution=config.RES,
        numpoints=max_points
    )

    return response['prices']


def update_candles(df):
    # === Récupération de la dernière bougie ===
    ig_service = IGService(config.USERNAME, config.PASSWORD, config.API_KEY, config.ACC_TYPE, acc_number=config.ACC_ID)
    ig_service.create_session(version='3')

    logger.info("📥 Mise à jour : récupération de la dernière bougie...")
    response = ig_service.fetch_historical_prices_by_epic_and_num_points(
        epic=config.EPIC,
        resolution=config.RES,
        numpoints=1
    )
    new_row = response['prices']

    # === On vérifie qu'il n'y a pas doublon ===
    timestamp = new_row.index[0]
    if timestamp not in df.index:
        df = pd.concat([df, new_row])
        df = df.iloc[1:]
        logger.debug(f"✅ Nouvelle ligne ajoutée : {timestamp}")
    else:
        logger.debug(f"⚠️ Ligne ignorée (doublon) : {timestamp}")

    return df

def fetch_funds_summary() -> dict:
    ig_service = IGService(config.USERNAME, config.PASSWORD, config.API_KEY, config.ACC_TYPE, acc_number=config.ACC_ID)
    ig_service.create_session(version='3')
    logger.debug("Connexion au serveur pour récupération des données du compte ...")
    accounts = ig_service.fetch_accounts()
    account = accounts[accounts["accountId"] == config.ACC_ID]
    account_dict = account.iloc[0].to_dict()
    logger.debug(f"Compte connecté : {account_dict}")
    return account_dict

def open_position(order: Order):
    ig_service = IGService(config.USERNAME, config.PASSWORD, config.API_KEY, config.ACC_TYPE, acc_number=config.ACC_ID)
    ig_service.create_session(version='3')

    logger.info(f"Tentative d'ouverture de position")
    logger.info(f"Ordre envoyé : {order}")
    response = ig_service.create_open_position(
        currency_code='USD',
        direction=order.direction,
        epic='CS.D.EURUSD.MINI.IP',
        expiry='-',
        force_open=True,
        guaranteed_stop=False,
        level=None,
        limit_distance=None,
        stop_distance=None,
        limit_level=order.tp,
        stop_level=order.sl,
        order_type='MARKET',
        quote_id=None,
        size=order.size,
        trailing_stop=False,
        trailing_stop_increment=None
    )

    if response.get("status") == "AMENDED" or response.get("reason") == "SUCCESS":
        print("✅ Create position query accepted")
    else:
        print(f"❌ Create position query failed: {response.get('reason', 'Unknown reason')}")

    return response

def update_position(order: Order):
    logger.info(f"Ordre passé au serveur : {order}")
    ig_service = IGService(config.USERNAME, config.PASSWORD, config.API_KEY, config.ACC_TYPE, acc_number=config.ACC_ID)
    ig_service.create_session(version='3')
    response = ig_service.update_open_position(
        deal_id=order.trade_id,
        stop_level=round(order.sl, 5),
        limit_level=round(order.tp, 5),
    )
    if response.get("status") == "AMENDED" or response.get("reason") == "SUCCESS":
        logger.info("✅ Ordre accepté par le serveur")
    else:
        logger.info(f"❌ Ordre refusé par le serveur : {response.get('reason', 'Unknown reason')}")
        logger.info(f"{response}")
    return response


def calculate_position_size(amount: float, direction: str = 'BUY'):
    return config.DEFAULT_SIZE

if __name__ == "__main__":
    ig_service = IGService(config.USERNAME, config.PASSWORD, config.API_KEY, config.ACC_TYPE, acc_number=config.ACC_ID)
    ig_service.create_session(version='3')

    accounts = ig_service.fetch_accounts()
    print(type(accounts))
    print(accounts.columns)


