from globalVar import safe_growth_rate

class DevAbility:
    data_name_list = [
        "销售增长率",
        "资产增长率",
        "净利润增长率",
        "净资产增长率",
        "固定资产增长率"
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
        self.weight = [25, 15, 20, 25, 15]
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
        self.score = 0
        for i in range(len(self.data_list)):
            self.score += self.data_list[i] * self.weight[i]


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
        year_list = list(year_set)
        year_list.sort()
        self.year2data = {}  # a dictionary whose key is year and value is DevAbility
        for idx in range(1, len(year_list)):
            curr_year = year_list[idx]
            prev_year = year_list[idx - 1]
            new_data = DevAbility(
                year=curr_year,
                curr_year_list=annual_data[curr_year],
                prev_year_list=annual_data[prev_year]
            )  # make a new instance of DevAbility
            self.year2data[curr_year] = new_data

    def get_indicator(self, year):
        """
        get the DevAbility instance of the year
        :param year: the year of develop ability indicator we want to get
        :return: the certain DevAbility instance
        """
        return self.year2data[year]