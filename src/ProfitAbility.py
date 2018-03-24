from globalVar import safe_div

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
        self.weight = [10, 10, 20, 20, 15, 10, 15]
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
        self.score = 0
        for i in range(len(self.data_list)):
            self.score += self.data_list[i] * self.weight[i]


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
        year_list = list(year_set)
        year_list.sort()
        self.year2data = {}  # a dictionary whose key is year and value is ProfitAbility
        for idx in range(1, len(year_list)):
            curr_year = year_list[idx]
            prev_year = year_list[idx - 1]
            new_data = ProfitAbility(
                year=curr_year,
                curr_year_list=annual_data[curr_year],
                prev_year_list=annual_data[prev_year]
            )  # make a new instance of ProfitAbility
            self.year2data[curr_year] = new_data

    def get_indicator(self, year):
        """
        get the DevAbility instance of the year
        :param year: the year of develop ability indicator we want to get
        :return: the certain DevAbility instance
        """
        return self.year2data[year]