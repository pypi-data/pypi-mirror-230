# flake8: noqa
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from fast_tradier.models.DataClassModelBase import DataClassModelBase
from fast_tradier.models.trading.Duration import Duration
from fast_tradier.models.trading.OptionOrder import OptionLeg, OptionOrder
from fast_tradier.models.trading.PriceTypes import OptionPriceType
from fast_tradier.models.trading.Sides import OptionOrderSide
from fast_tradier.models.trading.TOSTradierConverter import TOSTradierConverter

short_window = int(os.environ.get("SHORT_WINDOW", "8"))
long_window = int(os.environ.get("LONG_WINDOW", "21"))


class MarketDirection(Enum):
    TrendingUp = 1
    TrendingDown = 2
    RangeBound = 3


class BuySellSignal(Enum):
    Buy = 1
    Sell = 2
    StayPut = 3


class OptionType(Enum):
    Put = 1
    Call = 2


class OptionStrategy(Enum):
    CreditCallSpread = 1
    ATMCreditCallSpread = 2

    CreditPutSpread = 3
    ATMCreditPutSpread = 4

    CreditCallSingleLeg = 5
    ATMCreditCallSingleLeg = 6

    CreditPutSingleLeg = 7
    ATMCreditPutSingleLeg = 8

    DebitCallSpread = 9
    ATMDebitCallSpread = 10

    DebitPutSpread = 11
    ATMDebitPutSpread = 12

    DebitCallSingleLeg = 13
    ATMDebitCallSingleLeg = 14

    DebitPutSingleLeg = 15
    ATMDebitPutSingleLeg = 16

    ButterflyCall = 17
    ButterflyPut = 18

    CreditBWButterflyCall = 19
    CreditBWButterflyPut = 20
    DebitBWButterflyCall = 21
    DebitBWButterflyPut = 22
    IronButterfly = 23

    """return a map of matched option strategies to that we don't duplicate the buying power used"""
    # Dict[str, Union[str, List[str]]]
    @classmethod
    def matched_option_strategies_map(
        cls,
    ) -> Dict[OptionStrategy, List[OptionStrategy]]:
        return {
            OptionStrategy.CreditCallSpread: [
                OptionStrategy.CreditPutSpread,
                OptionStrategy.ATMCreditPutSpread,
            ],
            OptionStrategy.ATMCreditCallSpread: [
                OptionStrategy.ATMCreditPutSpread,
                OptionStrategy.CreditPutSpread,
            ],
            OptionStrategy.CreditPutSpread: [
                OptionStrategy.CreditCallSpread,
                OptionStrategy.ATMCreditCallSpread,
            ],
            OptionStrategy.ATMCreditPutSpread: [
                OptionStrategy.ATMCreditCallSpread,
                OptionStrategy.ATMCreditCallSpread,
            ],
        }

    @classmethod
    def credit_spread_strategies(cls) -> List[OptionStrategy]:
        return [
            OptionStrategy.CreditCallSpread,
            OptionStrategy.CreditPutSpread,
            OptionStrategy.ATMCreditCallSpread,
            OptionStrategy.ATMCreditPutSpread,
        ]

    @classmethod
    def debit_spread_strategies(cls) -> List[OptionStrategy]:
        return [
            OptionStrategy.DebitCallSpread,
            OptionStrategy.DebitPutSpread,
            OptionStrategy.ATMDebitCallSpread,
            OptionStrategy.ATMDebitPutSpread,
        ]

    @classmethod
    def debit_butterfly_strategies(cls) -> List[OptionStrategy]:
        return [
            OptionStrategy.ButterflyPut,
            OptionStrategy.ButterflyCall,
            OptionStrategy.DebitBWButterflyCall,
            OptionStrategy.DebitBWButterflyPut,
        ]

    @classmethod
    def credit_butterfly_strategies(cls) -> List[OptionStrategy]:
        # not including IronButterFly, because it has even number of legs
        return [
            OptionStrategy.CreditBWButterflyCall,
            OptionStrategy.CreditBWButterflyPut,
        ]

    @classmethod
    def credit_single_leg_strategies(cls) -> List[OptionStrategy]:
        return [
            OptionStrategy.ATMCreditCallSingleLeg,
            OptionStrategy.ATMCreditPutSingleLeg,
            OptionStrategy.CreditCallSingleLeg,
            OptionStrategy.CreditPutSingleLeg,
        ]

    @classmethod
    def debit_single_leg_strategies(cls) -> List[OptionStrategy]:
        return [
            OptionStrategy.DebitPutSingleLeg,
            OptionStrategy.DebitCallSingleLeg,
            OptionStrategy.ATMDebitCallSingleLeg,
            OptionStrategy.ATMDebitPutSingleLeg,
        ]


