import config
import pandas as pd
import random
import string


class Trade:
    def __init__(self, direction, size, level, opening_date=None, sl=None,
                 tp=None, closed=False, closing_date=None, closing_level=None,
                 closing_origin=None, dealId=None):
        self.direction = direction
        self.size = size
        self.level = level
        self.opening_date = opening_date
        self.sl = sl
        self.tp = tp
        self.closed = closed
        self.closing_date = closing_date
        self.closing_level = closing_level
        self.closing_origin = closing_origin

        self.dealId = dealId
        if self.dealId is None:
            characters = string.ascii_letters + string.digits  # a-zA-Z0-9
            self.dealId = ''.join(random.choices(characters, k=8))

        self.profit = 0

    def __str__(self):

        tp = "N/A" if self.tp is None else f"{self.tp:.5f}"
        sl = "N/A" if self.sl is None else f"{self.sl:.5f}"

        if self.closed:
            output = (f"{self.dealId} - {self.direction} ({self.size}lots) ouvert à "
                      f"{self.opening_date} (prix {self.level:.5f}) et fermé à "
                      f"{self.closing_date} ({self.closing_origin} hit - prix "
                      f"{self.closing_level:.5f}). Dernier TP : {tp} - Dernier"
                      f"SL : {sl} - profit {self.profit:.1f}")
        else:
            output = (f"{self.dealId} - {self.direction} ({self.size}lots) ouvert à "
                      f"{self.opening_date} (prix {self.level:.5f}) - En cours"
                      f"avec un TP à {tp} et un SL à {sl}")
        return output

    def close(self, closing_date, closing_level, closing_origin):
        self.closing_date = closing_date
        self.closing_level = closing_level
        self.closing_origin = closing_origin

        if self.direction == "BUY":
            self.profit = (self.closing_level - self.level) / config.PIP_VALUE
        else:
            self.profit = (self.level - self.closing_level) / config.PIP_VALUE

        self.profit = round(self.profit, 1)

        self.closed=True
