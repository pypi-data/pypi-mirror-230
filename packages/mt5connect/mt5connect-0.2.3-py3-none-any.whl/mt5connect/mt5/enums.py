from enum import Enum


class OrderType(Enum):
    LONG = "buy"
    SHORT = "sell"
    LONG_LIMIT = "buylimit"
    SHORT_LIMIT = "selllimit"
    LONG_STOP = "buystop"
    SHORT_STOP = "sellstop"


class ErrorCodes(Enum):
    ERR_1 = "Limit Long 'price' cannot be higher than the current bid price"
    ERR_2 = "Limit Short 'price' cannot be lower than the current ask price"
    ERR_3 = "Order Type not supported. Please use long or short"
    ERR_4 = "Price for a Limit/Stop order cannot be 0"
    ERR_5 = "Stop Long 'price' cannot be lower than the current bid price"
    ERR_6 = "Stop Short 'price' cannot be higher than the current ask price"
