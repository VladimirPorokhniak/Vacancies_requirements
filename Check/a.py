import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


vacancy_url = 'https://jobs.dou.ua/companies/hacken/vacancies/66381/'
driver = Service(os.getcwd() + "\WebDrivers\chromedriver(win).exe")
option = Options()
wd = webdriver.Chrome(options=option, service=driver)
wd.get(vacancy_url + '?switch_lang=en')
page_data = BeautifulSoup(wd.page_source, 'html.parser')
print(page_data.find(attrs={'class': 'l-vacancy'}).text.replace('—', '\n—'))
wd.close()
wd.quit()