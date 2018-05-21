from .BalanceSheet import BalanceData
from .ProfitStatement import ProfitData
from .CashFlowStatement import CashData
from .DevAbility import DevData, DevAbility
from .CreateAbility import CreData, CreateAbility
from .ProfitAbility import ProData, ProfitAbility
from .OperAbility import OperData, OperAbility
from .Solvency import SolvData, Solvency
from .globalVar import id2name_dict, season2date, module_path
from xlsxwriter import Workbook
from xlsxwriter.utility import xl_rowcol_to_cell
from copy import copy


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
        self.score = 0

    def trim_year_set(self, master_set):
        """
        :param master_set: a year set that three data set must be trimmed to be similar to it
        :return: no return
        """
        self.year_set = copy(master_set)
        sub_set = self.balance_data.year_set - master_set
        for year in sub_set:
            self.balance_data.del_sheet(year=year)  # remove the sheet whose year is not in the master set
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
            sub_key_set = self.annual_data.keys() - master_set
            for key in sub_key_set:
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

    def get_score(self):
        self.score = (
            0.3 * self.dev_data.score
            + 0.25 * self.cre_data.score
            + 0.2 * self.pro_data.score
            + 0.15 * self.oper_data.score
            + 0.1 * self.solv_data.score
        )

    def write_xlsx(self, filepath=module_path+'/result/'):
        """
        output the company information and data to the excel 2007+ (.xlsx) file
        :param filepath: the dir of the excel file you want to create
        """
        workbook = Workbook(filepath + self.name + ".xlsx")
        merge_format = workbook.add_format({
            "align": "center",
            "valign": "center"
        })
        year_list = list(self.year_set)
        year_list.sort()

        balance_sheet = workbook.add_worksheet('资产负债表')
        self.balance_data.write_data(sheet=balance_sheet, year_list=year_list)

        profit_sheet = workbook.add_worksheet('利润表')
        self.profit_data.write_data(sheet=profit_sheet, year_list=year_list)

        cash_sheet = workbook.add_worksheet('现金流量表')
        self.cash_data.write_data(sheet=cash_sheet, year_list=year_list)

        indicator_sheet = workbook.add_worksheet('指标')
        # write the year of the indicator sheet
        col = 1
        avg_col = len(year_list)  # “行业平均”数据所在列
        ratio_col = 1 + avg_col  # “比率”数据所在列
        sub_score_col = 1 + ratio_col  # “分项能力”得分所在列
        score_col = 1 + sub_score_col  # 公司得分所在列
        year_list.pop(0)
        for year in year_list:
            indicator_sheet.write(0, col, year)
            col += 1
        indicator_sheet.write(0, avg_col, "行业平均数据")
        indicator_sheet.write(0, ratio_col, "比率")
        indicator_sheet.write(0, sub_score_col, "分项能力得分")
        indicator_sheet.write(0, score_col, "公司得分")
        # write the indicator name which is on the left bar to the indicator sheet
        indicator_sheet.write_column(1, 0, DevAbility.data_name_list)
        indicator_sheet.write_column(6, 0, CreateAbility.data_name_list)
        indicator_sheet.write_column(12, 0, ProfitAbility.data_name_list)
        indicator_sheet.write_column(19, 0, OperAbility.data_name_list)
        indicator_sheet.write_column(28, 0, Solvency.data_name_list)
        # write the indicator data
        self.dev_data.write_data(indicator_sheet, merge_format)
        self.cre_data.write_data(indicator_sheet, merge_format)
        self.pro_data.write_data(indicator_sheet, merge_format)
        self.oper_data.write_data(indicator_sheet, merge_format)
        self.solv_data.write_data(indicator_sheet, merge_format)
        indicator_sheet.merge_range("%s:%s"%(xl_rowcol_to_cell(1, score_col), xl_rowcol_to_cell(30, score_col)),
                                    self.score, merge_format)

        dev_chart_sheet = workbook.add_worksheet('发展能力')
        self.dev_data.write_xlsx(sheet=dev_chart_sheet, father=self)

        cre_chart_sheet = workbook.add_worksheet('创现能力')
        self.cre_data.write_xlsx(sheet=cre_chart_sheet, father=self)

        pro_chart_sheet = workbook.add_worksheet('盈利能力')
        self.pro_data.write_xlsx(sheet=pro_chart_sheet, father=self)

        oper_chart_sheet = workbook.add_worksheet('运营能力')
        self.oper_data.write_xlsx(sheet=oper_chart_sheet, father=self)

        solv_chart_sheet = workbook.add_worksheet('偿债能力')
        self.solv_data.write_xlsx(sheet=solv_chart_sheet, father=self)

        workbook.close()
