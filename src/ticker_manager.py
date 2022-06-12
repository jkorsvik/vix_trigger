from enum import Enum, auto, unique
class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

@unique
class Ticker(AutoName):
    VIX = "^VIX" #auto()
    AAPL = auto()
    TSLA = auto()
    MSFT = auto()
    GME = auto()
    SP500 = "^GSPC" #auto()
    Natural_Gas = "NG=F" #auto()# Natural GasJULY 2022
    Corn = "ZC=F" #auto()# DEC 2022
    Wheat = "KE=F" #auto()# SEPT 2022
    Crude_Oil = "CL=F" #auto()



if __name__ == '__main__':   
    for tick in Ticker:
        print(tick == Ticker.AAPL)

    data = {Ticker.AAPL: "test"} 
    print(data)
    print(tick.value)