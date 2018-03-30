from .NoResponseError import NoResponseError
from .Crawler import *
from .globalVar import *
from xlsxwriter.worksheet import Worksheet


class ProfitStatement:
    def __init__(self, stockid, year, date):
        self.data_list = []
        self.data = {}
        self.year = year
        temp_date = str(year) + date
        web = 'http://stockdata.stock.hexun.com/2008/lr.aspx?stockid=' + stockid + '&accountdate=' + temp_date
        msg = get_page(web)
        for htmlslice in r2.findall(msg):
            if "strong" not in htmlslice and temp_date not in htmlslice:
                if '--' in htmlslice:
                    self.data_list.append(0)
                elif htmlslice == '':
                    continue
                else:
                    s = htmlslice.replace(",", "")
                    try:
                        self.data_list.append(float(s))
                    except ValueError:
                        pass
        for i in range(len(profit_sheet_content)):
            self.data[profit_sheet_content[i]] = self.data_list[i]

    def get_year(self):
        return self.year

    def get_list(self):
        return self.data_list

    def get_data(self):
        return self.data

    def data_add(self, other):
        for i in range(len(self.data_list)):
            self.data_list[i] += other.data_list[i]
        for key in profit_sheet_content:
            self.data[key] += other.data[key]



class ProfitData:
    def __init__(self, stockid, startyear, finalyear, date):
        """
        :param stockid: string, the stock code of the company
        :param startyear: int, the first year the program want to fetch
        :param finalyear: itn, the last year the program want to fetch
        :param date: string, the date related to the season, the first season is 03.15, the second season is 06.30,
            > the third season is 09.30, the annual season is 12.31
        """
        self.year_set = set()
        self.year2sheet = {}
        web = 'http://stockdata.stock.hexun.com/2008/lr.aspx?stockid='+stockid+'&accountdate='
        msg = get_page(web)
        if msg is None:
            raise NoResponseError(stockid, startyear, finalyear, date)
            return
        p = r.findall(msg)
        for wholestr in p:
            find_list = r1.findall(wholestr)
            for slice in find_list:
                '''
                slice has two types:
                    the first is 'year.month.day' like '2017.12.31'
                    the second is year+season like '17年年度'
                    we wanna get the first type
                '''
                if date not in slice:
                    find_list.remove(slice)
            # now the find list only has the date related to our season
            for year in range(startyear, finalyear + 1):
                temp_date = str(year) + date
                if temp_date not in find_list:
                    continue
                new_sheet = ProfitStatement(stockid=stockid, year=year, date=date)
                self.year_set.add(year)
                self.year2sheet[year] = new_sheet

    def get_sheet(self, year):
        """
        :param year: year of the sheet we want
        :return: instance of the balance sheet of the year in the company
        """
        return self.year2sheet[year]

    def del_sheet(self, year):
        """
        :param year: year of the sheet we want to delete
        :return: no return
        """
        if year in self.year_set:
            self.year_set.remove(year)
            self.year2sheet.pop(k=year, default=None)

    def write_data(self, sheet: Worksheet, year_list):
        row = 0
        for year in year_list:
            sheet.write(row, 0, year)
            sheet.write_row(row, 1, self.get_sheet(year).data_list)
            row += 1
