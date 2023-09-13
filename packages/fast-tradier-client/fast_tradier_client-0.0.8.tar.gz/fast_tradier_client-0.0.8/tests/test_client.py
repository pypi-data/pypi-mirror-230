# to run pytest:
# python -m pytest tests/test_client.py
import httpx
import pytest
import json
import arrow
import pytz
import random
from datetime import datetime, timedelta
from typing import Dict
from pathlib import Path
from pytest_httpx import HTTPXMock

from fast_tradier.models.account import AccountBalance
from fast_tradier.FastTradierClient import FastTradierClient
from fast_tradier.FastTradierAsyncClient import FastTradierAsyncClient
from fast_tradier.utils.OptionUtils import OptionUtils

from fast_tradier.models.trading.OptionOrder import OptionLeg, OptionOrder
from fast_tradier.models.trading.EquityOrder import EquityOrder
from fast_tradier.models.trading.Sides import OptionOrderSide, EquityOrderSide
from fast_tradier.models.trading.PriceTypes import OptionPriceType, EquityPriceType
from fast_tradier.models.trading.Duration import Duration

eastern = pytz.timezone('US/Eastern')
mock_response_file_name = 'tradier_api_response_mock.json'
account_id = 'abc'
account_at = '123xyz'

def mock_order() -> OptionOrder:
    ticker = 'SPX'
    order_status = 'pending'
    option_symbols = ['SPXW_080823C4510', 'SPXW_080823C4520'] #TODO: replace option symbols
    sides = [OptionOrderSide.SellToOpen, OptionOrderSide.BuyToOpen]
    option_legs = []

    for i in range(len(sides)):
        opt_symbol = option_symbols[i]
        side = sides[i]
        option_legs.append(OptionLeg(underlying_symbol=ticker, option_symbol=opt_symbol, side=side, quantity=1))

    option_order = OptionOrder(ticker=ticker,
                            price=1.2,
                            price_type=OptionPriceType.Credit,
                            duration=Duration.Day,
                            option_legs=option_legs)
    return option_order

def get_mock_response() -> Dict:
    mock_file_path = Path(Path(__file__).resolve().parent, mock_response_file_name)
    with open(mock_file_path, 'r') as json_file:
        return json.load(json_file)

def test_client_init():
    client = FastTradierClient(access_token = account_at, account_id=account_id, is_prod=False)
    assert client is not None

@pytest.mark.asyncio
async def test_option_expirations_call(httpx_mock: HTTPXMock):
    mock_resp = get_mock_response()
    httpx_mock.add_response(json=mock_resp['option_expirations_resp'])

    symbol = 'SPX'
    with httpx.Client() as client:
        tradier_client = FastTradierClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        results = tradier_client.get_option_expirations(symbol=symbol)
        assert len(results) > 0
        assert results[0] == "2023-08-08"
    
    # async test:
    async with httpx.AsyncClient() as client:
        tradier_client = FastTradierAsyncClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        results = await tradier_client.get_option_expirations_async(symbol=symbol)
        assert len(results) > 0
        assert results[0] == "2023-08-08"

@pytest.mark.asyncio
async def test_is_market_open_today(httpx_mock: HTTPXMock):
    today = datetime.now().astimezone(eastern)
    today_str = today.strftime("%Y-%m-%d")
    now_t = arrow.get(f'{today_str} 12:00', 'YYYY-M-D HH:mm', tzinfo=eastern)
    now = now_t.datetime
    tomorrow = now + timedelta(days=1)
    year = now.year
    month = now.month

    mock_json_resp = {
        "calendar": {
            "month": month,
            "year": year,
            "days": {
                "day": []
            }
        }
    }

    days = [now, tomorrow]
    for t in days:
        mock_json_resp["calendar"]["days"]["day"].append({
            "date": f'{t.year}-{t.month}-{t.day}',
            "status": "open",
            "open": {
                "start": "09:30",
                "end": "16:00"
            }
        })
    httpx_mock.add_response(json=mock_json_resp)
    with httpx.Client() as client:
        tradier_client = FastTradierClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        is_open, day_arr, today_open_window = tradier_client.is_market_open_today()
        assert len(day_arr) == len(days)
        assert day_arr[0] == f'{days[0].year}-{days[0].month}-{days[0].day}'
    
    # async test:
    async with httpx.AsyncClient() as client:
        tradier_client = FastTradierAsyncClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        is_open, day_arr, today_open_window = await tradier_client.is_market_open_today_async()
        assert len(day_arr) == len(days)
        assert day_arr[0] == f'{days[0].year}-{days[0].month}-{days[0].day}'

