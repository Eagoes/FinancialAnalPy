from Company import Company

class Industry(Company):
    """
    working as a high-level company whose data is the sum of the wholee companies, it can be regarded as the
    industry of all companies
    """
    def __init__(self, company_list, curr_year):
        """
        the init function of class Industry
        :param company_list: a list of companies, the Industry instance is the sum of these companies
        :param curr_year: using for updating the final year
        """
        self.year_set = set()
        for i in range(1997, curr_year+1):
            self.year_set.add(i)
        for company in company_list:
            self.year_set &= company.year_set
        for company in company_list:
            company.trim_year_set(master_set=self.year_set)