from ccxtools.base.Exchange import Exchange


class CcxtExchange(Exchange):

    def __init__(self):
        self.ccxt_inst = None

    def get_balance(self, ticker):
        """
        :param ticker: <String> Ticker name. ex) 'USDT', 'BTC'
        :return: <Int> Balance amount
        """
        return self.ccxt_inst.fetch_balance()[ticker]['total']
