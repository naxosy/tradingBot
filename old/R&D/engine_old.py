import pandas as pd
import ta

PIP_VALUE = 0.0001

class Trade:
    def __init__(self, kind, sl, tp, open_date, close_date, entry_price, exit_price):
        self.kind = kind
        self.sl = sl
        self.tp = tp
        self.open_date = open_date
        self.close_date = close_date
        self.entry_price = entry_price
        self.exit_price = exit_price

        self.profit = None
        self.closed = False
        self.close_type = None

        print(self)

    def __str__(self):
            if self.closed :
                header = "TP hit" if self.close_type == "TP" else "SL hit"
                return f"{self.kind} trade fermé ({header}) à {self.close_date} : sortie à {self.exit_price:.4f} soit un profit de {self.profit:.1f} pips"
            else :
                return f"{self.kind} trade ouvert à {self.open_date} : entrée à {self.entry_price:.4f} avec un TP à {self.tp:.4f} et un SL à {self.sl:.4f}"

    def close(self, exit_price, close_date, close_type):
        self.exit_price = exit_price
        self.close_date = close_date
        self.close_type = close_type
        if self.kind == "LONG":
            self.profit = self.exit_price - self.entry_price
        elif self.kind == "SHORT" :
            self.profit = self.entry_price - self.exit_price
        self.profit /= PIP_VALUE
        self.closed = True
        print(self)

    def update(self, candle):
        trade_closed = False
        match self.kind :
            case "LONG":
                if candle.bid_Close <= self.sl :
                    self.close(self.sl, candle[0], "SL")
                    trade_closed = True
                elif candle.bid_Close >= self.tp :
                    self.close(self.tp, candle[0], "TP")
                    trade_closed = True
                else :
                    self.sl = candle.ema_13
            case "SHORT":
                if candle.ask_Close >= self.sl:
                    self.close(self.sl, candle[0], "SL")
                    trade_closed = True
                elif candle.ask_Close <= self.tp:
                    self.close(self.tp, candle[0], "TP")
                    trade_closed = True
                else:
                    self.sl = candle.ema_13
        return trade_closed



def apply_strat_to_df(df):

    result = 0
    last = {}
    current_trade = None
    profit = 0

    for candle in df.itertuples():

        if not last :
            last['price'] = candle.bid_Close
            last['ema_5'] = candle.ema_5
            last['ema_13'] = candle.ema_13
            continue

        price = candle.bid_Close
        ema_5 = candle.ema_5
        ema_13 = candle.ema_13

        if last['ema_5'] < last['ema_13'] and ema_5 > ema_13 : # LONG trade signal
            price = candle.ask_Close
            sl = last['ema_5']
            tp = price + (price-sl) * 3
            current_trade = Trade("LONG", sl, tp, candle[0], None, price, None )

        if last['ema_5'] > last['ema_13'] and ema_5 < ema_13: # SHORT trade signal
            price = candle.bid_Close
            sl = last['ema_5']
            tp = price - (sl-price)*3
            current_trade = Trade("SHORT", sl, tp, candle[0], None, price, None)

        if current_trade :
            closed = current_trade.update(candle)
            if closed :
                profit += current_trade.profit
                current_trade = None

        last['price'] = price
        last['ema_5'] = ema_5
        last['ema_13'] = ema_13

    return profit