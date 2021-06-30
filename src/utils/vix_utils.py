def isNewHigh(high, data):
    """
    Returns True if the 'high' is higher than any of the highs in the data
    array passed in. Otherwise returns False
    """
    highs = data.get("High")
    for i in highs:
        try:
            if (float(i)) >= float(high):
                return False
        except ValueError:
            return False
    return True


def isNewLow(low, data):
    """
    Returns True if the 'low' is lower than any of the lows in the data
    array passed in. Otherwise returns False
    """
    lows = data.get("Low")
    print(low)
    for i in lows:
        try:
            if float(i) <= float(low):
                return False
        except ValueError:
            return False
    return True


def isCurrentHigherThanOpen(current, open):
    """
    Simple check to see if the current price is greater than the open price
    """
    return float(current) > float(open)


def isCurrentLowerThanOpen(current, open):
    """
    Simple check to see if the current price is lower than the open price
    """
    return float(current) < float(open)
