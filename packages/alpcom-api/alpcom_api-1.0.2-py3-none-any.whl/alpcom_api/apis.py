from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Union, Dict, Optional

from alpcom_api import clients
from alpcom_api.dto import api as dto
from alpcom_api.dto import constants as dto_const
from alpcom_api.dto import constants
from alpcom_api.errors import ApiError


class APIMixin:
    @classmethod
    def clean(cls, **kwargs) -> dict:
        result = {}

        if isinstance(kwargs.get('start_time'), datetime) and isinstance(kwargs.get('end_time'), datetime):
            if (kwargs['end_time'] - kwargs['start_time']) > timedelta(days=30):
                raise ValueError('Max time interval is 30 days')

        for key, val in kwargs.items():
            if val is None:
                continue

            if isinstance(val, datetime):
                result[key] = val.replace(microsecond=0, tzinfo=timezone.utc).isoformat()
            elif isinstance(val, Decimal):
                result[key] = str(val)
            elif isinstance(val, int):
                result[key] = int(val)
            else:
                result[key] = val

        return result


class ALPPublicApi(APIMixin):
    def __init__(self, client: clients.ALPClient):
        self._client = client

    def currencies(self) -> List[dto.Currency]:
        raw_result = self._client.get('currencies', {})
        return [dto.Currency(**item) for item in (raw_result or [])]

    def pairs(self, currency1: str = None, currency2: str = None) -> List[dto.Pair]:
        raw_result = self._client.get('pairs', self.clean(currency1=currency1, currency2=currency2))
        return [dto.Pair(**item) for item in (raw_result or [])]

    def orderbook(self, pair: str,
                  group: int = None,
                  limit_buy: int = None,
                  limit_sell: int = None) -> dto.Orderbook:
        raw_result = self._client.get(
            'order_book',
            self.clean(pair=pair, group=group, limit_buy=limit_buy, limit_sell=limit_sell)
        )
        return dto.Orderbook(**raw_result)

    def ticker(self, pair: str = None, pair_id: int = None) -> dto.Ticker:
        raw_result = self._client.get('ticker', self.clean(pair=pair, pair_id=pair_id))
        return dto.Ticker(**raw_result)

    def tickers(self, limit: int = None, offset: int = None) -> List[dto.Ticker]:
        raw_result = self._client.get('ticker', self.clean(limit=limit, offset=offset))
        return [dto.Ticker(**item) for item in (raw_result or [])]

    def charts(self, pair: str,
               interval: constants.ChartInterval,
               since: int,
               until: int = None,
               limit: int = None) -> List[dto.Candle]:
        raw_result = self._client.get(
            'charts',
            self.clean(pair=pair, interval=interval, since=since, until=until, limit=limit)
        )
        return [dto.Candle(**item) for item in (raw_result or [])]

    def trades(self, pair: str = None, limit: int = None, offset: int = None) -> List[dto.Trade]:
        raw_result = self._client.get('trades', self.clean(pair=pair, limit=limit, offset=offset))
        return [dto.Trade(**item) for item in (raw_result or [])]


class BasePrivateApi(APIMixin):
    def __init__(self, client: clients.ALPAuthClient):
        self._client = client


class ALPPrivateApi(BasePrivateApi):
    def version(self):
        return self._client.get('version', {})

    def accounts(self) -> "AccountsApi":
        return AccountsApi(client=self._client)

    def deposits(self) -> "DepositApi":
        return DepositApi(client=self._client)

    def withdraws(self) -> "WithdrawApi":
        return WithdrawApi(client=self._client)

    def trading(self) -> "TradingApi":
        return TradingApi(client=self._client)

    def margin(self) -> "MarginApi":
        return MarginApi(client=self._client)


