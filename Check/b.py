import datetime
import json
import os
import re
import sys
import time
import threading
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

vacancy_url = 'https://www.work.ua/en/jobs/4743780/'
driver = Service(os.getcwd() + "\WebDrivers\chromedriver(win).exe")
option = Options()
wd = webdriver.Chrome(options=option, service=driver)
wd.get(vacancy_url)
page_data = BeautifulSoup(wd.page_source, 'html.parser')
print(page_data.find(attrs={'id': 'job-description'}).text)
print()
print(page_data.h3.(
    
))
wd.close()
wd.quit()