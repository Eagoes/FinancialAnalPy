from globalVar import safe_div

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
        self.weight = [50, 30, 20]
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
        self.score = 0
        for i in range(len(self.data_list)):
            self.score += self.data_list[i] * self.weight[i]


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
        year_list = list(year_set)
        year_list.sort()
        self.year2data = {}  # a dictionary whose key is year and value is Solvency
        for idx in range(1, len(year_list)):
            curr_year = year_list[idx]
            prev_year = year_list[idx - 1]
            new_data = Solvency(
                year=curr_year,
                curr_year_list=annual_data[curr_year],
                prev_year_list=annual_data[prev_year]
            )  # make a new instance of Solvency
            self.year2data[curr_year] = new_data

    def get_indicator(self, year):
        """
        get the DevAbility instance of the year
        :param year: the year of develop ability indicator we want to get
        :return: the certain DevAbility instance
        """
        return self.year2data[year]