class AccountsApi(BasePrivateApi):
    def accounts(self, include_subaccounts: bool = False) -> List[dto.Account]:
        data = self.clean(include_subaccounts=include_subaccounts)
        raw_result = self._client.get('accounts/accounts', data)
        return [dto.Account(**item) for item in (raw_result or [])]

    def balances(self, currency: str = None) -> List[dto.Balance]:
        data = self.clean(currency=currency)
        raw_result = self._client.get('accounts/balances', data)
        return [dto.Balance(**item) for item in (raw_result or [])]

    def fees(self) -> List[dto.AccountFee]:
        raw_result = self._client.get('accounts/feeinfo', {})
        return [dto.AccountFee(**item) for item in (raw_result or [])]

    def orders(self, pair: str,
               open_only: bool = None,
               side: str = None,
               start_time: datetime = None,
               end_time: datetime = None) -> List[dto.Order]:
        data = self.clean(pair=pair, open_only=open_only, side=side, start_time=start_time, end_time=end_time)
        raw_result = self._client.get('accounts/order', data)
        return [dto.Order(**item) for item in (raw_result or [])]

    def trades(self, pair: str,
               side: dto.OrderSide = None,
               start_time: datetime = None,
               end_time: datetime = None) -> List[dto.AccountTrade]:
        data = self.clean(pair=pair, side=side, start_time=start_time, end_time=end_time)
        raw_result = self._client.get('accounts/trades', data)
        return [dto.AccountTrade(**item) for item in (raw_result or [])]

    def history(self, currency: str,
                start_time: datetime = None,
                end_time: datetime = None) -> List[dto.WalletMotion]:
        data = self.clean(currency=currency, start_time=start_time, end_time=end_time)
        raw_result = self._client.get('accounts/activity', data)
        return [dto.WalletMotion(**item) for item in (raw_result or [])]


class DepositApi(BasePrivateApi):
    def methods(self, currency: str) -> List[dto.DepositMethod]:
        raw_result = self._client.get('deposit/methods', data=self.clean(currency=currency))
        return [dto.DepositMethod(**item) for item in (raw_result or [])]

    def history(self, currency: str = None,
                start_time: datetime = None,
                end_time: datetime = None) -> List[dto.Deposit]:
        data = self.clean(currency=currency, start_time=start_time, end_time=end_time)
        raw_result = self._client.get('deposit', data)
        return [dto.Deposit(**item) for item in (raw_result or [])]


class WithdrawApi(BasePrivateApi):
    def methods(self, currency: str) -> List[dto.WithdrawMethod]:
        raw_result = self._client.get('withdraw/methods', data=self.clean(currency=currency))
        return [dto.WithdrawMethod(**item) for item in (raw_result or [])]

    def create(self, req: dto.WithdrawRequest) -> bool:
        return self._client.json('withdraw', req.model_dump(mode='json', exclude_none=True))

    def history(self, currency: str = None,
                start_time: datetime = None,
                end_time: datetime = None) -> List[dto.Withdraw]:
        data = self.clean(currency=currency, start_time=start_time, end_time=end_time)
        raw_result = self._client.get('withdraw', data)
        return [dto.Withdraw(**item) for item in (raw_result or [])]


class TradingApi(BasePrivateApi):
    def place_order(self, req: Union[dto.LimitOrderRequest, dto.MarketOrderRequest, dto.StopLimitOrderRequest]) -> int:
        result = self._client.json('trading/order', req.model_dump(mode='json', exclude_none=True))

        if isinstance(result, list) and len(result) == 1:
            return result[0]

        elif isinstance(result, str):
            raise ApiError(result)

        else:
            raise ApiError(str(result))

    def cancel_order(self, order_id: int) -> Optional[str]:
        return self.cancel_orders([order_id]).get(order_id)

    def cancel_orders_of_pair(self, pair: str) -> Dict[int, str]:
        result = self._client.json('trading/order', {'pair': pair}, method='DELETE')
        return {int(str_oid): status for str_oid, status in (result or {}).items()}

    def cancel_all_orders(self) -> Dict[int, str]:
        result = self._client.json('trading/order', {'all': True}, method='DELETE')
        return {int(str_oid): status for str_oid, status in (result or {}).items()}

    def cancel_orders(self, orders: List[int]) -> Dict[int, str]:
        result = self._client.json('trading/order', {'order_ids': orders}, method='DELETE')
        return {int(str_oid): status for str_oid, status in (result or {}).items()}


