from BalanceSheet import BalanceData
from ProfitStatement import ProfitData
from CashFlowStatement import CashData
from DevAbility import DevData
from CreateAbility import CreData
from ProfitAbility import ProData
from OperAbility import OperData
from Solvency import SolvData
from globalVar import id2name_dict, season2date
import xlsxwriter as xlw


class Company:
    def __init__(self, stockid, startyear, finalyear, season):
        self.stockid = stockid
        self.name = id2name_dict[stockid]
        self.season = season
        date = season2date[season]
        self.balance_data = BalanceData(stockid=stockid, startyear=startyear, finalyear=finalyear, date = date)
        self.profit_data = ProfitData(stockid=stockid, startyear=startyear, finalyear=finalyear, date = date)
        self.cash_data = CashData(stockid=stockid, startyear=startyear, finalyear=finalyear, date = date)
        self.year_set = self.balance_data.year_set & self.profit_data.year_set & self.cash_data.year_set
        self.trim_year_set(master_set=self.year_set)  # synchronize three sheets to unify their year set
        self.annual_data = {}
        for year in self.year_set:
            self.annual_data[year] = [
                self.balance_data.get_sheet(year),
                self.profit_data.get_sheet(year),
                self.cash_data.get_sheet(year)
            ]
        self.dev_data = None  # 发展能力数据
        self.oper_data = None  # 运营能力数据
        self.pro_data = None  # 盈利能力数据
        self.cre_data = None  # 创现能力
        self.solv_data = None  # 偿债能力

    def trim_year_set(self, master_set):
        """
        :param master_set: a year set that three data set must be trimmed to be similar to it
        :return: no return
        """
        sub_set = self.balance_data.year_set - master_set
        for year in sub_set:
            self.balance_data.del_sheet(year=year)  #remove the sheet whose year is not in the master set
        sub_set = self.profit_data.year_set - master_set
        for year in sub_set:
            self.profit_data.del_sheet(year=year)
        sub_set = self.cash_data.year_set - master_set
        for year in sub_set:
            self.cash_data.del_sheet(year=year)
        if hasattr(self, 'annual_data'):
            '''
            if the method is called by __init__(), the attribute annual_data is not defined yet, this section will not
            run. if the method is called later when all the companies unify their year set, their annual data dictionary
            should also be trimmed.
            '''
            for key, value in self.annual_data.items():
                if key not in master_set:
                    self.annual_data.pop(key)

    def calculate(self):
        """
        after every company has synchronized and unified the year set and annual data, each company
        calculate their own indictors including develop ability, create ability, profit ability,
        operate ability and solvency
        """
        self.dev_data = DevData(year_set=self.year_set, annual_data=self.annual_data)
        self.cre_data = CreData(year_set=self.year_set, annual_data=self.annual_data)
        self.pro_data = ProData(year_set=self.year_set, annual_data=self.annual_data)
        self.oper_data = OperData(year_set=self.year_set, annual_data=self.annual_data)
        self.solv_data = SolvData(year_set=self.year_set, annual_data=self.annual_data)

    def write_xlsx(self, filepath='../result/'):
        """
        output the company information and data to the excel 2007+ (.xlsx) file
        :param filepath: the dir of the excel file you want to create
        """
        workbook = xlw.Workbook(filepath + self.stockid)
        balance_sheet = workbook.add_worksheet('资产负债表')
        # add balance sheet output here
        profit_sheet = workbook.add_worksheet('利润表')
        # add profit statement output here
        cash_sheet = workbook.add_worksheet('现金流量表')
        # add cash flow statement output here
        indicator_sheet = workbook.add_worksheet('指标')
        # add indicator data output here
        dev_chart_sheet = workbook.add_worksheet('发展能力图表')
        # add devlop ability chart output here
        cre_chart_sheet = workbook.add_worksheet('创现能力图表')
        # add create ability chart output here
        pro_chart_sheet = workbook.add_worksheet('盈利能力图表')
        # add profit ability chart output here
        oper_chart_sheet = workbook.add_worksheet('运营能力图表')
        # add operate ability chart output here
        solv_chart_sheet = workbook.add_worksheet('偿债能力图表')
        # add solvency chart output here
