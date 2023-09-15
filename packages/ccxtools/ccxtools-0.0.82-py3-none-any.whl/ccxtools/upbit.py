import ccxt
from ccxtools.base.CcxtExchange import CcxtExchange


class Upbit(CcxtExchange):

    def __init__(self, who, config):
        super().__init__()
        self.ccxt_inst = ccxt.upbit({
            'apiKey': config(f'UPBIT_API_KEY{who}'),
            'secret': config(f'UPBIT_SECRET_KEY{who}')
        })

    def get_last_price(self, ticker):
        res = self.ccxt_inst.fetch_ticker(f'{ticker}/KRW')
        return res['last']

    def get_best_book_price(self, ticker, side):
        order_book = self.ccxt_inst.fetch_order_book(f'{ticker}/KRW')[f'{side}s']
        return order_book[0][0]

    def post_market_order(self, ticker, side, amount, price):
        res = self.ccxt_inst.create_order(f'{ticker}/KRW', 'market', side, amount, price)
        order_data = self.ccxt_inst.fetch_order(res['id'])
        return order_data['average']
