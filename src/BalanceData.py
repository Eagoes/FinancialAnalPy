from Crawler import *
from NoResponseError import NoResponseError


class BalanceData:
    def __init__(self, stockid, startyear, finalyear, date):
        '''

        :param stockid: string, the stock code of the company
        :param startyear: int, the first year the program want to fetch
        :param finalyear: itn, the last year the program want to fetch
        :param date: string, the date related to the season, the first season is 03.15, the second season is 06.30, the third season is 09.30, the annual season is 12.31
        '''
        self.data_list = []
        web = 'http://stockdata.stock.hexun.com/2008/zcfz.aspx?stockid='+stockid+'&accountdate='
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
                web1 = web + temp_date
                msg1 = get_page(web1)
                for htmlslice in r2.findall(msg1):
                    if "strong" not in htmlslice and temp_date not in htmlslice:
                        if '--' in htmlslice:


