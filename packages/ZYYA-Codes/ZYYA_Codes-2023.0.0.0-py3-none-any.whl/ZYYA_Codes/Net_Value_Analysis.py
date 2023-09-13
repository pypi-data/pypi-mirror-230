# -*- coding: utf-8 -*-
"""
@Time ： 2023/9/12 21:37
@Auth ： Alan Gong
@File ：Net_Value_Analysis.py
@IDE ：PyCharm
"""
import pandas as _pd
import numpy as _np
import datetime


class RiskIndex:
    def __init__(self, df: _pd.DataFrame, **kwargs):
        self.Table = df.copy().sort_index(ascending=True)
        self.Table.index = [_pd.to_datetime(x).date() for x in self.Table.index]
        self.Table = self.Table[
            (self.Table.index >= _pd.to_datetime(kwargs.get("start", "19990218")).date())
            &
            (self.Table.index <= _pd.to_datetime(kwargs.get("end", "22180218")).date())
            ].rename_axis("日期", axis=0)
        self.date = max(self.Table.index)

    def Unified_NV(self, **kwargs):
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        table = self.Table[self.Table.index >= start]
        start_date = (table > 0).sort_index(ascending=True).idxmax()
        Initial_NV = {x: table[x][y] for x, y in start_date.to_dict().items()}
        return table / Initial_NV

    def Correlation(self, **kwargs):
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        table = self.Table[self.Table.index >= start]
        return table.pct_change().corr(method="spearman")

    def Annual_Return(self, **kwargs) -> _pd.Series:
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        table = self.Table[self.Table.index >= start]
        return _np.exp(_np.log(table.pct_change() + 1).mean() * 365 / 7) - 1

    def Annual_Volatility(self, **kwargs) -> _pd.Series:
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        table = self.Table[self.Table.index >= start]
        return _np.log(table.pct_change() + 1).std() * (365 / 7) ** 0.5

    def Annual_Downward_Volatility(self, **kwargs) -> _pd.Series:
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        table = self.Table[self.Table.index >= start]
        pct_change = table.pct_change().where(table.pct_change() < 0)
        return _np.log(pct_change + 1).std() * (365 / 7) ** 0.5

    def Max_Return(self, **kwargs):
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        table = self.Table[self.Table.index >= start]
        return table.pct_change().where(table.pct_change() > 0, 0).max()

    def Max_Loss(self, **kwargs):
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        table = self.Table[self.Table.index >= start]
        return table.pct_change().where(table.pct_change() < 0, 0).min()

    def Maximum_Drawdown(self, **kwargs) -> _pd.Series:
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        table = self.Table[self.Table.index >= start]
        return - _pd.DataFrame(
            {date: table.loc[date] / table[table.index <= date].max() - 1 for date in table.index}
        ).T.min()

    def No_New_High_Period(self, **kwargs) -> _pd.Series:
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        table = self.Table[self.Table.index >= start]
        return _pd.DataFrame(
            {date: date - table[table.index <= date].idxmax() for date in table.index}
        ).T.max()

    def Drawdown_Recover_Period(self, **kwargs) -> _pd.Series:
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        table = self.Table[self.Table.index >= start]
        delta = - _pd.DataFrame(
            {date: table.loc[date] / table[table.index <= date].max() - 1 for date in table.index}
        ).T
        return delta

    def Sharpe_Ratio(self, **kwargs) -> _pd.Series:
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        return self.Annual_Return(start=start) / self.Annual_Volatility(start=start)

    def Sortino_Ratio(self, **kwargs) -> _pd.Series:
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        return self.Annual_Return(start=start) / self.Annual_Downward_Volatility(start=start)

    def Calmar_Ratio(self, **kwargs) -> _pd.Series:
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        return self.Annual_Return(start=start) / self.Maximum_Drawdown(start=start)

    def Start_Date(self) -> _pd.Series:
        return (self.Table > 0).sort_index(ascending=True).idxmax()

    def End_Date(self) -> _pd.Series:
        return (self.Table > 0).sort_index(ascending=False).idxmax()

    def Latest_NV(self) -> _pd.Series:
        return _pd.Series({x: self.Table[x][y] for x, y in self.End_Date().to_dict().items()})

    def Return_YTM(self, delta=0):
        if self.Table.index.min() <= _pd.to_datetime("%s1231" % (self.date.year - delta)).date():
            start = max(
                self.Table[
                    self.Table.index <= _pd.to_datetime("%s1231" % (self.date.year - delta - 1)).date()
                    ].index.tolist() +
                [self.Table.index.min()]
            )
            table = self.Table[
                (self.Table.index >= start)
                &
                (self.Table.index <= _pd.to_datetime("%s1231" % (self.date.year - delta)).date())
                ]
            return _np.exp(_np.log(table.pct_change() + 1).mean() * 52) - 1
        else:
            return _pd.Series({x: float("nan") for x in self.Table.columns})

    def Return_Period(self, weeks=1):
        table = self.Table.tail(weeks + 1)
        return _np.exp(_np.log(table.pct_change() + 1).sum()) - 1

    def Success(self, **kwargs):
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        table = self.Table[self.Table.index >= start]
        return (table.pct_change() > 0).sum() / (table > 0).sum()

    def DD_Last(self, **kwargs):
        start = _pd.to_datetime(kwargs.get("start", "19990218")).date()
        Shorted_Table = self.Table[self.Table.index >= start]
        Shorted_Table: _pd.DataFrame = Shorted_Table / Shorted_Table.iloc[0]
        Length = _pd.Series(index=Shorted_Table.columns,
                           dtype=int)
        for name in Shorted_Table.columns:
            tt = _pd.DataFrame(index=Shorted_Table.index, columns=['时长', '回撤'])
            for date in Shorted_Table.index:
                shorted = Shorted_Table[Shorted_Table.index <= date][name]
                Day = shorted[shorted == shorted.max()].index.max()
                dd = list(shorted)[-1] / shorted.max() - 1
                tt.loc[date] = [(date - Day).days if str(Day) != 'nan' else 0, -dd if dd < 0 else 0]
            Length[name] = list(tt[tt['回撤'] == tt['回撤'].max()]['时长'])[0]
        return Length

    def Index_Table(self):
        table = _pd.DataFrame(index=self.Table.columns).rename_axis("产品名称", axis=0)
        table["最新净值"] = self.Latest_NV()
        table["净值日期"] = self.End_Date()
        table["统计起始日"] = self.Start_Date()
        table['近一周涨幅'] = self.Return_Period(1)
        table['近两周涨幅'] = self.Return_Period(2)
        table['近一月涨幅'] = self.Return_Period(4)
        table['近三月涨幅'] = self.Return_Period(13)
        table['近半年涨幅'] = self.Return_Period(26)
        table["%s年年化收益" % (self.date.year - 0)] = self.Return_YTM(0)
        table["%s年年化收益" % (self.date.year - 1)] = self.Return_YTM(1)
        table["%s年年化收益" % (self.date.year - 2)] = self.Return_YTM(2)
        table["近半年年化收益率"] = self.Annual_Return(start=self.date - datetime.timedelta(days=182))
        table["近半年年化波动率"] = self.Annual_Volatility(start=self.date - datetime.timedelta(days=182))
        table["近半年最大回撤"] = self.Maximum_Drawdown(start=self.date - datetime.timedelta(days=182))
        table["近半年夏普率"] = self.Sharpe_Ratio(start=self.date - datetime.timedelta(days=182))
        table["近半年索提诺比率"] = self.Sortino_Ratio(start=self.date - datetime.timedelta(days=182))
        table["近半年卡玛比率"] = self.Calmar_Ratio(start=self.date - datetime.timedelta(days=182))
        table["年化收益率"] = self.Annual_Return()
        table["年化波动率"] = self.Annual_Volatility()
        table["最大回撤"] = self.Maximum_Drawdown()
        table["夏普率"] = self.Sharpe_Ratio()
        table["索提诺比率"] = self.Sortino_Ratio()
        table["卡玛比率"] = self.Calmar_Ratio()
        table["最长不创新高天数"] = self.No_New_High_Period()
        table["胜率"] = self.Success()
        return table
