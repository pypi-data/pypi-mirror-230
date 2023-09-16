import asyncio
import os
import requests
from bs4 import BeautifulSoup
from decouple import Config, RepositoryEnv


def get_current_directory():
    return os.path.abspath(os.curdir)


def get_env_vars():
    current_directory = get_current_directory()
    return Config(RepositoryEnv(f'{current_directory}/.env'))


def get_async_results(func_list):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as error:
        if 'There is no current event loop in thread' in str(error):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise error

    async def run_func(func_info):
        func = func_info['func']
        args = func_info.get('args', ())
        return await loop.run_in_executor(None, func, *args)

    results = loop.run_until_complete(asyncio.gather(*[
        run_func(func_info) for func_info in func_list
    ]))
    return results


def add_query_to_url(base_url, queries):
    url = f'{base_url}?'
    for field, value in queries.items():
        url += f'{field}={value}&'
    return url[:-1]


def get_usdkrw_rate():
    url = "https://markets.businessinsider.com/currencies/usd-krw"
    selector = "span.price-section__current-value"

    b_soup = BeautifulSoup(requests.get(url).text, "html.parser")
    tags = b_soup.select(selector)
    exch_rate = float(tags[0].text.replace(",", ""))

    # Business Insider 환율 오류 시 네이버 환율 참조
    if not 500 < exch_rate < 2000:
        url = "https://finance.naver.com/marketindex/"
        selector = "#exchangeList > li:nth-child(1) > a.head.usd > div > span.value"

        b_soup = BeautifulSoup(requests.get(url).text, "html.parser")
        tags = b_soup.select(selector)
        exch_rate = float(tags[0].text.replace(',', ''))

    return exch_rate
