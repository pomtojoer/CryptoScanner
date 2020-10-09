class ScanDetails:
    def __init__(self, name, exchange, interval, description):
        self.status = None
        self.name = None
        self.exchange = None
        self.interval = None
        self.description = None
        self.filters = None
        self.indicators = None
    

    def get_status(self):
        pass

    def add_filter(self, quantity, condition, value, lookback):
        if self.filters == None:
            self.filters = []

        new_filter = dict(
            quantity=quantity,
            condition=condition,
            value=value,
            lookback=lookback,
        )
        self.filters.append(new_filter)

    def add_indicator(self, indicator_1, condition, indicator_2, value, style, note):
        if self.indicators == None:
            self.indicators = []

        new_indicator = dict(
            indicator_1=indicator_1,
            condition=condition,
            indicator_2=indicator_2,
            value=value,
            style=style,
            note=note,
        )
        self.indicators.append(new_indicator)

    def remove_filter(self):
        pass

    def remove_indicator(self):
        pass

    def change_status(self):
        pass