@pytest.mark.asyncio
async def test_get_quotes(httpx_mock: HTTPXMock):
    mock_resp = get_mock_response()
    httpx_mock.add_response(json=mock_resp['quotes_resp'])
    with httpx.Client() as client:
        tradier_client = FastTradierClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        tickers = ['AAPL']
        quotes_list = tradier_client.get_quotes(symbols=tickers)
        assert len(quotes_list) > 0
        assert quotes_list[0].symbol == 'AAPL'
        assert quotes_list[0].type == 'stock'
        assert quotes_list[0].ask == 208.21
    
    # async test:
    async with httpx.AsyncClient() as client:
        tradier_client = FastTradierAsyncClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        tickers = ['AAPL']
        quotes_list = await tradier_client.get_quotes_async(symbols=tickers)
        assert len(quotes_list) > 0
        assert quotes_list[0].symbol == 'AAPL'
        assert quotes_list[0].type == 'stock'
        assert quotes_list[0].ask == 208.21

@pytest.mark.asyncio
async def test_get_order_status(httpx_mock: HTTPXMock):
    mock_resp = get_mock_response()
    httpx_mock.add_response(json=mock_resp['orders_resp'])
    target_order_id = 228175
    with httpx.Client() as client:
        tradier_client = FastTradierClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        order_status = tradier_client.get_order_status(order_id=target_order_id)
        assert order_status == 'expired'
    
    # async test:
    async with httpx.AsyncClient() as client:
        tradier_client = FastTradierAsyncClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        order_status = await tradier_client.get_order_status_async(order_id=target_order_id)
        assert order_status == 'expired'
@pytest.mark.asyncio
async def test_get_option_chain(httpx_mock: HTTPXMock):
    mock_resp = get_mock_response()
    httpx_mock.add_response(json=mock_resp["option_chain_resp"])
    expiration = '2023-08-08'
    symbol = 'VIX'
    with httpx.Client() as client:
        tradier_client = FastTradierClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        result = tradier_client.get_option_chain(symbol=symbol, expiration=expiration)
        assert result["expiration"] == expiration
        assert result["ticker"] == symbol
        assert len(result["call_chain"]) > 0
        assert len(result["put_chain"]) > 0
        call_df, put_df = result["call_chain"], result["put_chain"]
        bid, ask, lastPrice = OptionUtils.find_option_price(option_symbol='VXX190517C00016000', call_df=call_df, put_df=put_df)
        assert bid == 10.85
        assert ask == 11.0
        assert lastPrice == 0
    
    # async test:
    async with httpx.AsyncClient() as client:
        tradier_client = FastTradierAsyncClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        result = await tradier_client.get_option_chain_async(symbol=symbol, expiration=expiration)
        assert result["expiration"] == expiration
        assert result["ticker"] == symbol
        assert len(result["call_chain"]) > 0
        assert len(result["put_chain"]) > 0
        call_df, put_df = result["call_chain"], result["put_chain"]
        bid, ask, lastPrice = OptionUtils.find_option_price(option_symbol='VXX190517C00016000', call_df=call_df, put_df=put_df)
        assert bid == 10.85
        assert ask == 11.0
        assert lastPrice == 0

@pytest.mark.asyncio
async def test_get_account_balance(httpx_mock: HTTPXMock):
    mock_resp = get_mock_response()
    httpx_mock.add_response(json=mock_resp["account_balances_resp"])
    with httpx.Client() as client:
        tradier_client = FastTradierClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        account_balance = tradier_client.get_account_balance()
        assert account_balance is not None
        assert account_balance.account_type == 'margin'
        assert account_balance.margin is not None
        assert account_balance.margin.option_buying_power == 6363.86
    
    # async test:
    async with httpx.AsyncClient() as client:
        tradier_client = FastTradierAsyncClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        account_balance = await tradier_client.get_account_balance_async()
        assert account_balance is not None
        assert account_balance.account_type == 'margin'
        assert account_balance.margin is not None
        assert account_balance.margin.option_buying_power == 6363.86

