import time
import pandas as pd
pd.set_option("display.float_format", "{:.5f}".format)
import IGQuery, engine
import config
import logging



if __name__ == "__main__":

    config.setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Lancement de l'application")

    df = IGQuery.fetch_initial_candles()
    trade_dict = IGQuery.fetch_current_trades()
    account_status = IGQuery.fetch_funds_summary()

    cur_tick = 1
    while(True):
        df = IGQuery.update_candles(df)
        current_trades = IGQuery.fetch_current_trades()
        account_status = IGQuery.fetch_funds_summary()
        engine.tick(df, current_trades, account_status)

        print(f"Tick {cur_tick} -------------------")
        print(engine.print_last_candle(df))
        print(f"Positions ouvertes actuellement : {len(current_trades)}")
        for index, trade in current_trades.items() :
            print(f"{index} : {trade}")
        print("-----------------------")
        cur_tick += 1
        time.sleep(config.TICK)