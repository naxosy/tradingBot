class Order:
    def __init__(self, order_type, size=None, value=None, sl=None, tp=None, trade_id=None, direction=None, origin=None):
        self.order_type = order_type
        self.size = size
        self.value = value
        self.trade_id = trade_id
        self.sl = sl
        self.tp = tp
        self.direction = direction
        self.origin= origin

    def __str__(self):
        output = f"Ordre {self.order_type} "
        tp = f"{self.tp:.5f}" if self.tp is not None else "N/A"
        sl = f"{self.sl:.5f}" if self.sl is not None else "N/A"
        match self.order_type:
            case "UPDATE":
                output += f"pour le trade n°{self.trade_id}, on passe le SL à {sl} et le TP à {tp}"
                pass
            case "OPEN":
                output += f" position {self.direction} de {self.size} lots avec SL à {sl} et TP à {tp}"
            case "CLOSE":
                if self.origin == "TP":
                    header = "TP hit"
                elif self.origin == "SL:":
                    header = "SL hit"
                else :
                    header = "unknown"
                output += f"pour le trade n°{self.trade_id}, origine : {header}"

        return output