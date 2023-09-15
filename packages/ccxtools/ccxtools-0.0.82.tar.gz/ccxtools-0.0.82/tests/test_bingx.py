import pytest
import math
from src.ccxtools.bingx import Bingx


@pytest.fixture
def bingx(env_vars):
    return Bingx('', env_vars)


def test_get_funding_rates(bingx, necessary_tickers):
    funding_rates = bingx.get_funding_rates()
    for ticker in necessary_tickers:
        assert ticker in funding_rates
        assert isinstance(funding_rates[ticker], float)


def test_get_contract_sizes(bingx):
    sizes = bingx.get_contract_sizes()
    assert isinstance(sizes, dict)
    assert sizes['BTC'] == 0.0001
    assert sizes['ETH'] == 0.01


def test_get_balance(bingx):
    # Test input Start
    ticker = 'USDT'
    balance_input = 9813
    # Test input End

    balance = bingx.get_balance(ticker)
    assert balance_input * 0.9 <= balance <= balance_input * 1.1


def test_get_position(bingx):
    # Test input Start
    ticker = 'XRP'
    amount = -4
    # Test input End

    position = bingx.get_position(ticker)
    assert isinstance(position, float)
    if amount:
        assert math.isclose(position, amount)


def test_post_market_order(bingx):
    # Test input Start
    ticker = 'XRP'
    amount = 20
    # Test input End

    contracts = bingx.get_ticker()['data']['tickers']
    last_price = float(list(filter(lambda contract: contract['symbol'] == f'{ticker}-USDT', contracts))[0]['lastPrice'])

    buy_open_price = bingx.post_market_order(ticker, 'buy', 'open', amount)
    assert 0.9 * last_price < buy_open_price < 1.1 * last_price
    sell_close_price = bingx.post_market_order(ticker, 'sell', 'close', amount)
    assert 0.9 * last_price < sell_close_price < 1.1 * last_price
    sell_open_price = bingx.post_market_order(ticker, 'sell', 'open', amount)
    assert 0.9 * last_price < sell_open_price < 1.1 * last_price
    buy_close_price = bingx.post_market_order(ticker, 'buy', 'close', amount)
    assert 0.9 * last_price < buy_close_price < 1.1 * last_price


def test_get_precise_order_amount(bingx):
    ticker = 'BTC'
    ticker_amount = 0.00011
    assert bingx.get_precise_order_amount(ticker, ticker_amount) == 0.0001


def test_get_last_price(bingx):
    last_price = bingx.get_last_price('BTC')
    assert isinstance(last_price, float)
    assert last_price > 10000


def test_get_contracts(bingx):
    response = bingx.get_contracts()
    assert response['code'] == 0


def test_get_latest_price(bingx):
    # Test input Start
    ticker = 'BTC'
    # Test input End
    response = bingx.get_latest_price(ticker)
    for price_name in ['tradePrice', 'indexPrice', 'fairPrice']:
        assert price_name in response['data']


def test_get_market_depth(bingx):
    depth_data = bingx.get_market_depth('BTC')
    for side in ['asks', 'bids']:
        assert side in depth_data
        assert 'p' in depth_data[side][0]
        assert 'v' in depth_data[side][0]


def test_get_ticker(bingx):
    # Test input Start
    ticker = 'BTC'
    # Test input End

    tickers = bingx.get_ticker()['data']['tickers']
    assert isinstance(tickers, list)
    assert 'symbol' in tickers[0]
    ticker_data = bingx.get_ticker('BTC')['data']['tickers'][0]
    assert ticker_data['symbol'] == f'{ticker}-USDT'


def test_get_account_asset(bingx):
    res = bingx.get_account_asset('USDT')
    assert res['code'] == 0
    assert res['msg'] == ''


def test_get_swap_positions(bingx):
    res = bingx.get_swap_positions()
    assert res['code'] == 0
    assert 'positions' in res['data']
    assert isinstance(res['data']['positions'], list)


def test_post_order(bingx):
    # Test input Start
    ticker = 'XRP'
    side = 'Bid'
    amount = 20
    # Test input End

    order_id = bingx.post_order(ticker, side, amount, 'Market', 'Open')['data']['orderId']
    order_info = bingx.get_order(ticker, order_id)['data']

    assert order_info['action'] == 'Open'
    assert order_info['entrustVolume'] == amount
    assert order_info['side'] == side
    assert order_info['tradeType'] == 'Market'


def test_get_order(bingx):
    data = bingx.get_order('XRP', '1694169380130131968')['data']

    order_info = {
        'action': 'Close',
        'avgFilledPrice': 3.6777,
        'commission': -0.327322,
        'entrustPrice': 3.6973,
        'entrustTm': '2023-08-23T02:07:11Z',
        'entrustVolume': 178,
        'filledVolume': 178,
        'orderId': '1694169380130131968',
        'profit': -19.4491,
        'side': 'Bid',
        'status': 'Filled',
        'tradeType': 'Market',
        'updateTm': '2023-08-23T02:07:11Z'
    }

    assert data == order_info
