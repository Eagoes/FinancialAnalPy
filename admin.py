import json
import datetime
import os
from src.DataContainer import DataContainer
from src.globalVar import module_path


if __name__ == '__main__':
    if not os.path.exists(module_path+"/result"):
        os.mkdir(module_path+"/result")
    time = datetime.datetime.now()
    curr_year = time.year
    f = open(module_path+"/settings.json", "r")
    settings = json.load(f)
    company_list = settings['company']
    startyear = settings['start year']
    finalyear = settings['final year']
    season = settings['season']
    pickleload = settings['load from file']
    pickledump = settings['write to file']
    platform = DataContainer(company_list, startyear, finalyear, season, curr_year, pickleload, pickledump)
    platform.calculate()
    platform.write()