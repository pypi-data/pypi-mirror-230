import MetaTrader5 as Mt5

class Tick:

    def __init__(self, symbol):

        self.time = Mt5.symbol_info_tick(symbol).time
        self.bid = Mt5.symbol_info_tick(symbol).bid
        self.ask = Mt5.symbol_info_tick(symbol).ask
        self.last = Mt5.symbol_info_tick(symbol).last
        self.volume = Mt5.symbol_info_tick(symbol).volume
        self.time_msc = Mt5.symbol_info_tick(symbol).time_msc
        self.flags = Mt5.symbol_info_tick(symbol).flags
        self.volume_real = Mt5.symbol_info_tick(symbol).volume_real

    def filling_type(input):

        if input == 1:
            return "Mt5.ORDER_FILLING_FOK"
        
        elif input == 2:
            return "ORDER_FILLING_IOC"
        
        elif input == 3:
            return "ORDER_FILLING_RETURN"