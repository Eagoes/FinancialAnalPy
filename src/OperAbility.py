from .globalVar import safe_growth_rate, safe_div, get_ratio
from xlsxwriter.worksheet import Worksheet
from xlsxwriter.utility import xl_rowcol_to_cell
from copy import copy
from .ImgDrawer import img_draw, bar_and_plot


class OperAbility:
    data_name_list = [
        "销售费用率",
        "销售回款率",
        "管理费用率",
        "销售管理费用率",
        "期间费用率",
        "资产周转天数",
        "应收账款周转天数",
        "存货周转天数",
        "营业周期"
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
        curr_fsheet = curr_year_list[2].get_data()
        self.year = year
        self.data = {}
        # 销售费用率
        self.data["sales_expense_rate"] = safe_div(
            dividend=curr_psheet["selling_expenses"],
            divisor=curr_psheet["operating_income"]
        )
        # 销售回款率
        self.data["repayment_rate_of_sales"] = safe_div(
            dividend=curr_fsheet["cash_from_sale"],
            divisor=curr_psheet["operating_income"]
        )
        # 管理费用率
        self.data["management_fee_rate"] = safe_div(
            dividend=curr_psheet["management_fees"],
            divisor=curr_psheet["operating_income"]
        )
        # 销售管理费用率
        self.data["sales_management_fee_rate"] = safe_div(
            dividend=curr_psheet["selling_expenses"] + curr_psheet["management_fees"],
            divisor=curr_psheet["operating_income"]
        )
        # 期间费用率
        self.data["period_expense_rate"] = safe_div(
            dividend=(
                curr_psheet["selling_expenses"]
                + curr_psheet["management_fees"]
                + curr_psheet["financial_expenses"]
            ),
            divisor=curr_psheet["operating_income"]
        )
        # 资产周转天数
        self.data["asset_turnover_days"] = safe_div(
            dividend=curr_psheet["operating_income"],
            divisor=180 * (curr_bsheet["total_assets"] + prev_bsheet["total_assets"])
        )
        # 应收账款周转天数
        self.data["accounts_receivable_turnover_days"] = safe_div(
            dividend=curr_psheet["operating_income"],
            divisor=180 * (curr_bsheet["accounts_receivable"] + prev_bsheet["accounts_receivable"])
        )
        # 存货周转天数
        self.data["inventory_turnover_days"] = safe_div(
            dividend=curr_psheet["operating_cost"],
            divisor=180 * (curr_bsheet["stock"] + prev_bsheet["stock"])
        )
        # 营业周期
        self.data["business_cycle"] = (
            self.data["inventory_turnover_days"]
            + self.data["accounts_receivable_turnover_days"]
        )
        self.data_list = [
            self.data["sales_expense_rate"],
            self.data["repayment_rate_of_sales"],
            self.data["management_fee_rate"],
            self.data["sales_management_fee_rate"],
            self.data["period_expense_rate"],
            self.data["asset_turnover_days"],
            self.data["accounts_receivable_turnover_days"],
            self.data["inventory_turnover_days"],
            self.data["business_cycle"]
        ]

    def get_data(self):
        return self.data

    def get_year(self):
        return self.year


class OperData:
    def __init__(self, year_set, annual_data):
        """
        initial function
        :param year_set: catch the year set from Company instance and calculate the operation ability
        :param annual_data: the dictionary whose key is year and value is data list received from Company instance
        """
        self.weight = [0, 0, 0, 10, 20, 30, 20, 20, 0]
        self.year_list = list(year_set)
        self.year_list.sort()
        self.year2data = {}  # a dictionary whose key is year and value is OperAbility
        for idx in range(1, len(self.year_list)):
            curr_year = self.year_list[idx]
            prev_year = self.year_list[idx - 1]
            new_data = OperAbility(
                year=curr_year,
                curr_year_list=annual_data[curr_year],
                prev_year_list=annual_data[prev_year]
            )  # make a new instance of OperAbility
            self.year2data[curr_year] = new_data
        self.year_list.remove(self.year_list[0])
        self.avg_data = None  # the average data of the industry
        self.ratio = [0] * 9  # the limited ratio between the company data and the average data
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
        for i in range(len(avg_data)):
            if avg_data[i] < 0:
                avg_data[i] = 0.01
        last_year_data = self.year2data[max(self.year_list)].data_list
        for i in range(len(last_year_data)):
            if i in range(5, 9):
                # 资产周转天数 应收账款周转天数 存货周转天数 营业周期 比率越小越好
                self.ratio[i] = get_ratio(last_data=avg_data[i], avg_data=last_year_data[i])
            else:
                self.ratio[i] = get_ratio(last_data=last_year_data[i], avg_data=avg_data[i])
            self.score += self.ratio[i] * self.weight[i]

    def write_data(self, sheet: Worksheet, merge_format):
        """
        write the indicator data to the indicator sheet
        :param sheet: indicator sheet which is a xlsxwriter.Worksheet instance
        """
        col = 1
        for year in self.year_list:
            year_data = self.year2data[year]
            sheet.write_column(19, col, year_data.data_list)
            col += 1
        avg_col = 1 + len(self.year_list)  # “行业平均”数据所在列
        ratio_col = 1 + avg_col  # “比率”数据所在列
        sub_score_col = 1 + ratio_col  # “分项能力”得分所在列
        sheet.write_column(19, avg_col, self.avg_data)
        sheet.write_column(19, ratio_col, self.ratio)
        sheet.merge_range("%s:%s" % (xl_rowcol_to_cell(19, sub_score_col), xl_rowcol_to_cell(27, sub_score_col)),
                          self.score, merge_format)

    def write_xlsx(self, sheet: Worksheet, father):
        graph1 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [father.profit_data.get_sheet(year).data["selling_expenses"] for year in self.year_list],
                "销售费用"
            ],
            plot_param=[
                [self.get_indicator(year).data["sales_expense_rate"] for year in self.year_list],
                "销售费用率"
            ]
        )
        sheet.insert_image(0, 0, "", {"image_data": graph1})

        graph2 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [father.profit_data.get_sheet(year).data["management_fees"] for year in self.year_list],
                "管理费用"
            ],
            plot_param=[
                [self.get_indicator(year).data["management_fee_rate"] for year in self.year_list],
                "管理费用率"
            ]
        )
        sheet.insert_image(20, 0, "", {"image_data": graph2})

        graph3 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [(
                    father.profit_data.get_sheet(year).data["management_fees"] +
                    father.profit_data.get_sheet(year).data["selling_expenses"]
                ) for year in self.year_list],
                "销售费用+管理费用"
            ],
            plot_param=[
                [self.get_indicator(year).data["sales_management_fee_rate"] for year in self.year_list],
                "销售管理费用率"
            ]
        )
        sheet.insert_image(40, 0, "", {"image_data": graph3})

        graph4 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [(
                    father.profit_data.get_sheet(year).data["management_fees"] +
                    father.profit_data.get_sheet(year).data["selling_expenses"] +
                    father.profit_data.get_sheet(year).data["financial_expenses"]
                ) for year in self.year_list],
                "期间费用"
            ],
            plot_param=[
                [self.get_indicator(year).data["period_expense_rate"] for year in self.year_list],
                "期间费用率"
            ]
        )
        sheet.insert_image(60, 0, "", {"image_data": graph4})

        graph5 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [father.balance_data.get_sheet(year).data["total_assets"] for year in self.year_list],
                "资产总计"
            ],
            plot_param=[
                [self.get_indicator(year).data["asset_turnover_days"] for year in self.year_list],
                "资产周转天数"
            ],
            use_percent=False
        )
        sheet.insert_image(80, 0, "", {"image_data": graph5})

        graph6 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [father.balance_data.get_sheet(year).data["accounts_receivable"] for year in self.year_list],
                "应收账款"
            ],
            plot_param=[
                [self.get_indicator(year).data["accounts_receivable_turnover_days"] for year in self.year_list],
                "应收账款周转天数"
            ],
            use_percent=False
        )
        sheet.insert_image(100, 0, "", {"image_data": graph6})

        graph7 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [father.balance_data.get_sheet(year).data["stock"] for year in self.year_list],
                "存货"
            ],
            plot_param=[
                [self.get_indicator(year).data["inventory_turnover_days"] for year in self.year_list],
                "存货周转天数"
            ],
            use_percent=False
        )
        sheet.insert_image(120, 0, "", {"image_data": graph7})

        graph8 = img_draw(
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["business_cycle"] for year in self.year_list],
                    "营业周期",
                    1
                ]
            ],
            use_percent=False
        )
        sheet.insert_image(140, 0, "", {"image_data": graph8})
