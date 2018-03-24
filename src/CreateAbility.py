from globalVar import safe_growth_rate, safe_div

class CreateAbility:
    data_name_list = [
        "经营现金增长率",
        "现金流量增长率",
        "自由现金比",
        "销售经营现金比",
        "销售现金比",
        "销售自由现金比"
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
        self.weight = [25, 15, 20, 15, 10, 15]
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
        # 自由现金比
        self.data["free_cash_ratio"] = (curr_fsheet["net_cash_op"] - curr_fsheet["cash_paid_fa"]) / (10**8)
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
        self.score = 0
        for i in range(len(self.data_list)):
            self.score += self.data_list[i] * self.weight[i]


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
        year_list = list(year_set)
        year_list.sort()
        self.year2data = {}  # a dictionary whose key is year and value is CreateAbility
        for idx in range(1, len(year_list)):
            curr_year = year_list[idx]
            prev_year = year_list[idx - 1]
            new_data = CreateAbility(
                year=curr_year,
                curr_year_list=annual_data[curr_year],
                prev_year_list=annual_data[prev_year]
            )  # make a new instance of CreateAbility
            self.year2data[curr_year] = new_data

    def get_indicator(self, year):
        """
        get the DevAbility instance of the year
        :param year: the year of develop ability indicator we want to get
        :return: the certain DevAbility instance
        """
        return self.year2data[year]