class MarginApi(BasePrivateApi):
    def transfer(self, req: dto.MarginTransferRequest) -> int:
        """
        Transfer money between spot and margin wallets
        :rtype: Operation id <int>
        """

        result = self._client.json(
            'margin/transfer',
            req.model_dump(mode='json', exclude_none=True)
        )
        return int(result)

    def borrow(self, req: dto.BorrowRequest) -> int:
        """
        Borrow money
        :rtype: Operation id <int>
        """

        result = self._client.json(
            'margin/borrow',
            req.model_dump(mode='json', exclude_none=True)
        )
        return int(result)

    def repay(self, req: dto.RepayRequest) -> int:
        """
        Borrow money
        :rtype: Operation id <int>
        """

        result = self._client.json(
            'margin/repay',
            req.model_dump(mode='json', exclude_none=True)
        )
        return int(result[0])

    def close_position(self, account_id: int,
                       wallet_type: constants.WalletType,
                       pair: str = ''):
        result = self._client.json(
            'margin',
            {'account_id': account_id, 'wallet_type': wallet_type, 'pair': pair},
            method='DELETE'
        )
        return result

    def loans(self, isolated_margin: bool = None, cross_margin: bool = None) -> List[dto.Loan]:
        if isolated_margin and cross_margin or (not isolated_margin and not cross_margin):
            raise AttributeError('Either isolated_margin or cross_margin must be set')

        data = self.clean(isolated_margin=isolated_margin, cross_margin=cross_margin)
        raw_result = self._client.get('margin', data)
        return [dto.Loan(**item) for item in (raw_result or [])]

    def transfers(self, currency: str,
                  pair: str = '',
                  start_time: datetime = None,
                  end_time: datetime = None) -> List[dto.MarginTransfer]:
        data = self.clean(pair=pair, currency=currency, start_time=start_time, end_time=end_time)
        raw_result = self._client.get('margin/transfer', data)
        return [dto.MarginTransfer(**item) for item in (raw_result or [])]

    def borrows(self, currency: str,
                pair: str = '',
                open_only: bool = None,
                start_time: datetime = None,
                end_time: datetime = None) -> List[dto.Borrow]:
        data = self.clean(pair=pair, currency=currency, open_only=open_only, start_time=start_time, end_time=end_time)
        raw_result = self._client.get('margin/borrow', data)
        return [dto.Borrow(**item) for item in (raw_result or [])]

    def repays(self, currency: str,
               pair: str = '',
               start_time: datetime = None,
               end_time: datetime = None) -> List[dto.Repay]:
        data = self.clean(pair=pair, currency=currency, start_time=start_time, end_time=end_time)
        raw_result = self._client.get('margin/repay', data)
        return [dto.Repay(**item) for item in (raw_result or [])]

    def interests(self, currency: str,
                  pair: str = '',
                  start_time: datetime = None,
                  end_time: datetime = None) -> List[dto.Interest]:
        data = self.clean(pair=pair, currency=currency, start_time=start_time, end_time=end_time)
        raw_result = self._client.get('margin/interest', data)
        return [dto.Interest(**item) for item in (raw_result or [])]

    def liquidations(self, currency: str,
                     pair: str = '',
                     open_only: bool = None,
                     start_time: datetime = None,
                     end_time: datetime = None) -> List[dto.Liquidation]:
        data = self.clean(pair=pair, currency=currency, open_only=open_only, start_time=start_time, end_time=end_time)
        raw_result = self._client.get('margin/liquidation', data)
        return [dto.Liquidation(**item) for item in (raw_result or [])]
