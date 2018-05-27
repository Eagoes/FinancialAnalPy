from .Company import Company
from .Industry import Industry
from .globalVar import module_path
import pickle
import os

class DataContainer:
    """
    use for the basic program class, containing a list of company and a industry instance, working
    as a platform to bring an opportunity for them to transit the data
    """
    def __init__(self, idlist, startyear, finalyear, season, curr_year, pickleload, pickledump):
        self.company_list = []
        if not pickleload:  # do not require load company instances from pickle file, then init new companies
            for stockid in idlist:
                print("initing the company " + stockid)
                company = Company(stockid, startyear, finalyear, season)
                self.company_list.append(company)
                if pickledump:  # require to write the company instance to file
                    pickle.dump(company, open(module_path+"/bin/" + stockid, "wb"))
        else:  # require to load company from pickle file
            for stockid in idlist:
                try:
                    company = pickle.load(open(module_path+"/bin/" + stockid, "rb"))
                    print("found company " + stockid)
                except (FileNotFoundError, pickle.UnpicklingError):
                    print("file "+stockid+" not found")
                    company = Company(stockid, startyear, finalyear, season)
                    if pickledump:
                        pickle.dump(company, open(module_path+"/bin/"+stockid, "wb"))
                self.company_list.append(company)
        self.industry = Industry(self.company_list, curr_year)

    def calculate(self):
        for company in self.company_list:
            company.calculate()
        self.industry.calculate()
        self.industry.alloc_data_for_company(self.company_list)

    def write(self):
        for company in self.company_list:
            company.write_xlsx()
        self.industry.write_xlsx()