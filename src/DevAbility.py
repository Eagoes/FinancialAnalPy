from .globalVar import safe_growth_rate, get_ratio
from xlsxwriter.worksheet import Worksheet
from xlsxwriter.utility import xl_rowcol_to_cell
from copy import copy
from .ImgDrawer import img_draw, bar_and_plot


class DevAbility:
    data_name_list_zh = [
        "销售增长率",
        "资产增长率",
        "净利润增长率",
        "净资产增长率",
        "固定资产增长率"
    ]
    data_name_list = [
        "sales_growth_rate",
        "asset_growth_rate",
        "net_profit_growth_rate",
        "net_asset_growth_rate",
        "fixed_asset_growth_rate"
    ]


    def __init__(self, year, prev_year_list, curr_year_list):
        """
        :param year: [year]'s indicators
        :param prev_year_list: the sheet list of the previous year
        :param curr_year_list: the sheet list of the current year
        """
        prev_bsheet = prev_year_list[0].get_data()
        prev_psheet = prev_year_list[1].get_data()
        curr_bsheet = curr_year_list[0].get_data()
        curr_psheet = curr_year_list[1].get_data()
        self.year = year
        self.data = {}
        # 销售增长率
        self.data["sales_growth_rate"] = safe_growth_rate(
            dividend=curr_psheet["operating_income"],
            divisor=prev_psheet["operating_income"]
        )
        # 资产增长率
        self.data["asset_growth_rate"] = safe_growth_rate(
            dividend=curr_bsheet["total_assets"],
            divisor=prev_bsheet["total_assets"]
        )
        # 净利润增长率
        self.data["net_profit_growth_rate"] = safe_growth_rate(
            dividend=curr_psheet["net_profit"],
            divisor=prev_psheet["net_profit"]
        )
        # 净资产增长率
        self.data["net_asset_growth_rate"] = safe_growth_rate(
            dividend=curr_bsheet["owners_equity"],
            divisor=prev_bsheet["owners_equity"]
        )
        # 固定资产增长率
        self.data["fixed_asset_growth_rate"] = safe_growth_rate(
            dividend=curr_bsheet["fixed_assetes"],
            divisor=prev_bsheet["fixed_assetes"]
        )
        self.data_list = [
            self.data["sales_growth_rate"],
            self.data["asset_growth_rate"],
            self.data["net_profit_growth_rate"],
            self.data["net_asset_growth_rate"],
            self.data["fixed_asset_growth_rate"]
        ]

    def get_data(self):
        return self.data

    def get_data_list(self):
        return self.data_list

    def get_year(self):
        return self.year


class DevData:
    def __init__(self, year_set, annual_data):
        """
        initial function
        :param year_set: catch the year set from Company instance and calculate the develop ability
        :param annual_data: the dictionary whose key is year and value is data list received from Company instance
        """
        self.weight = [30, 25, 20, 15, 10]
        self.year_list = list(year_set)
        self.year_list.sort()
        self.year2data = {}  # a dictionary whose key is year and value is DevAbility
        for idx in range(1, len(self.year_list)):
            curr_year = self.year_list[idx]
            prev_year = self.year_list[idx - 1]
            new_data = DevAbility(
                year=curr_year,
                curr_year_list=annual_data[curr_year],
                prev_year_list=annual_data[prev_year]
            )  # make a new instance of DevAbility
            self.year2data[curr_year] = new_data
        self.year_list.remove(self.year_list[0])
        self.avg_data = None  # the average data of the industry
        self.ratio = [0] * 5  # the limited ratio between the company data and the average data
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
            sheet.write_column(1, col, year_data.data_list)
            col += 1
        avg_col = 1 + len(self.year_list)  # “行业平均”数据所在列
        ratio_col = 1 + avg_col  # “比率”数据所在列
        sub_score_col = 1 + ratio_col  # “分项能力”得分所在列
        sheet.write_column(1, avg_col, self.avg_data)
        sheet.write_column(1, ratio_col, self.ratio)
        sheet.merge_range("%s:%s"%(xl_rowcol_to_cell(1, sub_score_col), xl_rowcol_to_cell(5, sub_score_col)),
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
        """
        insert the image to the work sheet
        :param sheet: the Worksheet instance
        :param father: the Company instance to share the data betweeen different sheets and indicators
        :return:
        """
        graph1 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [father.profit_data.get_sheet(year).data["operating_income"] for year in self.year_list],
                "营业收入"
            ],
            plot_param=[
                [self.get_indicator(year).data["sales_growth_rate"] for year in self.year_list],
                "销售增长率"
            ]
        )
        sheet.insert_image(0, 0, "", {"image_data": graph1})

        graph2 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [father.balance_data.get_sheet(year).data["total_assets"] for year in self.year_list],
                "资产总计"
            ],
            plot_param=[
                [self.get_indicator(year).data["asset_growth_rate"] for year in self.year_list],
                "资产增长率"
            ]
        )
        sheet.insert_image(19, 0, "", {"image_data": graph2})

        graph3 = img_draw(
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["sales_growth_rate"] for year in self.year_list],
                    "销售增长率",
                    1
                ],
                [
                    [self.get_indicator(year).data["asset_growth_rate"] for year in self.year_list],
                    "资产增长率",
                    1
                ]
            ]
        )
        sheet.insert_image(39, 0, "", {"image_data": graph3})

        graph4 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [father.profit_data.get_sheet(year).data["net_profit"] for year in self.year_list],
                "净利润"
            ],
            plot_param=[
                [self.get_indicator(year).data["net_profit_growth_rate"] for year in self.year_list],
                "净利润增长率"
            ]
        )
        sheet.insert_image(59, 0, "", {"image_data": graph4})

        graph5 = img_draw(
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["net_profit_growth_rate"] for year in self.year_list],
                    "净利润增长率",
                    1
                ],
                [
                    [self.get_indicator(year).data["sales_growth_rate"] for year in self.year_list],
                    "销售收入增长率",
                    1
                ]
            ]
        )
        sheet.insert_image(79, 0, "", {"image_data": graph5})

        graph6 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [father.balance_data.get_sheet(year).data["owners_equity"] for year in self.year_list],
                "净资产"
            ],
            plot_param=[
                [self.get_indicator(year).data["net_asset_growth_rate"] for year in self.year_list],
                "净资产增长率"
            ]
        )
        sheet.insert_image(99, 0, "", {"image_data": graph6})

        graph7 = img_draw(
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["asset_growth_rate"] for year in self.year_list],
                    "资产增长率",
                    1
                ],
                [
                    [self.get_indicator(year).data["net_asset_growth_rate"] for year in self.year_list],
                    "净资产增长率",
                    1
                ]
            ]
        )
        sheet.insert_image(119, 0, "", {"image_data": graph7})

        graph8 = bar_and_plot(
            category=self.year_list,
            bar_param=[
                [father.balance_data.get_sheet(year).data["fixed_assetes"] for year in self.year_list],
                "固定资产"
            ],
            plot_param=[
                [self.get_indicator(year).data["fixed_asset_growth_rate"] for year in self.year_list],
                "固定资产增长率"
            ]
        )
        sheet.insert_image(139, 0, "", {"image_data": graph8})

        graph9 = img_draw(
            category=self.year_list,
            plot_params=[
                [
                    [self.get_indicator(year).data["asset_growth_rate"] for year in self.year_list],
                    "资产增长率",
                    1
                ],
                [
                    [self.get_indicator(year).data["fixed_asset_growth_rate"] for year in self.year_list],
                    "固定资产增长率",
                    1
                ]
            ]
        )
        sheet.insert_image(159, 0, "", {"image_data": graph9})