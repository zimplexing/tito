from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

class Tito(bt.Indicator):
    lines = ('tito_line',)

    def __init__(self, data):
        n = 0
        res_1 = self.tito_next(data, -1 + n)
        res_2 = self.tito_next(data, -2 + n)
        res_3 = self.tito_next(data, -3 + n)
        res_4 = self.tito_next(data, -4 + n)
        res_5 = self.tito_next(data, -5 + n)
        res_6 = self.tito_next(data, -6 + n)
        res_7 = self.tito_next(data, -7 + n)
        res_8 = self.tito_next(data, -8 + n)
        res_9 = self.tito_next(data, -9 + n)
        res_10 = self.tito_next(data, -10 + n)
        res_11 = self.tito_next(data, -11 + n)
        res_12 = self.tito_next(data, -12 + n)
        ret = bt.And(bt.Or(res_1, res_2, res_3, res_4, res_5, res_6, res_7, res_8, res_9, res_10, res_11, res_12),
                     self.tito_pre(data, 0))
        print('tito_line', ret)
        self.lines.tito_line = ret

    def tito_pre(self, source, pre_days):
        if pre_days == 0:
            return bt.And(source.close(pre_days) > source.close(pre_days - 1),
                          source.close(pre_days) > source.close(pre_days - 2))
        if pre_days % 2 == 0:
            return bt.And(self.tito_pre(source, pre_days + 1),
                          bt.And(source.close(pre_days) <= source.close(pre_days - 1),
                                 source.close(pre_days) >= source.close(pre_days - 2)))
        else:
            return bt.And(self.tito_pre(source, pre_days + 1),
                          bt.And(source.close(pre_days) >= source.close(pre_days - 1),
                                 source.close(pre_days) <= source.close(pre_days - 2)))

    def tito_next(self, source, pre_days):
        if pre_days == 0:
            return bt.And(source.close(pre_days) < source.close(pre_days - 1),
                          source.close(pre_days) < source.close(pre_days - 2))
        if pre_days % 2 != 0:
            return bt.And(self.tito_pre(source, pre_days + 1),
                          bt.And(source.close(pre_days) >= source.close(pre_days - 1),
                                 source.close(pre_days) <= source.close(pre_days - 2)))
        else:
            return bt.And(self.tito_pre(source, pre_days + 1),
                          bt.And(source.close(pre_days) <= source.close(pre_days - 1),
                                 source.close(pre_days) >= source.close(pre_days - 2)))

# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.tito = Tito(data=self.data)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.tito == 1:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.dataclose[0] > self.buyprice * 1.1 or self.dataclose[0] < self.buyprice * 0.9:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    data = bt.feeds.GenericCSVData(
      dataname='./data/AAPL.csv',
      fromdate=datetime.datetime(2020, 5, 12),
      todate = datetime.datetime(2021, 5, 12),
      dtformat='%Y-%m-%d',
      datetime=0,
      open=1,
      high=2,
      low=3,
      close=4,
      volume=6
  )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(50000)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.AllInSizer, percents = 100)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot()