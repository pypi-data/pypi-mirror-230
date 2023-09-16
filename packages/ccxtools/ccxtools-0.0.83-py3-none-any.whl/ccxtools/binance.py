import ccxt

from ccxtools.base.CcxtFutureExchange import CcxtFutureExchange


class Binance(CcxtFutureExchange):

    def __init__(self, who, env_vars, extra_config):
        super().__init__()

        config = dict({
            'apiKey': env_vars(f'BINANCE_API_KEY{who}'),
            'secret': env_vars(f'BINANCE_SECRET_KEY{who}')
        }, **extra_config)

        self.ccxt_inst = ccxt.binance(config)
