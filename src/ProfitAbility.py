from .globalVar import safe_growth_rate, safe_div, get_ratio
from xlsxwriter.worksheet import Worksheet
from xlsxwriter.utility import xl_rowcol_to_cell
from copy import copy
from .ImgDrawer import *


class ProfitAbility:
    data_name_list = [
        "销售毛利率",
        "销售营业利润率",
        "销售净利率",
        "净资产收益率",
        "资产报酬率",
        "每股收益",
        "资本运营收益率"
    ]

    def __init__(self, year, prev_year_list, curr_year_list):
        """
        :param year: [year]'s indicators
        :param prev_year_list: the sheet list of the previous year
        :param curr_year_list: the sheet list of the current year
        """
        prev_bsheet = prev_year_list[0].get_data()
        curr_bsheet = curr_year_list[0].get_data()
        curr_psheet = curr_year_list[1].get_data()
        self.year = year
        self.data = {}
        # 销售毛利率
        self.data["sales_gross_margin"] = safe_div(
            dividend=curr_psheet["operating_income"] - curr_psheet["operating_cost"],
            divisor=curr_psheet["operating_income"]
        )
        # 销售营业利润率
        self.data["sales_operating_profit_margin"] = safe_div(
            dividend=curr_psheet["operating_profit"],
            divisor=curr_psheet["operating_income"]
        )
        # 销售净利率
        self.data["sales_margin"] = safe_div(
            dividend=curr_psheet["net_profit"],
            divisor=curr_psheet["operating_income"]
        )
        # 净资产收益率
        self.data["roe"] = safe_div(
            dividend=curr_psheet["net_profit"],
            divisor=(curr_bsheet["owners_equity"] + prev_bsheet["owners_equity"]) / 2
        )
        # 资产报酬率
        self.data["return_on_assets"] = safe_div(
            dividend=curr_psheet["total_profit"] + curr_psheet["financial_expenses"],
            divisor=(curr_bsheet["total_assets"] + prev_bsheet["total_assets"]) / 2
        )
        # 每股收益
        self.data["earnings_per_share"] = safe_div(
            dividend=curr_psheet["net_profit"],
            divisor=(curr_bsheet["paid_in_capital"] + prev_bsheet["paid_in_capital"]) / 2
        )
        # 资本运营收益率
        self.data["capital_operating_rate_of_return"] = safe_div(
            dividend=curr_psheet["investment_income"],
            divisor=(
                curr_bsheet["trading_financial_assets"] + prev_bsheet["trading_financial_assets"] +
                curr_bsheet["available_for_sail_financial_assets"] + prev_bsheet["available_for_sail_financial_assets"] +
                curr_bsheet["held_to_haturity_investments"] + prev_bsheet["held_to_haturity_investments"] +
                curr_bsheet["long_term_investment"] + prev_bsheet["long_term_investment"] +
                curr_bsheet["investment_properties"] + prev_bsheet["investment_properties"]
            ) / 2
        )
        self.data_list = [
            self.data["sales_gross_margin"],
            self.data["sales_operating_profit_margin"],
            self.data["sales_margin"],
            self.data["roe"],
            self.data["return_on_assets"],
            self.data["earnings_per_share"],
            self.data["capital_operating_rate_of_return"]
        ]


    def get_data(self):
        return self.data

    def get_year(self):
        return self.year