class OptionStrikeInfo(object):
    def __init__(
        self,
        underlying_symbol: str,
        option_symbol: str,
        strike: float,
        bid: float,
        ask: float,
        last_price: float,
        option_type: OptionType,
        convert_tos_symbol: bool = True,
    ) -> None:
        self.__underlying_symbol = underlying_symbol
        self.__option_symbol = (
            TOSTradierConverter.tos_to_tradier(option_symbol)
            if convert_tos_symbol
            else option_symbol
        )
        self.__tos_option_symbol = (
            TOSTradierConverter.tradier_to_tos(option_symbol)
            if convert_tos_symbol
            else option_symbol
        )
        self.__strike = strike
        self.__bid = bid
        self.__ask = ask
        self.__last_price = last_price
        self.__option_type = option_type

    @property
    def option_symbol(self) -> str:
        return self.__option_symbol

    @property
    def tos_option_symbol(self) -> str:
        return self.__tos_option_symbol

    @property
    def strike(self) -> float:
        return self.__strike

    @property
    def bid(self) -> float:
        return self.__bid

    @property
    def ask(self) -> float:
        return self.__ask

    @property
    def last_price(self) -> float:
        return self.__last_price

    @property
    def option_type(self) -> OptionType:
        return self.__option_type


@dataclass
class TradierOptionOrderMetadata(DataClassModelBase):
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    predicted_close: Optional[float]
    db_primary_id: Optional[int]

    def __init__(self, json_obj: Dict) -> None:  # type: ignore
        super().__init__(json_obj)


class SimpleOptionChainPair(object):
    def __init__(
        self,
        underlying_symbol: str,
        call_df: pd.DataFrame,
        put_df: pd.DataFrame,
    ) -> None:
        self.__underlying_symbol = underlying_symbol
        self.__call_df = call_df
        self.__put_df = put_df

    @property
    def underlying_symbol(self) -> str:
        return self.__underlying_symbol

    @property
    def call_df(self) -> pd.DataFrame:
        return self.__call_df

    @property
    def put_df(self) -> pd.DataFrame:
        return self.__put_df

    """
        find the latest price from option chain for the option_symbol
        Note: option_symbol could be either TOS or Tradier
        returns bid, ask, lastPrice
    """

    def find_price(self, option_symbol: str) -> Tuple:  # type: ignore
        try:
            option_symbol = option_symbol.upper()
            iloc_idx_call = self.call_df.loc[self.call_df["symbol"] == option_symbol]
            iloc_idx_put = self.put_df.loc[self.put_df["symbol"] == option_symbol]
            target_idx = -1
            target_df = None
            result = (-1, -1, -1)

            if len(iloc_idx_call.index) > 0:
                target_idx = self.call_df.index.get_loc(iloc_idx_call.index[0])
                target_df = self.call_df
            elif len(iloc_idx_put.index) > 0:
                target_idx = self.put_df.index.get_loc(iloc_idx_put.index[0])
                target_df = self.put_df
            else:
                raise Exception("option symbol not found")
        except Exception as ex:
            print(f"exception getting price for option symbol {option_symbol}: {ex} ")

        if target_df is not None:
            bid = target_df.iloc[target_idx]["bid"]
            ask = target_df.iloc[target_idx]["ask"]
            lastPrice = target_df.iloc[target_idx]["lastPrice"]
            if lastPrice == 0:
                # when lastPrice is 0, try to average bid and ask
                lastPrice = np.round(np.mean(bid, ask), 2)
            result = (bid, ask, lastPrice)
        return result


