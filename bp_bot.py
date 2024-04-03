# coding=utf-8
from bpx.bpx import *
from bpx.bpx_pub import *

import time


class TradeBot:

    def __init__(self, data, emit) -> None:
        self.API_KEY = data.get("API_KEY")  # 填入你的api
        self.API_SECRET = data.get("API_SECRET")  # 填入你的api
        self.WISH_VOLUME = int(data.get("WISH_VOLUME"))  # 期望刷的USDC
        self.ITER_NUM = int(data.get("ITER_NUM"))

        self.run_pair = data.get("TRADE_TOKEN")
        self.pair_name = data.get("TRADE_PAIR")
        self.pair_accuracy = int(data.get("PAIR_ACCURACY"))  # 交易对价格精度

        self.MIN_USDC = int(data.get("MIN_USDC"))
        self.MIN_PAIR = int(data.get("MIN_PAIR"))
        self.bpx = BpxClient()
        self.bpx.init(
            api_key=self.API_KEY,
            api_secret=self.API_SECRET,
        )
        self.logger = emit

    def buy_and_sell(self, usdc_available, sol_available, asks_price, bids_price):
        get_diff_price = round(asks_price - bids_price, self.pair_accuracy)
        if get_diff_price == 1 / int(10**self.pair_accuracy):

            if sol_available > 1000:
                self.bpx.ExeOrder(
                    symbol=self.pair_name,
                    side="Ask",
                    orderType="Limit",
                    timeInForce="",
                    quantity=sol_available,
                    price=asks_price,
                )
                self.logger(f"try sell {sol_available} {self.run_pair} at {asks_price}")
                return sol_available * asks_price
            elif usdc_available > 1:

                self.bpx.ExeOrder(
                    symbol=self.pair_name,
                    side="Bid",
                    orderType="Limit",
                    timeInForce="",
                    quantity=int(int(usdc_available / bids_price * 100) / 100),
                    price=bids_price,
                )
                self.logger(f"try buy {usdc_available} USDC at {bids_price}")
                return usdc_available
        else:

            if sol_available > 1000:
                asks_price = asks_price - 1 / int(10**self.pair_accuracy)

                self.bpx.ExeOrder(
                    symbol=self.pair_name,
                    side="Ask",
                    orderType="Limit",
                    timeInForce="",
                    quantity=sol_available,
                    price=round(asks_price, self.pair_accuracy),
                )

                self.logger(f"try sell {sol_available} {self.run_pair} at {asks_price}")
                return sol_available * asks_price
            elif usdc_available > 1:
                bids_price = bids_price + 1 / int(10**self.pair_accuracy)

                self.bpx.ExeOrder(
                    symbol=self.pair_name,
                    side="Bid",
                    orderType="Limit",
                    timeInForce="",
                    quantity=int(int(usdc_available / bids_price * 100) / 100),
                    price=round(bids_price, self.pair_accuracy),
                )

                self.logger(f"try buy {usdc_available} USDC at {bids_price}")
                return usdc_available
        return 0

    def one_trade(self, usdc_available, sol_available):
        start_time = time.time()
        sol_market_depth1 = Depth(self.pair_name)
        sol_market_depth2 = Depth(self.pair_name)
        end_time = time.time()
        elapsed_time = end_time - start_time

        # self.logger(account_balance)
        asks_depth1 = round(float(sol_market_depth1["asks"][0][1]), self.pair_accuracy)
        bids_depth1 = round(float(sol_market_depth1["bids"][-1][1]), self.pair_accuracy)
        # self.logger(asks_depth1,bids_depth1)
        asks_depth2 = round(float(sol_market_depth2["asks"][0][1]), self.pair_accuracy)
        # asks_price2 = round(float(sol_market_depth2["asks"][0][0]), pair_accuracy)
        bids_depth2 = round(float(sol_market_depth2["bids"][-1][1]), self.pair_accuracy)
        # bids_price2 = round(float(sol_market_depth2["bids"][-1][0]), pair_accuracy)
        # self.logger(asks_depth2,bids_depth2)
        ask_quick_market = 0
        bid_quick_market = -1
        if (asks_depth1 - asks_depth2) / elapsed_time * 5 > asks_depth2:
            ask_quick_market += 1
        if (bids_depth1 - bids_depth2) / elapsed_time * 5 > bids_depth2:
            bid_quick_market -= 1
        # self.logger(f"The time difference is {elapsed_time} seconds")

        asks_price = round(
            float(sol_market_depth2["asks"][ask_quick_market][0]), self.pair_accuracy
        )
        bids_price = round(
            float(sol_market_depth2["bids"][bid_quick_market][0]), self.pair_accuracy
        )
        try:
            vol = self.buy_and_sell(
                usdc_available, sol_available, asks_price, bids_price
            )
        except:
            vol = -1
            self.logger("发送交易时发生错误")
        return vol

    def one_iter(self):
        wish_vol = self.WISH_VOLUME

        wish_vol = wish_vol  # 期望刷的量，单位USDC

        begin_vol = int(wish_vol)
        run_time = time.time()
        account_balance = self.bpx.balances()
        # 获取余额
        try:
            begin_usdc_available = float(account_balance["USDC"]["available"])
        except:
            begin_usdc_available = 0

        try:
            begin_sol_available = float(account_balance[self.run_pair]["available"])
        except:
            begin_sol_available = 0
        if begin_usdc_available < 5 and begin_usdc_available < 0.02:
            self.bpx.ordersCancel(self.pair_name)
            account_balance = self.bpx.balances()
            # 获取余额
            begin_usdc_available = (
                int(float(account_balance["USDC"]["available"]) * 100) / 100
            )
            begin_sol_available = (
                int(float(account_balance[self.run_pair]["available"]) * 100) / 100
            )
        self.logger(f"初始USDC余额：{begin_usdc_available} USDC")
        self.logger(f"初始{self.run_pair}余额：{begin_sol_available} {self.run_pair}")

        last_error = False
        while wish_vol > 0:
            account_balance = self.bpx.balances()
            # 获取余额
            usdc_available = (
                int(float(account_balance["USDC"]["available"]) * 100) / 100
            )
            try:
                sol_available = (
                    int(float(account_balance[self.run_pair]["available"]) * 100) / 100
                )
            except:
                sol_available = 0
            self.logger(f"当前USDC余额：{usdc_available} USDC")
            self.logger(f"当前{self.run_pair}余额：{sol_available} {self.run_pair}")
            if usdc_available < 1 and sol_available < 0.02:
                order = self.bpx.ordersQuery(self.pair_name)
                now_time = time.time()
                if order and now_time - run_time > 5:
                    self.bpx.ordersCancel(self.pair_name)
                    unfinish_vol = 0
                    for each_order in order:
                        unfinish_vol += (
                            float(each_order["quantity"])
                            - float(each_order["executedQuoteQuantity"])
                        ) * float(each_order["price"])
                    wish_vol += unfinish_vol
                    self.logger(f"取消未成交订单 {unfinish_vol} USDC")
                self.logger("go on")
                continue
            run_time = time.time()
            vol = self.one_trade(
                usdc_available=round(
                    min(self.MIN_USDC, usdc_available - 1), self.pair_accuracy
                ),
                sol_available=int(min(self.MIN_PAIR, sol_available - 0.1)),
            )
            wish_vol -= vol

        order = self.bpx.ordersQuery(self.pair_name)
        self.bpx.ordersCancel(self.pair_name)
        unfinish_vol = 0
        for each_order in order:
            unfinish_vol += (float(each_order["executedQuoteQuantity"])) * float(
                each_order["price"]
            )
        wish_vol += unfinish_vol
        self.logger(f"刷量结束，共刷{begin_vol - wish_vol} USDC")
        account_balance = self.bpx.balances()
        # 获取余额
        final_usdc_available = float(account_balance["USDC"]["available"])
        final_sol_available = float(account_balance[self.run_pair]["available"])
        self.logger(f"最终USDC余额：{final_usdc_available} USDC")
        self.logger(f"最终{self.run_pair}余额：{final_sol_available} {self.run_pair}")
        final_depth = Depth(self.pair_name)
        price = round(float(final_depth["bids"][-1][0]), self.pair_accuracy)
        wear = round(
            price * (begin_sol_available - final_sol_available)
            + begin_usdc_available
            - final_usdc_available,
            6,
        )
        wear_ratio = round(wear / (begin_vol - wish_vol), 6)
        self.logger(f"本次刷量磨损 {wear} USDC, 磨损率 {wear_ratio}")