class ProData:
    def __init__(self, year_set, annual_data):
        """
        initial function
        :param year_set: catch the year set from Company instance and calculate the profit ability
        :param annual_data: the dictionary whose key is year and value is data list received from Company instance
        """
        self.weight = [10, 10, 20, 20, 15, 10, 15]
        self.year_list = list(year_set)
        self.year_list.sort()
        self.year2data = {}  # a dictionary whose key is year and value is ProfitAbility
        for idx in range(1, len(self.year_list)):
            curr_year = self.year_list[idx]
            prev_year = self.year_list[idx - 1]
            new_data = ProfitAbility(
                year=curr_year,
                curr_year_list=annual_data[curr_year],
                prev_year_list=annual_data[prev_year]
            )  # make a new instance of ProfitAbility
            self.year2data[curr_year] = new_data
        self.year_list.remove(self.year_list[0])
        self.avg_data = None  # the average data of the industry
        self.ratio = [0] * 7  # the limited ratio between the company data and the average data
        self.score = 0  # the final score of the company ability which is related to the ratio and the score weight

    def get_indicator(self, year):
        """
        get the DevAbility instance of the year
        :param year: the year of develop ability indicator we want to get
        :return: the certain DevAbility instance
        """
        return self.year2data[year]

    def get_avg_data(self, avg_data):
        self.avg_data = copy(avg_data)
        last_year_data = self.year2data[max(self.year_list)].data_list
        for i in range(len(last_year_data)):
            self.ratio[i] = get_ratio(last_data=last_year_data[i], avg_data=avg_data[i])
            self.score += self.ratio[i] * self.weight[i]

    def write_data(self, sheet: Worksheet, merge_format):
        """
        write the indicator data to the indicator sheet
        :param sheet: indicator sheet which is a xlsxwriter.Worksheet instance
        :param year_list: the year list of the company's year set
        """
        col = 1
        for year in self.year_list:
            year_data = self.year2data[year]
            sheet.write_column(12, col, year_data.data_list)
            col += 1
        avg_col = 1 + len(self.year_list)  # “行业平均”数据所在列
        ratio_col = 1 + avg_col  # “比率”数据所在列
        sub_score_col = 1 + ratio_col  # “分项能力”得分所在列
        sheet.write_column(12, avg_col, self.avg_data)
        sheet.write_column(12, ratio_col, self.ratio)
        sheet.merge_range("%s:%s" % (xl_rowcol_to_cell(12, sub_score_col), xl_rowcol_to_cell(18, sub_score_col)),
                          self.score, merge_format)

    def write_xlsx(self, sheet: Worksheet, father):
        graph1 = img_draw(
            title="销售毛利率",
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["sales_gross_margin"] for year in self.year_list],
                    "销售毛利率",
                    1
                ]
            ]
        )
        sheet.insert_image(0, 0, "", {"image_data": graph1})

        graph2 = img_draw(
            title="销售营业利润率",
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["sales_operating_profit_margin"] for year in self.year_list],
                    "销售营业利润率",
                    1
                ]
            ]
        )
        sheet.insert_image(20, 0, "", {"image_data": graph2})

        graph3 = img_draw(
            title="销售净利率",
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["sales_margin"] for year in self.year_list],
                    "销售净利率",
                    1
                ]
            ]
        )
        sheet.insert_image(40, 0, "", {"image_data": graph3})

        graph4 = img_draw(
            title="",
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["sales_operating_profit_margin"] for year in self.year_list],
                    "销售营业利润率",
                    1
                ],
                [
                    [self.get_indicator(year).data["sales_operating_profit_margin"] for year in self.year_list],
                    "销售营业利润率",
                    1
                ],
                [
                    [self.get_indicator(year).data["sales_margin"] for year in self.year_list],
                    "销售净利率",
                    1
                ]
            ]
        )
        sheet.insert_image(60, 0, "", {"image_data": graph4})

        graph5 = img_draw(
            title="净资产收益率",
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["roe"] for year in self.year_list],
                    "净资产收益率",
                    1
                ]
            ]
        )
        sheet.insert_image(80, 0, "", {"image_data": graph5})

        graph6 = img_draw(
            title="资产报酬率",
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["return_on_assets"] for year in self.year_list],
                    "资产报酬率",
                    1
                ]
            ]
        )
        sheet.insert_image(100, 0, "", {"image_data": graph6})

        graph7 = img_draw(
            title="",
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["roe"] for year in self.year_list],
                    "净资产收益率",
                    1
                ],
                [
                    [self.get_indicator(year).data["return_on_assets"] for year in self.year_list],
                    "资产报酬率",
                    1
                ]
            ]
        )
        sheet.insert_image(120, 0, "", {"image_data": graph7})

        graph8 = img_draw(
            title="每股收益",
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["earnings_per_share"] for year in self.year_list],
                    "每股收益",
                    1
                ]
            ]
        )
        sheet.insert_image(140, 0, "", {"image_data": graph8})

        graph9 = img_draw(
            title="资本运营收益率",
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["capital_operating_rate_of_return"] for year in self.year_list],
                    "资本运营收益率",
                    1
                ]
            ]
        )
        sheet.insert_image(160, 0, "", {"image_data": graph9})