class TradierOptionOrder(OptionOrder):
    def __init__(
        self,
        ticker: str,
        price: float,
        price_type: OptionPriceType,
        duration: Duration,
        option_legs: List[OptionLeg],
        timestamp: Optional[int] = None,
        stop_loss_factor: float = 0.5,
        stop_win_factor: float = 0.8,
        option_strategy: OptionStrategy = OptionStrategy.CreditCallSpread,
        init_stop_loss_hits: int = 0,
        close_status: Optional[str] = None,
        close_order_id: Optional[int] = None,
        meta_data: Optional[TradierOptionOrderMetadata] = None,
    ):
        super().__init__(ticker, price, price_type, duration, option_legs)
        # self.__buying_power_used = price # TODO: needs to be updated by OrderManager, #FIXME: use the actual amount, not price
        self.__timestamp = (
            int(datetime.now().timestamp()) if timestamp is None else timestamp
        )
        self.__stop_loss_factor = stop_loss_factor
        self.__stop_win_factor = stop_win_factor
        self.__option_strategy = option_strategy
        self.__stop_loss_hit_count = init_stop_loss_hits
        self.__close_status = close_status
        self.__close_order_id = close_order_id
        self.__meta_data = meta_data

    @property
    def close_status(self) -> Optional[str]:
        return self.__close_status

    @close_status.setter
    def close_status(self, new_val: str) -> None:
        self.__close_status = new_val

    @property
    def close_order_id(self) -> Optional[int]:
        return self.__close_order_id

    @close_order_id.setter
    def close_order_id(self, new_val: Optional[int]) -> None:
        self.__close_order_id = new_val

    @property
    def metadata(self) -> Optional[TradierOptionOrderMetadata]:
        return self.__meta_data

    @metadata.setter
    def metadata(self, new_value: Dict) -> None:  # type: ignore
        if new_value is not None:
            self.__meta_data = TradierOptionOrderMetadata(new_value)

    # TODO: rename to buying_power_required ?
    @property
    def buying_power_used(self) -> float:
        return self.__buying_power_used

    @buying_power_used.setter
    def buying_power_used(self, new_value: float) -> None:
        self.__buying_power_used = new_value

    @property
    def is_buying_power_released(self) -> bool:
        return (
            self.status
            not in ["open", "pending", "closing", "filled", "partially_filled"]
            or self.close_status == "filled"
        )

    @property
    def waiting_for_fill(self) -> bool:
        return self.status in ["open", "partially_filled", "pending"]

    @property
    def is_filled(self) -> bool:
        return self.status in ["filled", "partially_filled"]

    @property
    def is_closed(self) -> bool:
        return self.close_status == "filled" and self.close_order_id is not None

    @property
    def close_status_needs_confirm(self) -> bool:
        return (
            self.status == "closing"
            and self.close_status != "filled"
            and self.close_order_id is not None
        )

    @property
    def is_open(self) -> bool:
        return self.status.upper() == "OPEN"

    @property
    def is_pending(self) -> bool:
        return self.status.upper() == "PENDING"

    @property
    def is_closing(self) -> bool:
        return self.status.upper() == "CLOSING"

    @property
    def timestamp(self) -> int:
        return self.__timestamp

    @property
    def stop_loss_factor(self) -> float:
        return self.__stop_loss_factor

    @property
    def stop_win_factor(self) -> float:
        return self.__stop_win_factor

    @property
    def option_strategy(self) -> OptionStrategy:
        return self.__option_strategy

    @property
    def stop_loss_hit_count(self) -> int:
        return self.__stop_loss_hit_count

    def increment_stop_loss_hit(self) -> None:
        self.__stop_loss_hit_count += 1

    def tradier_option_symbols(self) -> List[str]:
        return [opt_leg.option_symbol for opt_leg in self.option_legs]

    def flip_price_type(self) -> str:
        """reverse the price_type from credit to debit or vice versa"""
        if self.price_type.lower() == "credit":
            return "debit"
        elif self.price_type.lower() == "debit":
            return "credit"

        return self.price_type

    """
    given the latest call and put option chain. calculates
    the profit amount and its percentage in buying power used
    tuple 0: profit amount, 1: profit vs buying power used
    """

    def profit_info(self, call_df: pd.DataFrame, put_df: pd.DataFrame) -> Tuple:  # type: ignore
        # FIXME: what if the number of legs are not the same for each option symbol. e.g. Butterfly ?
        contract_count = (
            1
            if self.option_legs is None or len(self.option_legs) == 0
            else self.option_legs[0].quantity
        )
        cur_val = 0
        profit_bp_percentage = 0

        # find the option curr price in the dataframe, and calculate the profit vs the price.
        opt_chain_pair = SimpleOptionChainPair(
            underlying_symbol=self.ticker,
            call_df=call_df,
            put_df=put_df,
        )
        min_leg_count = 1
        for opt_leg in self.option_legs:
            min_leg_count = min(min_leg_count, opt_leg.quantity)
            bid, ask, lastPrice = opt_chain_pair.find_price(
                opt_leg.tos_option_symbol,
            )  # TODO: try tos option symbol first, because it queries TOS option chain # FIXME with regex
            if lastPrice == -1:
                # Try tradier option as a backup
                bid, ask, lastPrice = opt_chain_pair.find_price(
                    opt_leg.option_symbol,
                )  # TODO: try both TOS and Tradier option symbols?

            if lastPrice > -1:
                if opt_leg.side == "sell_to_open":
                    cur_val += (
                        lastPrice * opt_leg.quantity
                    )  ### * 100 ??? # FIXME: what if the number of option legs are different int he order ???
                elif opt_leg.side == "buy_to_open":
                    cur_val -= lastPrice * opt_leg.quantity

        profit = 0.0
        if (
            self.option_strategy in OptionStrategy.debit_spread_strategies()
            or self.option_strategy in OptionStrategy.debit_single_leg_strategies()
        ):
            contract_count = self.option_legs[0].quantity
            profit = cur_val - (self.price * contract_count)
        elif (
            self.option_strategy in OptionStrategy.credit_spread_strategies()
            or self.option_strategy
            == self.option_strategy
            == OptionStrategy.IronButterfly
        ):
            contract_count = self.option_legs[0].quantity
            profit = (self.price * contract_count) - cur_val
        elif self.option_strategy in OptionStrategy.debit_butterfly_strategies():
            contract_count = min_leg_count
            profit = cur_val - (self.price * contract_count)
        elif self.option_strategy in OptionStrategy.credit_butterfly_strategies():
            contract_count = min_leg_count
            profit = (self.price * contract_count) - cur_val

        # TODO: make 100.0 a constant
        profit_bp_percentage = profit * 100.0 / self.buying_power_used  # type: ignore
        # profit per contract, needs to be divided by contract_count.
        # FIXME: but what happens to butterfly strategies?
        return np.round(profit / (1.0 * contract_count), 3), np.round(
            profit_bp_percentage,
            3,
        )

    def to_json(self) -> Dict:  # type: ignore
        result = super().to_json()
        # result = {
        #     "id": self.id,
        #     "status": self.status,
        #     "symbol": self.ticker,
        #     "duration": self.duration,
        #     "price": self.price,
        #     "type": self.price_type,
        #     "class": self.order_class,
        # }
        if self.metadata is not None:
            result["metadata"] = self.metadata.to_json()
        return result

    # def __str__(self) -> str:
    #     legs = ""
    #     for i in range(len(self.option_legs)):
    #         opt_leg = self.option_legs[i]
    #         legs += f"leg[{i}]:{opt_leg.option_symbol}({opt_leg.side});"
    #     return f"id:{self.id},price:{self.price}|strategy:{self.option_strategy.name}|legs:[{legs}]"

