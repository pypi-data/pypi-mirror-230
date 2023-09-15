import time
import ccxt
from ccxtools.base.CcxtFutureExchange import CcxtFutureExchange


class Bitget(CcxtFutureExchange):

    def __init__(self, who, config):
        super().__init__()

        self.ccxt_inst = ccxt.bitget({
            'apiKey': config(f'BITGET_API_KEY{who}'),
            'secret': config(f'BITGET_SECRET_KEY{who}'),
            'password': config(f'BITGET_PASSWORD{who}'),
            'options': {
                'defaultType': 'swap',
                'fetchMarkets': ['swap'],
            },
        })
        self.contract_sizes = self.get_contract_sizes()

    def get_contracts(self):
        contracts = []
        for contract in self.ccxt_inst.fetch_markets():
            if not contract['active'] or contract['future'] or not contract['linear'] or contract['settle'] != 'USDT':
                continue

            contracts.append(contract)

        return contracts

    def get_funding_rates(self):
        contracts = self.ccxt_inst.public_mix_get_market_tickers({
            'productType': 'UMCBL'
        })['data']

        funding_rates = {}
        for contract in contracts:
            ticker = contract['symbol'][:contract['symbol'].find('USDT_')]
            funding_rates[ticker] = float(contract['fundingRate'])

        return funding_rates

    def get_contract_sizes(self):
        sizes = {}
        for contract in self.get_contracts():
            sizes[contract['base']] = contract['precision']['amount']

        return sizes

    def get_balance(self, ticker):
        balances = self.ccxt_inst.fetch_balance()['info']
        ticker_balance = next((data for data in balances if data['marginCoin'] == ticker), None)
        return float(ticker_balance['equity']) if ticker_balance else 0

    def get_position(self, ticker):
        res = self.ccxt_inst.fetch_position(f'{ticker}USDT_UMCBL')
        abs_size = float(res['info']['total'])
        return abs_size if res['side'] == 'long' else -abs_size

    def post_market_order(self, ticker, side, open_close, amount):
        symbol = f'{ticker}USDT_UMCBL'
        if open_close == 'open':
            param_side = f'open_{"long" if side == "buy" else "short"}'
        else:
            param_side = f'close_{"short" if side == "buy" else "long"}'

        res = self.ccxt_inst.create_market_order(symbol, param_side, amount)

        for i in range(10):
            try:
                order = self.ccxt_inst.fetch_order(res['id'], symbol)
                if order['status'] == 'open':
                    time.sleep(0.1)
                    continue

                return order['average']
            except Exception as error:
                if i < 9:
                    time.sleep(0.1)
                    continue

                raise error

        raise Exception('order not filled')
