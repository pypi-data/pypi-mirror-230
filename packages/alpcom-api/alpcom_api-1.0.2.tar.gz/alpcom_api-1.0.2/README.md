# ALP API - official python client for trading platform **ALP.COM**
## Usage

### Initialization

```python
from alpcom_api import factories, cache

public_api = factories.get_public_api()
private_api = factories.get_private_api(
    key='** Your private_api Key **',
    secret='** Your private_api Secret **',
    # Optionally use cache to store temp token
    # otherwise it will be generated every time an instance of HTTPClient gets created
    # cache=cache.FileCache('/path/to/token.txt') 
)
```

### Public data

```python
import time
from alpcom_api import factories, dto

public_api = factories.get_public_api()

currency_list = public_api.currencies()
markets_list = public_api.pairs()
orderbook_btc_usdt = public_api.orderbook(pair='BTC_USDT')
tickers_list = public_api.tickers()
last_trades = public_api.trades(pair='BTC_USDT', limit=10)
candle_list = public_api.charts(
    pair='BTC_USDT',
    interval=dto.ChartInterval.DAY,
    since=int(time.time()) - 60 * 60 * 24 * 10  # last 10 days
)
```


### Accounts API

```python
from alpcom_api import factories, dto

private_api = factories.get_private_api(
    key='** Your private_api Key **',
    secret='** Your private_api Secret **',
)

# Get master account and sub-accounts
private_api.accounts().accounts(include_subaccounts=True)

# Get balances of all accounts
private_api.accounts().balances()

# Get fee info 
private_api.accounts().fees()

# Get own orders by pair
private_api.accounts().orders('ETH_USDT', open_only=True)

# Get trade history
private_api.accounts().trades('ETH_USDT')

# Get wallet motion history
private_api.accounts().history('USDT')
```


### Trading API


```python
from alpcom_api import factories, dto

private_api = factories.get_private_api(
    key='** Your private_api Key **',
    secret='** Your private_api Secret **',
)

# Place different order types
req_limit = dto.LimitOrderRequest(
    pair='ETH_USDT',
    order_side=dto.OrderSide.SELL,
    base_amount=0.05,
    limit_price=1800,
)
req_market = dto.MarketOrderRequest(
    pair='ETH_USDT',
    order_side=dto.OrderSide.SELL,
    base_amount=0.1 # base_amount or quote_amount
)
req_stop_limit = dto.StopLimitOrderRequest(
    pair='ETH_USDT',
    order_side=dto.OrderSide.SELL,
    stop_price=1800,
    stop_operator=dto.StopOperator.GTE,
    base_amount=0.05,
    limit_price=1700,
)

order1_id = private_api.trading().place_order(req_limit)
order2_id = private_api.trading().place_order(req_market)
order3_id = private_api.trading().place_order(req_stop_limit)

# Cancel one order by order id
status = private_api.trading().cancel_order(12312332)

# Cancel multiple orders by order ids
status_dict = private_api.trading().cancel_orders([12312332, 12312334, 12312338])

# Cancel multiple orders by pair
status_dict = private_api.trading().cancel_orders_of_pair('ETH_USDT')

# Cancel all open orders
status_dict = private_api.trading().cancel_all_orders()
```

### Deposit API

```python
from alpcom_api import factories

private_api = factories.get_private_api(
    key='** Your private_api Key **',
    secret='** Your private_api Secret **',
)

# get deposit methods (with attributes to make deposit)
methods = private_api.deposits().methods(currency='USDT')

# get deposit history
deposits = private_api.deposits().history(currency='USDT')
```

### Withdraw API

```python
from alpcom_api import factories, dto

private_api = factories.get_private_api(
    key='** Your private_api Key **',
    secret='** Your private_api Secret **',
)

# get withdraws methods
methods = private_api.withdraws().methods(currency='USDT')

# make withdraw request
req = dto.WithdrawRequest(
    amount=10.0,
    method=2,
    attributes={
        'address': '<my_dest_addr>',
        'memo': '<extra memo>'
    },
    client_order_id='order_123'
)
private_api.withdraws().create(req)

# get withdraws history
withdraws = private_api.withdraws().history(currency='USDT')
```


### Margin API


```python
from alpcom_api import factories, dto

private_api = factories.get_private_api(
    key='** Your private_api Key **',
    secret='** Your private_api Secret **',
)

# make margin transfer
req = dto.MarginTransferRequest(
    account_id=384457,
    wallet_type=dto.WalletType.MARGIN_CROSS,
    direction=dto.MarginDirection.ADD,
    amount=1,
    currency='ETH',
)

operation_id = private_api.margin().transfer(req)

# make borrow
req = dto.BorrowRequest(
    account_id=384457,
    borrow=1,
    currency='ETH',
    wallet_type=dto.WalletType.MARGIN_CROSS,
)

operation_id = private_api.margin().borrow(req)

# repay debt
req = dto.RepayRequest(
    account_id=384457,
    amount=0.03,
    currency='ETH',
    wallet_type=dto.WalletType.MARGIN_CROSS,
)

operation_id = private_api.margin().repay(req)

# close position
private_api.margin().close_position(account_id=384457, wallet_type=dto.WalletType.MARGIN_CROSS)

# Get loans
loans = private_api.margin().loans(cross_margin=True)

# Get transfer history
transfers = private_api.margin().transfers('ETH', start_time=None, end_time=None)

# Get borrow history
borrows = private_api.margin().borrows('ETH', start_time=None, end_time=None)

# Get repay history
repays = private_api.margin().repays('ETH', start_time=None, end_time=None)

# Get interest history
repays = private_api.margin().interests('ETH', start_time=None, end_time=None)

# Get liquidation history
repays = private_api.margin().liquidations('ETH', start_time=None, end_time=None)
```

### Web Socket API

```python
import asyncio
from pprint import pprint

from alpcom_api import ws, clients, cache
from alpcom_api.dto import ws as dto


class MyHandler(ws.Handler):
    def on_ticker(self, ticker: dto.Ticker):
        pprint(ticker)

    def on_trade(self, trade: dto.Trade):
        pprint(trade)

    def on_rate(self, rate: dto.Rate):
        pprint(rate)

    def on_diff(self, diff: dto.Diff):
        pprint(diff)

    def on_depth(self, depth: dto.Depth):
        pprint(depth)

    def on_wallet(self, wallet: dto.Wallet):
        pprint(wallet)

    def on_order(self, order: dto.Order):
        pprint(order)


async def main():
    cli = clients.ALPAuthClient(
        key='**API_KEY**',
        secret='**API_KEY**',
        token_cache=cache.FileCache('dev_token.txt')
    )

    async with ws.Client(handler=MyHandler()) as client:
        await client.auth(cli)
        await client.subscribe(ws.tps.tickers_all, ws.tps.trades_of('ETH_USDT'), ws.tps.diff_of('ETH_USDT'))
        await client.receive_messages()


asyncio.get_event_loop().run_until_complete(main())
```