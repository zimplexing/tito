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