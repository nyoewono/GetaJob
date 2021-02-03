#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 19:55:10 2021

@author: nathanaelyoewono
"""

# data storing and manipulation
from datetime import datetime

# scraping tools
from selenium import webdriver
import time

# add directories
import sys
sys.path.insert(1, '/Users/nathanaelyoewono/Project/GetaJob/database')

# import db
from db import JobDB

class SeekScrape:
    
    """
    This class scrape all job openings in Seek with specified role and location.
    The scraped jobs will be stored in a sql database called jobdata.db.
    This database will be showcased using GUI
    """
    
    # adjustable
    path = path = '/Users/nathanaelyoewono/Project/GetaJob/scraper/chromedriver'
    website = 'Seek'
    
    def __init__(self, role, location):
        self.role = role
        self.loc = location
    
    def _open_browser(self):
        """Open up the browser and set yahoo finance as the default url"""
        # set the chrome optionse
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--incognito") 
    
        # open browser
        self.browser = webdriver.Chrome(executable_path = SeekScrape.path, options = chrome_options)
        
        # alternative url
        url = 'https://www.seek.com.au/'
        
        self.browser.get(url)
        
    def run_query(self):
        
        # input the search parameter in the search bar
        self.browser.find_element_by_id('keywords-input').send_keys(self.role)
        self.browser.find_element_by_id('SearchBar__Where').send_keys(self.loc)
        time.sleep(2)
        
        # get the search button
        self.browser.find_element_by_id('react-autowhatever-1-section-0-item-0').click()
        self.browser.find_element_by_xpath('/html/body/div[1]/div/div[4]/div/div[1]/section/div[2]/div/div/form/button').click()
        time.sleep(2)
        
    def _get_articles(self):
        
        """
        Since Seek's algo is sorting by relevance, me might as well just 
        take the top 50 page (early implementation)
        """
        
        duplicated_cards = 0
        
        start = 1
        end = 10
        
        # iterate over each page (but only limit to 50)
        for page in range(start, end+1):
            
            if duplicated_cards > 20:
                break
            
            # set the new page
            cur_url = self.browser.current_url+f'?page={page}'
            self.browser.get(cur_url)
            time.sleep(2)
            
            # get all job cards
            try:
                jobs = self.browser.find_element_by_class_name('_3MPUOLE')
                jobs = jobs.find_elements_by_class_name('_2m3Is-x')
            except:
                print('Jobs not found')
                break
                
            # iterate over each job cards to get the details
            for i in jobs:
                role, link, company, location, salary = self._get_details(i)
                
                # Don't apply the company is not stated
                if role != '' or link != '' or company != '':
                
                    get_comp_id = self.db.get_company_port_group_id(company, 'company')
                    get_port_id = self.db.get_company_port_group_id(SeekScrape.website, 'portal')
                    get_group_id = self.db.get_company_port_group_id(self.role.lower(), 'group_search')
                    
                    # check if the company already exist in db or not
                    if get_comp_id==None:
                        
                        # add company
                        get_comp_id = self.db.create_company((company,))
                    
                    if get_port_id==None:
                        # add website
                       get_port_id = self.db.create_portal((SeekScrape.website,))
                       
                    if get_group_id==None:
                        # add group
                       get_group_id = self.db.create_group((self.role.lower(),))
                    
                    # add job
                    today = datetime.date(datetime.now())
                    get_job_id = self.db.check_job_exist((role, get_comp_id))
                    if get_job_id==None:
                        job_id = self.db.create_job((role, get_comp_id, link, location, salary, get_port_id, today))
                    else:
                        job_id = None
                        duplicated_cards += 1
                    
                    # store the many-many relationship between job and role selected
                    if job_id != None and get_group_id!=None:
                        self.db.create_group_job((job_id, get_group_id))
                        
        self.browser.close()
 
        
        
    def _get_details(self, obj):
        
        try:
            title = obj.find_element_by_xpath('span[2]/span/h1/a').text
        except:
            title=''
        try:
            link = obj.find_element_by_xpath('span[2]/span/h1/a').get_attribute('href')
        except:
            link=''
        try:
            company = obj.find_element_by_xpath('span[5]/span/a').text
        except:
            company = ''
        
        try:
            location = obj.find_element_by_xpath('div[1]/span[2]/span/strong/span/span').text
            location = location.split(' ')[-1]
        except:
            location = ''
        
        try:
            salary = obj.find_element_by_xpath('div[1]/span[3]/span').text
            if 'classification' in salary:
                salary = ''
        except:
            salary = ''
        
        return (title, link, company, location, salary)
        
    def run(self):
        
        # SET DB
        self.db = JobDB()
        if self.db.create_connection()==1:
            self._open_browser()
            self.run_query()
            self._get_articles()
            self.db.conn.close()
        else:
            print('Failed to connect to db')
    
# scrape = SeekScrape('Data Analyst', 'Melbourne')
# scrape.run()
    
        