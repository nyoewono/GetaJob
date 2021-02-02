#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 12:40:22 2021

@author: nathanaelyoewono
"""

# data storing and manipulation
import pandas as pd
import numpy as np
import os 
import re
from datetime import datetime

# scraping tools
import requests
from selenium import webdriver
import time
from bs4 import BeautifulSoup

# add directories
import sys
sys.path.insert(1, '/Users/nathanaelyoewono/Project/GetaJob/database')

# import db
from db import JobDB

class IndeedScrape:
    
    """
    This class scrape all job openings in Indeed with specified role and location.
    The scraped jobs will be stored in a sql database called jobdata.db.
    This database will be showcased using GUIß
    """
    
    # adjustable
    path = os.getcwd()+'/chromedriver'
    website = 'Indeed'
    
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
        self.browser = webdriver.Chrome(executable_path = IndeedScrape.path, options = chrome_options)
        
        # alternative url
        url = f'https://au.indeed.com/?r=aus'
        
        self.browser.get(url)
        
    
    def run_query(self):
        
        self.browser.find_element_by_id('text-input-what').send_keys(self.role)
        self.browser.find_element_by_id('text-input-where').send_keys(self.loc)
        self.browser.find_element_by_xpath('/html/body/div[1]/div[2]/div[3]/div[2]/div/div/div/form/div[3]/button').click()
        time.sleep(2)
        
    def _get_job_cards(self):
        
        # get max page
        self._get_max_page()
        start = 0
        
        role_sr = self.role.split()
        role_sr = "+".join(role_sr)
        
        loc = self.loc.split()
        loc = "+".join(loc)
        
        duplicated_cards = 0
        
        for i in range(start, self.max_page, 10):
            
            if duplicated_cards > 20:
                break
            
            self._find_popup()
            
            url = f'https://au.indeed.com/jobs?q={role_sr}&l={loc}&start={i}'
            self.browser.get(url)
            time.sleep(2)
            
            self._find_popup()
            
            jobs = self.browser.find_elements_by_class_name("jobsearch-SerpJobCard")
            
            #print(jobs)
            #print(len(jobs))
            self._find_popup()
            
            for each in jobs:
                role, company, link, salary, location, comp_link = self._get_details(each)
                
                get_comp_id = self.db.get_company_port_group_id(company, 'company')
                get_port_id = self.db.get_company_port_group_id(IndeedScrape.website, 'portal')
                # fail here
                get_group_id = self.db.get_company_port_group_id(self.role.lower(), 'group_search')
                
                # check if the company already exist in db or not
                if get_comp_id==None:
                    
                    # add company
                    get_comp_id = self.db.create_company((company,comp_link))
                
                if get_port_id==None:
                    # add website
                   get_port_id = self.db.create_portal((IndeedScrape.website,))
                   
                if get_group_id==None:
                    # add group
                   get_group_id = self.db.create_group((self.role.lower(),))
                texts_detail = self._get_text(link)
                 # add job
                try:
                    today = datetime.date(datetime.now())
                    
                    job_id = self.db.create_job((role, get_comp_id, link, location, salary, get_port_id, today))
                except:
                    # duplicate
                    job_id = None
                    duplicated_cards += 1
                    pass
                
                # store the many-many relationship between job and role selected
                if job_id != None and get_group_id!=None:
                    # fail here
                    self.db.create_group_job((job_id, get_group_id))
                break
            break
        
        self.browser.close()
            # break
        
    def _find_popup(self):
        """Get rid of all pop-up"""
        try:
            self.browser.find_element_by_class_name('popover-x-button-close').click()
            time.sleep(1)
        except:
            pass
    
    def _get_text(self, link):
        page = requests.get(link)
        # parse with BFS
        soup = BeautifulSoup(page.text, 'html.parser')
        
        try:
            texts = soup.find(class_='jobsearch-jobDescriptionText').find_all('p')
        except:
            #texts = soup.find(class_='jobsearch-JobComponent-description').find_all('p')
            texts = ''
            
        all_text = []
        
        for i in texts:
            
            p = i.get_text()
            all_text.append(p)
            
            lists = self._extract_list(i)
            
            if lists != None:
                all_text.append(lists)

        return texts
    
    def _extract_list(self, p):
        for sibling in p.next_siblings:
            if sibling.name == 'ul':
                return [li.text for li in sibling.find_all('li')]
            if sibling.name == 'p':
                return None 
        
        
    def _get_details(self, job):
        role_and_link = job.find_element_by_class_name('title')
        role = role_and_link.text
        role = role.replace('new', '')
        role = role.replace('\n', '')
        link = role_and_link.find_element_by_xpath('a').get_attribute('href')
        company = job.find_element_by_class_name('company').text
        
        # get company's link
        try:
            comp_link = job.find_element_by_class_name('company').find_element_by_xpath('a').get_attribute('href')
        except:
            comp_link = ''
        try:
            salary = job.find_element_by_class_name('salaryText').text
            # print(salary)
        except:
            salary = ""
        try:
            location = job.find_element_by_class_name('location').text
            # print(location)
        except:
            location = ""
        
        return (role, company, link, salary, location, comp_link)
    
    def _get_max_page(self):
        self.max_page = self.browser.find_element_by_id('searchCountPages').text
        self.max_page = int(self.max_page.split(' ')[-2])

    
    def run(self):
        # SET DB
        self.db = JobDB()
        #self.db.create_table()
        if self.db.create_connection()==1:
            self._open_browser()
            self.run_query()
            self._get_job_cards()
            self.db.conn.close()
        else:
            print('Failed to connect to db')

job = IndeedScrape('Quantitative Developer', 'Melbourne')
job.run()
    