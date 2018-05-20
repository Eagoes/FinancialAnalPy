from .Company import Company
from copy import deepcopy, copy
from xlsxwriter.workbook import Workbook
from .globalVar import module_path


class Industry(Company):
    """
    working as a high-level company whose data is the sum of the wholee companies, it can be regarded as the
    industry of all companies
    """
    def __init__(self, company_list, curr_year):
        """
        the init function of class Industry
        :param company_list: a list of companies, the Industry instance is the sum of these companies
        :param curr_year: using for updating the final year
        """
        self.year_set = set()
        self.name = "total"
        self.stockid = "total"
        self.balance_data = None  # 资产负债表
        self.profit_data = None  # 利润表
        self.cash_data = None  # 现金流量表
        self.dev_data = None  # 发展能力数据
        self.oper_data = None  # 运营能力数据
        self.pro_data = None  # 盈利能力数据
        self.cre_data = None  # 创现能力
        self.solv_data = None  # 偿债能力
        self.annual_data = {}
        self.company_list = copy(company_list)
        for company in company_list:
            self.year_set |= company.year_set
        for company in company_list:
            self.__get_data_from_company(company=company)
        for year in self.year_set:
            self.annual_data[year] = [
                self.balance_data.get_sheet(year),
                self.profit_data.get_sheet(year),
                self.cash_data.get_sheet(year)
            ]

    def __add_balance(self, company : Company):
        other_bdata = company.balance_data
        self_bdata = self.balance_data
        for year in company.year_set:
            other_bsheet = other_bdata.get_sheet(year=year)
            self_bsheet = self_bdata.get_sheet(year=year)
            if self_bsheet is not None:
                self_bsheet.data_add(other_bsheet)
            else:
                self.balance_data.year_set.add(year)
                self.balance_data.year2sheet[year] = deepcopy(other_bsheet)

    def __add_profit(self, company : Company):
        other_pdata = company.profit_data
        self_pdata = self.profit_data
        for year in company.year_set:
            other_psheet = other_pdata.get_sheet(year=year)
            self_psheet = self_pdata.get_sheet(year=year)
            if self_psheet is not None:
                self_psheet.data_add(other_psheet)
            else:
                self.profit_data.year_set.add(year)
                self.profit_data.year2sheet[year] = deepcopy(other_psheet)

    def __add_cash(self, company : Company):
        other_fdata = company.cash_data
        self_fdata = self.cash_data
        for year in company.year_set:
            other_fsheet = other_fdata.get_sheet(year=year)
            self_fsheet = self_fdata.get_sheet(year=year)
            if self_fsheet is not None:
                self_fsheet.data_add(other_fsheet)
            else:
                self.cash_data.year_set.add(year)
                self.cash_data.year2sheet[year] = deepcopy(other_fsheet)

    def __get_data_from_company(self, company : Company):
        if self.balance_data is None:
            '''
            the industry is an initial statement and first copy data from the first company
            '''
            self.balance_data = deepcopy(company.balance_data)
            self.profit_data = deepcopy(company.profit_data)
            self.cash_data = deepcopy(company.cash_data)
        else:
            self.__add_balance(company=company)
            self.__add_profit(company=company)
            self.__add_cash(company=company)

    def alloc_data_for_company(self, company_list):
        """
        send the last year industry indicator data to every company as the average data of the industry
        :param company_list: the list of companies
        """
        cl = copy(company_list)
        cl.append(self)
        year_list = list(self.year_set)
        year_list.sort()
        lastyear = year_list[len(year_list) - 1]  # get the last year
        avg_dev_data = self.dev_data.get_indicator(year=lastyear).data_list
        avg_cre_data = self.cre_data.get_indicator(year=lastyear).data_list
        avg_pro_data = self.pro_data.get_indicator(year=lastyear).data_list
        avg_oper_data = self.oper_data.get_indicator(year=lastyear).data_list
        avg_solv_data = self.solv_data.get_indicator(year=lastyear).data_list
        for company in cl:
            company.dev_data.get_avg_data(avg_data=avg_dev_data)
            company.cre_data.get_avg_data(avg_data=avg_cre_data)
            company.pro_data.get_avg_data(avg_data=avg_pro_data)
            company.oper_data.get_avg_data(avg_data=avg_oper_data)
            company.solv_data.get_avg_data(avg_data=avg_solv_data)
            company.get_score()

    def write_score_xlsx(self, filepath=module_path+'/result/'):
        workbook = Workbook(filepath + "score.xlsx")
        sheet = workbook.add_worksheet()
        sheet.write_row(0, 0, ["公司名称", "综合", "发展能力", "创现能力", "盈利能力", "运营能力", "偿债能力"])
        row = 1
        for company in self.company_list:
            cre_score = company.cre_data.score
            dev_score = company.dev_data.score
            oper_score = company.oper_data.score
            pro_score = company.pro_data.score
            solv_score = company.solv_data.score
            comp_score = company.score
            score_list = [
                company.name, cre_score, dev_score, oper_score,
                pro_score, solv_score, comp_score
            ]
            sheet.write_row(row, 0, score_list)
            row += 1
        workbook.close()
