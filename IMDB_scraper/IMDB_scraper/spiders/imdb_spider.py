# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 15:28:13 2021

@author: Grace Shi
"""

# to run 
# scrapy crawl imdb_spider -o movies.csv

from scrapy.spiders import Spider
from scrapy.http import Request

class ImdbSpider(Spider):
    """
    A simple spider class to illustrate scraping the IMBd site by going from one's favorite movie or TV show site
    to crawl and extract other movies and TV shows that also star the cast of one's favorite movie or TV show. 
    
    The scraped information will be saved in a csv file when crawling the spider
    The location of the files saved, as well as the total number of requests sent, are controlled by settings.py
    """
    
    name       = 'imdb_spider'

    start_urls = ['https://www.imdb.com/title/tt0108778/']
    
    def parse(self, response):
        """
        This function assumes you start on a movie page, 
        and then navigate to the Cast & Crew page
        """
        # first get the link of the Cast & Crew page
        Cast_Crew_URL = response.css("a.ipc-metadata-list-item__icon-link")[0].attrib["href"]
        prefix        = "https://www.imdb.com"
        CastCrew_URL  = prefix + Cast_Crew_URL
        # Once there, the parse_full_credits(self,response) should be called
        yield Request(CastCrew_URL, callback = self.parse_full_credits)
        
        
    def parse_full_credits(self, response):
        """
        This function assumes that you start on the Cast & Crew page. 
        Its purpose is to yield a scrapy.Request for the page of each actor/actress listed on the page.
        Crew members are not included.
        """
        # get the link of each actor/actress listed on the page
        cast_links    = response.css("td.primary_photo").css("a:first-child")
        cast_suffixes = [link.attrib["href"] for link in cast_links]
        cast_URL      = ["https://www.imdb.com" + suffix for suffix in cast_suffixes]
        # the method parse_actor_page(self, response) should be called when the actor/actress’s page is reached
        for url in cast_URL:    
            yield Request(url, callback = self.parse_actor_page)
        
    def parse_actor_page(self, response):
        """
        This function assumes you start on the page of an actor/actress. 
        It yields a dictionary with two key-value pairs, of the form 
        {"actor/actress" : actor_name, "movie_or_TV_name" : movie_or_TV_name}
        """
        # get the name of the actor/actress
        ActorActress_name = response.css("span.itemprop::text")[0].get()
        # get all movies and TV shows for this actor/actress
        works             = response.css('div.filmo-category-section div[class*="filmo-row"] a:first-child::text').getall()
        for movie_or_TV_name in works:
            yield {
                    "actor/actress" : ActorActress_name,
                    "movie_or_TV_name": movie_or_TV_name
                    }
        
        
        
        
        
        
        
        
        
        
        
        