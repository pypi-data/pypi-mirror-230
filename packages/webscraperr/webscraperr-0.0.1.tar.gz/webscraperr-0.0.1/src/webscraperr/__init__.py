from typing import Callable, List, Dict
from .db import WebScraperDBMySQL
import parsel
import requests
import json

class WebScraperRequest:
    def __init__(self, config: dict):
        self.config = config
        self.get_items_urls_func : Callable[[parsel.Selector], List[str]] = None
        self.get_next_page_func : Callable[[parsel.Selector], str] = None
        self.parse_info_func : Callable[[parsel.Selector], Dict] = None
    
    def scrape_items_urls(self, urls: list):
        with requests.Session() as s:
            for url in urls:
                next_page = url[:]
                while next_page:
                    print("SCRAPING URLS", next_page)
                    response = s.get(next_page)
                    if next_page:
                        response = s.get(next_page)
                    if not response.ok:
                        print("FAILED GETTING URLS ", next_page)
                        continue
                    selector = parsel.Selector(text=response.text)
                    items_urls = [[i] for i in self.get_items_urls_func(selector)]
                    if len(items_urls) > 0:
                        with WebScraperDBMySQL(self.config['MYSQL']) as conn:
                            conn.save_urls(items_urls)
                            print(f"FOUND {len(items_urls)} URLS IN", next_page)
                    else:
                        print("NO URLS FOUND IN", next_page)
                    next_page = None
                    if self.get_next_page_func:
                        next_page = self.get_next_page_func(selector)
    
    def scrape_items_infos(self):
        items = []
        with WebScraperDBMySQL(self.config['MYSQL']) as conn:
            items = conn.get_all_without_info()
        with requests.Session() as s:
            for item in items:
                print("GETTING INFO ", item['URL'])
                response = s.get(item['URL'])
                if not response.ok:
                    print("FAILED GETTING INFO ", item['URL'])
                    continue
                selector = parsel.Selector(text=response.text)
                info = self.parse_info_func(selector)
                if info is None:
                    print("NO INFO ", item['URL'])
                    continue
                with WebScraperDBMySQL(self.config['MYSQL']) as conn:
                    conn.set_info_by_id(item['ID'], json.dumps(info))
            
    


