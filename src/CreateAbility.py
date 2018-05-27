from .globalVar import safe_growth_rate, safe_div, get_ratio
from xlsxwriter.worksheet import Worksheet
from xlsxwriter.utility import xl_rowcol_to_cell
from copy import copy
from .ImgDrawer import img_draw, bar_and_plot


class CreateAbility:
    data_name_list_zh = [
        "经营现金增长率",
        "现金流量增长率",
        "自由现金流",
        "销售经营现金比",
        "销售现金比",
        "销售自由现金比"
    ]
    data_name_list = [
        "operating_cash_growth_rate",
        "cash_flow_growth_rate",
        "free_cash_ratio",
        "sales_and_operating_cash_ratio",
        "sales_cash_ratio",
        "sales_free_cash_ratio"
    ]

    def __init__(self, year, prev_year_list, curr_year_list):
        """
        :param year: [year]'s indicators
        :param prev_year_list: the sheet list of the previous year
        :param curr_year_list: the sheet list of the current year
        """
        prev_fsheet = prev_year_list[2].get_data()
        curr_psheet = curr_year_list[1].get_data()
        curr_fsheet = curr_year_list[2].get_data()
        self.year = year
        self.data = {}
        # 经营现金增长率
        self.data["operating_cash_growth_rate"] = safe_growth_rate(
            dividend=curr_fsheet["net_cash_op"],
            divisor=prev_fsheet["net_cash_op"]
        )
        # 现金流量增长率
        self.data["cash_flow_growth_rate"] = safe_growth_rate(
            dividend=curr_fsheet["final_cash"],
            divisor=prev_fsheet["final_cash"]
        )
        # 自由现金流
        self.data["free_cash_ratio"] = curr_fsheet["net_cash_op"] - curr_fsheet["cash_paid_fa"]
        # 销售经营现金比
        self.data["sales_and_operating_cash_ratio"] = safe_div(
            dividend=curr_fsheet["net_cash_op"],
            divisor=curr_psheet["operating_income"]
        )
        # 销售现金比
        self.data["sales_cash_ratio"] = safe_div(
            dividend=curr_fsheet["final_cash"],
            divisor=curr_psheet["operating_income"]
        )
        # 销售自由现金比
        self.data["sales_free_cash_ratio"] = safe_div(
            dividend=curr_fsheet["net_cash_op"] - curr_fsheet["cash_paid_fa"],
            divisor=curr_psheet["operating_income"]
        )
        self.data_list = [
            self.data["operating_cash_growth_rate"],
            self.data["cash_flow_growth_rate"],
            self.data["free_cash_ratio"],
            self.data["sales_and_operating_cash_ratio"],
            self.data["sales_cash_ratio"],
            self.data["sales_free_cash_ratio"]
        ]


    def get_data(self):
        return self.data

    def get_year(self):
        return self.year


class CreData:
    def __init__(self, year_set, annual_data):
        """
        initial function
        :param year_set: catch the year set from Company instance and calculate the create ability
        :param annual_data: the dictionary whose key is year and value is data list received from Company instance
        """
        self.weight = [30, 20, 30, 20, 0, 0]
        self.year_list = list(year_set)
        self.year_list.sort()
        self.year2data = {}  # a dictionary whose key is year and value is CreateAbility
        for idx in range(1, len(self.year_list)):
            curr_year = self.year_list[idx]
            prev_year = self.year_list[idx - 1]
            new_data = CreateAbility(
                year=curr_year,
                curr_year_list=annual_data[curr_year],
                prev_year_list=annual_data[prev_year]
            )  # make a new instance of CreateAbility
            self.year2data[curr_year] = new_data
        self.year_list.remove(self.year_list[0])
        self.avg_data = None  # the average data of the industry
        self.ratio = [0] * 6  # the limited ratio between the company data and the average data
        self.score = 0  # the final score of the company ability which is related to the ratio and the score weight

    def get_indicator(self, year):
        """
        get the DevAbility instance of the year
        :param year: the year of develop ability indicator we want to get
        :return: the certain DevAbility instance
        """
        return self.year2data[year]

    def write_data(self, sheet: Worksheet, merge_format):
        """
        write the indicator data to the indicator sheet
        :param sheet: indicator sheet which is a xlsxwriter.Worksheet instance
        """
        col = 1
        for year in self.year_list:
            year_data = self.year2data[year]
            sheet.write_column(6, col, year_data.data_list)
            col += 1
        avg_col = 1 + len(self.year_list)  # “行业平均”数据所在列
        ratio_col = 1 + avg_col  # “比率”数据所在列
        sub_score_col = 1 + ratio_col  # “分项能力”得分所在列
        sheet.write_column(6, avg_col, self.avg_data)
        sheet.write_column(6, ratio_col, self.ratio)
        sheet.merge_range("%s:%s" % (xl_rowcol_to_cell(6, sub_score_col), xl_rowcol_to_cell(11, sub_score_col)),
                          self.score, merge_format)

    def get_avg_data(self, avg_data):
        self.avg_data = copy(avg_data)
        for i in range(len(avg_data)):
            if avg_data[i] < 0:
                avg_data[i] = 0.01
        last_year_data = self.year2data[max(self.year_list)].data_list
        for i in range(len(last_year_data)):
            self.ratio[i] = get_ratio(last_data=last_year_data[i], avg_data=avg_data[i])
            self.score += self.ratio[i] * self.weight[i]

    def write_xlsx(self, sheet: Worksheet, father):
        graph1 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [father.cash_data.get_sheet(year).data["net_cash_op"] for year in self.year_list],
                "经营现金流"
            ],
            plot_param=[
                [self.get_indicator(year).data["operating_cash_growth_rate"] for year in self.year_list],
                "经营现金增长率"
            ]
        )
        sheet.insert_image(0, 0, "", {"image_data": graph1})

        graph2 = img_draw(
            category=self.year_list,
            plot_params=[
                [
                    [father.dev_data.get_indicator(year).data["sales_growth_rate"] for year in self.year_list],
                    "销售增长率",
                    1
                ],
                [
                    [self.get_indicator(year).data["operating_cash_growth_rate"] for year in self.year_list],
                    "经营现金增长率",
                    1
                ]
            ]
        )
        sheet.insert_image(20, 0, "", {"image_data": graph2})

        graph3 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [father.cash_data.get_sheet(year).data["final_cash"] for year in self.year_list],
                "期末现金流"
            ],
            plot_param=[
                [self.get_indicator(year).data["cash_flow_growth_rate"] for year in self.year_list],
                "现金流量增长率"
            ]
        )
        sheet.insert_image(40, 0, "", {"image_data": graph3})

        graph4 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [self.get_indicator(year).data["free_cash_ratio"] for year in self.year_list],
                "自由现金流"
            ],
            plot_param=[
                [self.get_indicator(year).data["sales_and_operating_cash_ratio"] for year in self.year_list],
                "销售自由现金比"
            ]
        )
        sheet.insert_image(60, 0, "", {"image_data": graph4})

        graph5 = img_draw(
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["sales_and_operating_cash_ratio"] for year in self.year_list],
                    "销售经营现金比",
                    1
                ]
            ]
        )
        sheet.insert_image(80, 0, "", {"image_data": graph5})

        graph6 = img_draw(
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["sales_cash_ratio"] for year in self.year_list],
                    "销售现金比",
                    1
                ]
            ]
        )
        sheet.insert_image(100, 0, "", {"image_data": graph6})
