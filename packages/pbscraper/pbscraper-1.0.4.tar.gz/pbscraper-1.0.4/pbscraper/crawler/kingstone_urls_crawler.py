from .base_urls_crawler import BaseUrlsCrawler

import requests
from bs4 import BeautifulSoup
import re
import datetime
import lxml

class KingstoneUrlsCrawler(BaseUrlsCrawler):
    def __init__(self):
        pass
        
    def is_target_list(self, url):
        is_list = False
        match = re.search('www\.kingstone\.com\.tw\/.+', url)
        if match:
            is_list = True
        return is_list
    
    def scrape_list_to_urls(self, url, res):
        
        pure_html = res.text
        soup = BeautifulSoup(pure_html,features="lxml")

        # ---- 取下整頁的urls ----
        #prd_urls = [(('https://www.kingstone.com.tw' + u['href']) if 'kingstone.com' not in u['href'] else u['href']) for u in soup.select('li.displayunit h3.pdnamebox a')]
        prd_urls = []
        for item in soup.select('li.displayunit'):
            u=item.select_one('h3.pdnamebox a')
            ptext=item.select_one('div.buymixbox').text.replace(',','')
            match=re.findall(r"[^\d]*(\d+)?元", ptext)
            p=''
            if match:
                p = match[-1]
            prd_urls.append({'url': (('https://www.kingstone.com.tw' + u['href']) if 'kingstone.com' not in u['href'] else u['href']), 
                           'price':int(p)})

        # ---- 檢查有無下一頁，有則回填url ----
        elem = elem = soup.select_one('ul.pagination li.pageNext a')

        if elem:
            self._next_pg_url = ('https://www.kingstone.com.tw' + elem['href']) if 'kingstone.com' not in elem['href'] else elem['href']
        else:
            self._next_pg_url = None
        return prd_urls
        
    def get_next_pg_after_scraped(self):
        return self._next_pg_url
        
        
    