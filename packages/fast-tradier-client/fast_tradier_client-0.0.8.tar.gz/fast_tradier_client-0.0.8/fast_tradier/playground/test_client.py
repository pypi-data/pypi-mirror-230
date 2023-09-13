from fast_tradier.FastTradierAsyncClient import FastTradierAsyncClient
from fast_tradier.FastTradierClient import FastTradierClient
from fast_tradier.utils.YFinanceQuoteProvider import YFinanceQuoteProvider
from fast_tradier.models.market_data.Quote import Quote
from fast_tradier.models.trading.OptionOrder import OptionLeg, OptionOrder
from fast_tradier.models.trading.EquityOrder import EquityOrder
from fast_tradier.models.trading.Sides import OptionOrderSide, EquityOrderSide
from fast_tradier.models.trading.PriceTypes import OptionPriceType, EquityPriceType
from fast_tradier.models.trading.Duration import Duration

from pathlib import Path
import asyncio
import json


#TODO: replace the client_id and sandbox access token with yours
sandbox_client_id = 'VA7432928'
sandbox_at = 'dzAxKy3Ss7WxnWEspj0wVvktzUuJ'
yfin_real_quote_provider = YFinanceQuoteProvider()

def mock_order() -> OptionOrder:
    ticker = 'SPX'
    order_status = 'pending'
    option_symbols = ['SPXW_091523C4510', 'SPXW_091523C4520'] #TODO: replace option symbols
    sides = [OptionOrderSide.SellToOpen, OptionOrderSide.BuyToOpen]
    option_legs = []

    for i in range(len(sides)):
        opt_symbol = option_symbols[i]
        side = sides[i]
        option_legs.append(OptionLeg(underlying_symbol=ticker, option_symbol=opt_symbol, side=side, quantity=1))

    option_order = OptionOrder(ticker=ticker,
                            price=3.2,
                            price_type=OptionPriceType.Credit,
                            duration=Duration.Day,
                            option_legs=option_legs)
    return option_order

def mock_equity_order() -> EquityOrder:
    symbol = 'SPY'
    price = 379.0
    quantity = 1.0
    return EquityOrder(ticker=symbol, quantity=quantity, price=price, side=EquityOrderSide.Buy, price_type=EquityPriceType.Limit, duration=Duration.Gtc)

async def async_test():
    tasks = []
    count = 4
    tradier_client = FastTradierAsyncClient(sandbox_at, sandbox_client_id, is_prod=False, real_time_quote_provider=yfin_real_quote_provider)

    # quote1 = await tradier_client.get_quotes_async(['MSFT'])
    # print('quote1 last price: ', quote1[0].last)

    for i in range(count):
        m_order = mock_order()
        cloned_legs = m_order.clone_option_legs()
        assert cloned_legs[0].option_symbol == m_order.option_legs[0].option_symbol
        assert cloned_legs[0].side == m_order.option_legs[0].side
        tasks.append(asyncio.ensure_future(tradier_client.place_option_order_async(m_order)))

    order_ids = await asyncio.gather(*tasks)
    cancel_tasks = []
    for order_id in order_ids:
        print('order_id: ', order_id)
        cancel_tasks.append(asyncio.ensure_future(tradier_client.cancel_order_async(order_id)))

    is_canceled = await asyncio.gather(*cancel_tasks)
    for canceled in is_canceled:
        print('canceled? ', canceled)
    ### test equity order:
    equity_order = mock_equity_order()
    order_id = await tradier_client.place_equity_order_async(equity_order)
    print('equity order id: ', order_id)
    equity_order_canceled = await tradier_client.cancel_order_async(order_id)
    print('equity order canceld? ', equity_order_canceled)
    ### get option chain for spx
    ticker = 'spx'
    expiration = '2023-08-31' #TODO: replace the expiration date
    opt_chain_result = await tradier_client.get_option_chain_async(symbol=ticker, expiration=expiration)
    print('result of option chain: ', opt_chain_result)
    positions = await tradier_client.get_positions_async()
    print('positions: ', positions)
    exps = await tradier_client.get_option_expirations_async(symbol=ticker)
    print(f'ticker: {ticker} has exps: {exps}')

    print('------' * 10)
    balances = await tradier_client.get_account_balance_async()
    print('balances: ', balances.total_cash)
    account_orders = await tradier_client.get_account_orders_async()
    print('account orders count: ', len(account_orders))
    orders_json = []
    for acc in account_orders:
        print('acc: ', acc.to_json())
        orders_json.append(acc.to_json())
    json_file = Path(Path(__file__).resolve().parent, "orders_json.json")
    with open(json_file, 'w') as fp:
        fp.write(json.dumps(orders_json))

    if hasattr(balances, 'dt') and balances.pdt is not None:
        print('balances.pdt.to_json(): ', balances.pdt.to_json())
    elif hasattr(balances, 'margin') and balances.margin is not None:
        print('balances.margin.to_json: ', balances.margin.to_json())
    elif hasattr(balances, 'cash') and balances.cash is not None:
        print('balances.cash.to_json: ', balances.cash.to_json())

def sync_test():
    count = 4
    tradier_client = FastTradierClient(sandbox_at, sandbox_client_id, is_prod=False, real_time_quote_provider=yfin_real_quote_provider)
    # quote1 = tradier_client.get_quotes(['MSFT'])
    # print('quote1 last price: ', quote1[0].last)
    
    # m_order = mock_order()
    # cloned_legs = m_order.clone_option_legs()
    # assert cloned_legs[0].option_symbol == m_order.option_legs[0].option_symbol
    # assert cloned_legs[0].side == m_order.option_legs[0].side

    # order_id = tradier_client.place_option_order(m_order)
    # print('option order id: ', order_id)
    # order_status = tradier_client.get_order_status(order_id=order_id)
    # print(f'order_status: {order_status} for order_id: {order_id}')
    # canceled_order = tradier_client.cancel_order(order_id)
    # print('canceled order? ', canceled_order)
    
    # print('-------' * 10)
    # ### test equity order:
    # equity_order = mock_equity_order()
    # order_id = tradier_client.place_equity_order(equity_order)
    # print('equity order id: ', order_id)
    # equity_order_canceled = tradier_client.cancel_order(order_id)
    # print('equity order canceld? ', equity_order_canceled)

    # ### get option chain for spx
    # ticker = 'spx'
    # expiration = '2023-08-31' #TODO: replace the expiration date
    # opt_chain_result = tradier_client.get_option_chain(symbol=ticker, expiration=expiration)
    # print('result of option chain: ', opt_chain_result)
    # exps = tradier_client.get_option_expirations(symbol=ticker)
    # print(f'ticker: {ticker} has exps: {exps}')
    # positions = tradier_client.get_positions()
    # print('positions: ', positions)

    print('------' * 10)
    balances = tradier_client.get_account_balance()
    print('balances: ', balances.total_cash)
    if hasattr(balances, 'dt') and balances.pdt is not None:
        print('balances.pdt.to_json(): ', balances.pdt.to_json())
    elif hasattr(balances, 'margin') and balances.margin is not None:
        print('balances.margin.to_json: ', balances.margin.to_json())
    elif hasattr(balances, 'cash') and balances.cash is not None:
        print('balances.cash.to_json: ', balances.cash.to_json())

asyncio.run(async_test())
print('-------finished async tests--------')
# sync_test()
print('-------finished sync tests-------')