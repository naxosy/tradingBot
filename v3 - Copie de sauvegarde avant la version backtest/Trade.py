from config import PIP_VALUE
class Trade:
    _id_counter = 0  # index du trade

    @classmethod
    def set_start_id(cls, value: int) -> None:
        cls._id_counter = value

    def __init__(self, kind, sl, tp, open_date, close_date, entry_price, exit_price, size, instrument, epic):
        self.id = Trade._id_counter
        Trade._id_counter += 1
        self.kind = kind
        self.sl = sl
        self.tp = tp
        self.open_date = open_date
        self.close_date = close_date
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.size = size
        self.instrument = instrument
        self.epic = epic

        self.profit = None
        self.closed = False
        self.close_type = None

    def __str__(self):
            if self.closed :
                header = "TP hit" if self.close_type == "TP" else "SL hit"
                return f"Trade {self.id} ({self.kind} {self.size:.1f}) fermé ({header}) à {self.close_date} : sortie à {self.exit_price:.5f} soit un profit de {self.profit:.1f} pips"
            else :
                tp = f"{self.tp:.5f}" if self.tp is not None else "N/A"
                sl = f"{self.sl:.5f}" if self.sl is not None else "N/A"
                return f"Trade {self.id} ({self.kind} {self.size:.1f}) ouvert à {self.open_date} : entrée à {self.entry_price:.5f} avec un TP à {tp} et un SL à {sl}"

    def open(self):
        return None

    def close(self, exit_price, close_date, close_type):
        self.exit_price = exit_price
        self.close_date = close_date
        self.close_type = close_type
        if self.kind == "BUY":
            self.profit = self.exit_price - self.entry_price
        elif self.kind == "SELL" :
            self.profit = self.entry_price - self.exit_price
        self.profit /= PIP_VALUE
        self.closed = True
        print(self)

    def update(self, candle):
        trade_closed = False
        if self.kind == "BUY":
            if candle[('ask', 'Low')] <= self.sl :
                self.close(self.sl, candle[0], "SL")
                trade_closed = True
            elif candle[('ask', 'High')] >= self.tp :
                self.close(self.tp, candle[0], "TP")
                trade_closed = True
            else :
                last_sl = self.sl
                self.sl = candle[('ask', 'ask_ema_13')]
                print(f"Trade {self.id} - SL passé de {last_sl:.4f} à {self.sl:.4f}")
        if self.kind == "SELL":
            if candle[('bid', 'High')] >= self.sl:
                self.close(self.sl, candle[0], "SL")
                trade_closed = True
            elif candle[('bid', 'Low')] <= self.tp:
                self.close(self.tp, candle[0], "TP")
                trade_closed = True
            else:
                last_sl = self.sl
                self.sl = candle[('bid', 'bid_ema_13')]
                print(f"Trade {self.id} - SL passé de {last_sl:.4f} à {self.sl:.4f}")
        return trade_closed