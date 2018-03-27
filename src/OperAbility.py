from globalVar import safe_div

class OperAbility:
    data_name_list = [
        "销售费用率",
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
        self.year = year
        self.data = {}
        # 销售费用率
        self.data["sales_expense_rate"] = safe_div(
            dividend=curr_psheet["selling_expenses"],
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
            dividend=180 * (curr_bsheet["total_assets"] + prev_bsheet["total_assets"]),
            divisor=curr_psheet["operating_income"]
        )
        # 应收账款周转天数
        self.data["accounts_receivable_turnover_days"] = safe_div(
            dividend=180 * (curr_bsheet["accounts_receivable"] + prev_bsheet["accounts_receivable"]),
            divisor=curr_psheet["operating_income"]
        )
        # 存货周转天数
        self.data["inventory_turnover_days"] = safe_div(
            dividend=180 * (curr_bsheet["stock"] + prev_bsheet["stock"]),
            divisor=curr_psheet["operating_income"]
        )
        # 营业周期
        self.data["business_cycle"] = (
            self.data["inventory_turnover_days"]
            + self.data["accounts_receivable_turnover_days"]
        )
        self.data_list = [
            self.data["sales_expense_rate"],
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
        self.weight = [0, 0, 10, 20, 30, 20, 20, 0]
        year_list = list(year_set)
        year_list.sort()
        self.year2data = {}  # a dictionary whose key is year and value is OperAbility
        for idx in range(1, len(year_list)):
            curr_year = year_list[idx]
            prev_year = year_list[idx - 1]
            new_data = OperAbility(
                year=curr_year,
                curr_year_list=annual_data[curr_year],
                prev_year_list=annual_data[prev_year]
            )  # make a new instance of OperAbility
            self.year2data[curr_year] = new_data
        self.avg_data = None  # the average data of the industry
        self.ratio = None  # the limited ratio between the company data and the average data
        self.score = 0  # the final score of the company ability which is related to the ratio and the score weight

    def get_indicator(self, year):
        """
        get the DevAbility instance of the year
        :param year: the year of develop ability indicator we want to get
        :return: the certain DevAbility instance
        """
        return self.year2data[year]