if __name__ == '__main__':
    ticker = "spx"
    leg_quantity = 1
    price = 1.20
    option_leg1 = OptionLeg(
        underlying_symbol=ticker,
        option_symbol="SPXW_052223C4225",
        side=OptionOrderSide.SellToOpen,
        quantity=leg_quantity,
    )
    option_leg2 = OptionLeg(
        underlying_symbol=ticker,
        option_symbol="SPXW_052223C4235",
        side=OptionOrderSide.BuyToOpen,
        quantity=leg_quantity,
    )
    option_legs = [
        option_leg1,
        option_leg2,
    ]
    stop_loss_factor = 3.0
    stop_win_facotr = 0.5
    meta_data = TradierOptionOrderMetadata(
        {
            "lower_bound": 4100,
            "upper_bound": 4200,
            "predicted_close": 4150,
        },
    )

    order = TradierOptionOrder(
        ticker=ticker,
        price=price,
        price_type=OptionPriceType.Market,
        duration=Duration.Day,
        option_legs=option_legs,
        timestamp=int(datetime.now().timestamp()),
        stop_loss_factor=stop_loss_factor,
        stop_win_factor=stop_win_facotr,
        option_strategy=OptionStrategy.CreditCallSpread,
        close_status='pending',
        close_order_id=100,
        meta_data=meta_data,
    )
    
    print('order.to_json: ', order.to_json())