@pytest.mark.asyncio
async def test_get_account_positions(httpx_mock: HTTPXMock):
    mock_resp = get_mock_response()
    httpx_mock.add_response(json=mock_resp["positions_resp"])
    with httpx.Client() as client:
        tradier_client = FastTradierClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        positions = tradier_client.get_positions()
        assert len(positions) > 0
        assert positions[0].symbol == 'AAPL'
        assert positions[0].cost_basis == 207.01
        assert positions[1].symbol == 'AMZN'
        assert positions[3].symbol == 'FB'
        assert positions[3].cost_basis == 173.04
    
    # async test:
    async with httpx.AsyncClient() as client:
        tradier_client = FastTradierAsyncClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        positions = await tradier_client.get_positions_async()
        assert len(positions) > 0
        assert positions[0].symbol == 'AAPL'
        assert positions[0].cost_basis == 207.01
        assert positions[1].symbol == 'AMZN'
        assert positions[3].symbol == 'FB'
        assert positions[3].cost_basis == 173.04

@pytest.mark.asyncio
async def test_get_account_orders(httpx_mock: HTTPXMock):
    mock_resp = get_mock_response()
    httpx_mock.add_response(json=mock_resp["orders_resp"])
    with httpx.Client() as client:
        tradier_client = FastTradierClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        orders = tradier_client.get_account_orders()
        assert len(orders) == 3
        assert orders[0].symbol == 'AAPL'
        assert orders[0].id == 228175
        assert orders[1].symbol == 'SPY'
        assert len(orders[2].leg) > 0
        assert orders[2].leg[0].id == 229064
        assert orders[2].leg[1].option_symbol == 'SPY180720C00274000'
    
    # async test:
    async with httpx.AsyncClient() as client:
        tradier_client = FastTradierAsyncClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        orders = await tradier_client.get_account_orders_async()
        assert len(orders) == 3
        assert orders[0].symbol == 'AAPL'
        assert orders[0].id == 228175
        assert orders[1].symbol == 'SPY'
        assert len(orders[2].leg) > 0
        assert orders[2].leg[0].id == 229064
        assert orders[2].leg[1].option_symbol == 'SPY180720C00274000'

@pytest.mark.asyncio
async def test_place_order(httpx_mock: HTTPXMock):
    mock_order_id = random.randint(100, 200)
    httpx_mock.add_response(json={
        "order": {
            "status": "ok",
            "id": mock_order_id,
        }
    })

    with httpx.Client() as client:
        tradier_client = FastTradierClient(access_token=account_at, account_id=account_id, is_prod=False, http_client=client)
        order_id = tradier_client.place_option_order(mock_order())
        assert order_id == mock_order_id
    
    # async test:
    async with httpx.AsyncClient() as client:
        tradier_client = FastTradierAsyncClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        order_id = await tradier_client.place_option_order_async(mock_order())
        assert order_id == mock_order_id

@pytest.mark.asyncio
async def test_cancel_order(httpx_mock: HTTPXMock):
    mock_order_id = random.randint(100, 200)
    httpx_mock.add_response(json={
        "order": {
            "status": "ok",
            "id": mock_order_id,
        }
    })

    with httpx.Client() as client:
        tradier_client = FastTradierClient(access_token=account_at, account_id=account_id, is_prod=False, http_client=client)
        is_canceled = tradier_client.cancel_order(mock_order_id)
        assert is_canceled

    # async test:
    async with httpx.AsyncClient() as client:
        tradier_client = FastTradierAsyncClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        is_canceled = await tradier_client.cancel_order_async(mock_order_id)
        assert is_canceled

@pytest.mark.asyncio
async def test_modify_option_order(httpx_mock: HTTPXMock):
    mock_order_id = random.randint(100, 200)
    httpx_mock.add_response(json={
        "order": {
            "status": "ok",
            "id": mock_order_id,
        }
    })
    
    order = mock_order()
    order.id = mock_order_id

    with httpx.Client() as client:
        tradier_client = FastTradierClient(access_token=account_at, account_id=account_id, is_prod=False, http_client=client)
        is_modified = tradier_client.modify_option_order(order)
        assert is_modified
    
    # async test:
    async with httpx.AsyncClient() as client:
        tradier_client = FastTradierAsyncClient(access_token = account_at, account_id=account_id, is_prod=False, http_client=client)
        is_modified = await tradier_client.modify_option_order_async(order)
        assert is_modified