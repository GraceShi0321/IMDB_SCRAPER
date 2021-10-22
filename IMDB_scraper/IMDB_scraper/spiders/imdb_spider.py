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
    # This is the name of the spider that we will later call on in command line
    name       = 'imdb_spider'
    # This URL is the starting point, it is the IMDb site for the TV show friends
    start_urls = ['https://www.imdb.com/title/tt0108778/']
    
    def parse(self, response):
        """
        This function assumes you start on a movie page, 
        and then navigate to the Cast & Crew page
        """
        # first get the link of the Cast & Crew page
        # By inspecting the developer tools, we found that the link to the Cast & Crew page is inside an a.ipc-metadata-list-item__icon-link element
	# We will want to first select that element and then get the attribute "href"
        Cast_Crew_URL = response.css("a.ipc-metadata-list-item__icon-link")[0].attrib["href"]
        # The link provided by "href" is missing the prefix, we will want to get the full URL in order to navigate to there
        prefix        = "https://www.imdb.com"
        CastCrew_URL  = prefix + Cast_Crew_URL
        # We will now want to get to the Cast & Crew page
	# Once there, the parse_full_credits(self,response) should be called for each actor/actress listed 
        yield Request(CastCrew_URL, callback = self.parse_full_credits)
        
        
    def parse_full_credits(self, response):
        """
        This function assumes that you start on the Cast & Crew page. 
        Its purpose is to yield a scrapy.Request for the page of each actor/actress listed on the page.
        Crew members are not included.
        """
        # Get the link of each actor/actress listed on the page
	# By inspecting the developer tools, we see that there is a td.primary_photo element for each actor/actress
	# And the first child of td.primary_photo element with type a contains the link to each actor/actress’s page
        cast_links    = response.css("td.primary_photo").css("a:first-child")
        # We will again want the attribute "href" of the a element
        cast_suffixes = [link.attrib["href"] for link in cast_links]
        # Again add the prefix to get the full URL to each actor/actress’s page
        cast_URL      = ["https://www.imdb.com" + suffix for suffix in cast_suffixes]
        # we will now want to get to each actor/actress’s page 
        # Then the method parse_actor_page(self, response) should be called when the actor/actress’s page is reached
        for url in cast_URL:    
            yield Request(url, callback = self.parse_actor_page)
        
    def parse_actor_page(self, response):
        """
        This function assumes you start on the page of an actor/actress. 
        It yields a dictionary with two key-value pairs, of the form 
        {"actor/actress" : actor_name, "movie_or_TV_name" : movie_or_TV_name}
        """
        # Get the name of the actor/actress
	# We will first select the span.itemprop element and then grab the text which contains the name of the actor/actress
        ActorActress_name = response.css("span.itemprop::text")[0].get()
        # Get all movies and TV shows for this actor/actress
	# After inspecting the developer tools, we found that:
	# The div.filmo-category-section element, which is a sibling of the div.filmo-head-actor(actress) element, contains all the works for each actor/actress
	# Then inside the div.filmo-category-section element, we want the text of the a element which being the first child of each div.filmo-row-even(odd)
        works             = response.css('div[id*="filmo-head-act"] + div.filmo-category-section div[class*="filmo-row"] b a:first-child::text')
        works             = [work.get() for work in works]
        # Then we want to save these information
        for movie_or_TV_name in works:
            yield {
                    "actor/actress" : ActorActress_name,
                    "movie_or_TV_name": movie_or_TV_name
                    }
