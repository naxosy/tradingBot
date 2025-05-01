USERNAME = "naxosy_demo"
PASSWORD = "$$deR69me5"
API_KEY = "9744350976c271ef25e9c241338c1695f23a1e91"
ACC_TYPE = "demo"
ACC_ID = "Z5YW5L"

EPIC = "CS.D.EURUSD.MINI.IP"
INSTRUMENT = "EUR.USD"
RES = "1Min"

TICK = 60

PIP_VALUE = 0.0001
SIZE_PRECISION = 0.1
DEFAULT_POS_SIZE = 10.0 # passer à 20 sur la release def

INITIAL_NUMPOINTS = 100


#--------------------- Gestion des logs
import logging, sys
from datetime import datetime
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def setup_logging():

    log_filename = f"trading_log_{datetime.now():%Y%m%d_%H%M%S}.log"
    # Création du logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Définit le niveau global minimal

    # Handler FICHIER (DEBUG et plus)
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt='%d/%m - %Hh%M'
    )
    file_handler.setFormatter(file_formatter)

    # Handler CONSOLE (INFO et plus)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt='%d/%m - %Hh%M'
    )
    console_handler.setFormatter(console_formatter)

    # Ajout des handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("trading_ig").setLevel(logging.WARNING)

