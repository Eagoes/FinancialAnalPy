from globalVar import safe_growth_rate, safe_div, get_ratio
from BalanceSheet import *
from CashFlowStatement import *
from ProfitStatement import *
from xlsxwriter.worksheet import Worksheet
from copy import copy
from ImgDrawer import *


class Solvency:
    data_name_list = [
        "资产负债率",
        "流动比率",
        "速动比率"
    ]

    def __init__(self, year, prev_year_list, curr_year_list):
        """
        :param year: [year]'s indicators
        :param prev_year_list: the sheet list of the previous year
        :param curr_year_list: the sheet list of the current year
        """
        prev_bsheet = prev_year_list[0].get_data()
        prev_psheet = prev_year_list[1].get_data()
        prev_fsheet = prev_year_list[2].get_data()
        curr_bsheet = curr_year_list[0].get_data()
        curr_psheet = curr_year_list[1].get_data()
        curr_fsheet = curr_year_list[2].get_data()
        self.year = year
        self.data = {}
        # 资产负债率
        self.data["assets_and_liabilities"] = safe_div(
            dividend=curr_bsheet["total_liabilities"],
            divisor=curr_bsheet["total_assets"]
        )
        # 流动比率
        self.data["current_ratio"] = safe_div(
            dividend=curr_bsheet["total_current_assets"],
            divisor=curr_bsheet["sub_total_of_current_liabilities"]
        )
        # 速动比率
        self.data["quick_ratio"] = safe_div(
            dividend=curr_bsheet["total_current_assets"] - curr_bsheet["stock"],
            divisor=curr_bsheet["sub_total_of_current_liabilities"]
        )
        self.data_list = [
            self.data["assets_and_liabilities"],
            self.data["current_ratio"],
            self.data["quick_ratio"]
        ]


    def get_data(self):
        return self.data

    def get_year(self):
        return self.year


class SolvData:
    def __init__(self, year_set, annual_data):
        """
        initial function
        :param year_set: catch the year set from Company instance and calculate the solvency
        :param annual_data: the dictionary whose key is year and value is data list received from Company instance
        """
        self.weight = [50, 30, 20]
        self.year_list = list(year_set)
        self.year_list.sort()
        self.year2data = {}  # a dictionary whose key is year and value is Solvency
        for idx in range(1, len(self.year_list)):
            curr_year = self.year_list[idx]
            prev_year = self.year_list[idx - 1]
            new_data = Solvency(
                year=curr_year,
                curr_year_list=annual_data[curr_year],
                prev_year_list=annual_data[prev_year]
            )  # make a new instance of Solvency
            self.year2data[curr_year] = new_data
        self.avg_data = None  # the average data of the industry
        self.ratio = [0] * 3  # the limited ratio between the company data and the average data
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
            self.score += self.score[i]

    def write_data(self, sheet: Worksheet):
        """
        write the indicator data to the indicator sheet
        :param sheet: indicator sheet which is a xlsxwriter.Worksheet instance
        """
        col = 1
        for year in self.year_list:
            year_data = self.year2data[year]
            sheet.write_column(1, col, year_data.data_list)
            col += 1
