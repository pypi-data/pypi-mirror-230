import asyncio
import logging
import ssl
from datetime import datetime
from typing import Dict, Callable

import certifi
from websockets import connect
import json

from alpcom_api import clients
from alpcom_api.dto import ws as dto


class Handler:
    def on_ticker(self, ticker: dto.Ticker):
        ...

    def on_trade(self, trade: dto.Trade):
        ...

    def on_rate(self, rate: dto.Rate):
        ...

    def on_diff(self, diff: dto.Diff):
        ...

    def on_depth(self, depth: dto.Depth):
        ...

    def on_wallet(self, wallet: dto.Wallet):
        ...

    def on_order(self, order: dto.Order):
        ...


class Client:
    DEFAULT_URL = 'wss://www.alp.com/alp-ws'

    def __init__(self, handler: Handler, server_url: str = None):
        self.handler: Handler = handler
        self.server_url = server_url or self.DEFAULT_URL
        self.websocket = None

        self.routing: Dict[str, Callable] = {
            'tk': self._handle_tickers,
            't': self._handle_trade,
            'r': self._handle_rates,
            'd': self._handle_diff,
            'p': self._handle_depth,
            'w': self._handle_wallet,
            'o': self._handle_order,
        }

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def connect(self):
        ssl_context = ssl.create_default_context()
        ssl_context.load_verify_locations(certifi.where())
        self.websocket = await connect(self.server_url, ssl=ssl_context)

    async def receive_messages(self):
        while True:
            message = await self.websocket.recv()
            print(message)
            # handle ping
            if message == "1":
                await self.websocket.send("2")

            else:
                data: list = json.loads(message)

                if len(data) > 2:
                    handler = self.routing.get(data[0])

                    if handler is not None:
                        handler(*data[1:])

    async def subscribe(self, *topics):
        msg = json.dumps(['subscribe', *topics])
        await self.websocket.send(msg)

    async def auth(self, cli: clients.ALPAuthClient):
        msg = json.dumps(['auth', cli.get_token()])
        await self.websocket.send(msg)

    async def close(self):
        await self.websocket.close()

    def _handle_tickers(self, date: float, *tickers):
        for item in tickers:
            if len(item) < 9:
                logging.exception('Unexpected ticker format', item)
                continue

            self.handler.on_ticker(
                dto.Ticker(
                    symbol=item[0],
                    close=item[1],
                    base_vol=item[2],
                    quote_vol=item[3],
                    change=item[4],
                    high=item[5],
                    low=item[6],
                    bid=item[7],
                    ask=item[8],
                )
            )

    def _handle_trade(self, date: float, trade_id: int, pair: str, amount: str, price: str, direction: str, *args):
        self.handler.on_trade(
            dto.Trade(
                date=date,
                trade_id=trade_id,
                pair=pair,
                amount=amount,
                price=price,
                direction=direction,
            )
        )

    def _handle_rates(self, date: float, rates: list, *args):
        for item in rates:
            if len(item) < 3:
                logging.exception('Unexpected rate format', item)
                continue

            self.handler.on_rate(
                dto.Rate(
                    rate=item[0],
                    base=item[1],
                    quote=item[2],
                )
            )

    def _handle_diff(self, date: float, symbol: str, data: list, *args):
        if len(data) != 2:
            logging.exception('Bad orderbook', date)
            return

        self.handler.on_diff(
            dto.Diff(
                symbol=symbol,
                asks=[dto.BookOrder(price=item[0], amount=item[1]) for item in data[0]],
                bids=[dto.BookOrder(price=item[0], amount=item[1]) for item in data[1]],
            )
        )

    def _handle_depth(self, date: float, depth: dict, *args):
        for key in 'Symbol', 'Asks', 'Bids', 'TotalAsks', 'TotalBids':
            if key not in depth:
                logging.exception(f'Bad market depth, missing param f[{key}]', depth)
                return

        self.handler.on_depth(
            dto.Depth(
                symbol=depth.get('Symbol'),
                asks=[dto.BookOrder(price=item[0], amount=item[1]) for item in depth['Asks']],
                bids=[dto.BookOrder(price=item[0], amount=item[1]) for item in depth['Bids']],
                total_asks=depth.get('TotalAsks'),
                total_bids=depth.get('TotalBids'),
            )
        )

    def _handle_wallet(self, date: float, code: str, wallet_type: str, symbol: str, balance: str, reserve: str):
        wallet = dto.Wallet(
            code=code,
            wallet_type=wallet_type,
            symbol=symbol,
            balance=balance,
            reserve=reserve,
        )
        self.handler.on_wallet(wallet)

    def _handle_order(self, date: float,
                      order_id: int,
                      symbol: str,
                      side: str,
                      order_type: str,
                      base_amount: str,
                      limit_price: str,
                      amount_unfilled: str,
                      amount_filled: str,
                      amount_cancelled: str,
                      value_filled: str,
                      price_avg: str,
                      done_at: float,
                      status: str,
                      quote_amount: str,
                      wallet_type: str,
                      stop_price: str,
                      stop_operator: str):
        order = dto.Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            base_amount=base_amount,
            limit_price=limit_price,
            amount_unfilled=amount_unfilled,
            amount_filled=amount_filled,
            amount_cancelled=amount_cancelled,
            value_filled=value_filled,
            price_avg=price_avg,
            done_at=done_at,
            status=status,
            quote_amount=quote_amount,
            wallet_type=wallet_type,
            stop_price=stop_price,
            stop_operator=stop_operator,
        )

        self.handler.on_order(order)


class Topics:
    tickers_all = "ticker.*"
    trades_all = "trade.*"
    rates_all = "rates.*"

    @classmethod
    def tickers_of(cls, pair: str):
        return f'ticker.{pair}'

    @classmethod
    def trades_of(cls, pair: str):
        return f'trade.{pair}'

    @classmethod
    def rates_of(cls, pair: str):
        return f'rates.{pair}'

    @classmethod
    def diff_of(cls, pair: str):
        return f'diff.{pair}'

    @classmethod
    def depth_of(cls, pair: str):
        return f'market_depth.{pair}'


tps = Topics()
