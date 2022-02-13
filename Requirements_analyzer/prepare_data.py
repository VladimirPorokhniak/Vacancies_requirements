import datetime
import json
import os
import re
import time
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from googletrans import Translator

translator = Translator()

vacancies_links = {}
vacancies = []

def get_vacancy_list_dou_ua(search_request, webdriver):
    search_request = "+".join(search_request.split())
    vacancy_list_url = f'https://jobs.dou.ua/vacancies/?category=Security&search={search_request}&descr=1'
    webdriver.get(vacancy_list_url)
    try:
        link = webdriver.find_element(By.LINK_TEXT, value='English')
        link.click()
    except Exception as e:
        print('Exception_get_vacancy_list_dou_ua1:', e)
    time.sleep(0.5)
    for number in range(1, 100):
        time.sleep(0.5)
        try:
            link = webdriver.find_element(By.LINK_TEXT, value='More jobs')
            link.click()
        except Exception as e:
            print('Exception_get_vacancy_list_dou_ua2:', e)
            break
    page_data = BeautifulSoup(webdriver.page_source, 'html.parser')
    vacancy_list = set(re.findall(r'<a class="vt" href="(.*?)">', str(page_data)))
    vacancies_links['dou_ua_links'] = list(vacancy_list)

def get_vacancy_list_work_ua(search_request, webdriver):
    search_request = '-'.join(search_request.split())
    vacancy_list_url = f'https://www.work.ua/en/jobs-it-{search_request}/?advs=1&page='
    vacancy_list = set()
    for number in range(1, 100):
        webdriver.get(vacancy_list_url + str(number))
        page_data = BeautifulSoup(webdriver.page_source, 'html.parser')
        if all(i in str(page_data) for i in
                   ['There are no jobs matching your query ', ' with selected filters yet.']):
            break
        vacs_data = page_data.findAll(attrs={'id': 'pjax-job-list'})
        ids = re.findall(r'<a href="/en/jobs/(\d*)/" title', str(vacs_data))
        vacancy_list.update(ids)
    vacancies_links['work_ua_links'] = list(vacancy_list)

def get_vacancy_info_dou_ua(vacancy_url: str, webdriver):
    webdriver.get(vacancy_url + '?switch_lang=en')
    page_data = BeautifulSoup(webdriver.page_source, 'html.parser')
    job_info = page_data.find(attrs={'class': 'l-vacancy'}).text
    translation = translator.translate(job_info, src='en', dest='ru')
    # print(f"({translation.src}) ({translation.dest})")
    translation = translator.translate(translation.text)
    # print(f"({translation.src}) ({translation.dest})")
    vacancies.append([vacancy_url, translation])

def get_vacancy_info_work_ua(vacancy_id: str, webdriver):
    vacancy_url_ua = f'https://www.work.ua/jobs/{vacancy_id}/'
    vacancy_url_en = f'https://www.work.ua/en/jobs/{vacancy_id}/'
    webdriver.get(vacancy_url_en)
    page_data = BeautifulSoup(webdriver.page_source, 'html.parser')
    job_desc = (page_data.find(attrs={'id': 'job-description'})).text
    translation = translator.translate(job_desc, src='en', dest='ru')
    # print(f"({translation.src}) ({translation.dest})")
    translation = translator.translate(translation.text)
    # print(f"({translation.src}) ({translation.dest})")
    vacancies.append([vacancy_url_ua, translation])

def get_vacancies_data(search_request) -> None:
    """
    :param search_request: (split search requests by space)
    """
    driver = Service(os.getcwd() + "\WebDrivers\chromedriver(win).exe")
    option = Options()
    option.headless = True
    userAgent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
    option.add_argument(f'user-agent={userAgent}')
    # sys.exit()
    wd = webdriver.Chrome(options=option, service=driver)
    path = f'vacancies({"_".join(search_request.split())}).json'
    try:
        print("Collecting list of vacancies...", end=' \n')
        s1_time = datetime.datetime.now()
        get_vacancy_list_work_ua(search_request, wd)
        get_vacancy_list_dou_ua(search_request, wd)
        all_jobs = len(vacancies_links['dou_ua_links']) + len(vacancies_links['work_ua_links'])
        f1_time = datetime.datetime.now()
        print(f'done ({(f1_time - s1_time).seconds}.{int((f1_time - s1_time).microseconds)} secs).')
        print(f'{all_jobs} vacancies were found!')
        s2_time = datetime.datetime.now()
        index = 0
        for job in vacancies_links['work_ua_links']:
            get_vacancy_info_work_ua(job, wd)
            print(f'\rCollecting vacancies\' information... {round((index + 1) / all_jobs * 100, 2)}%', end='')
            index += 1
        for job in vacancies_links['dou_ua_links']:
            get_vacancy_info_dou_ua(job, wd)
            print(f'\rCollecting vacancies\' information... {round((index + 1) / all_jobs * 100, 2)}%', end='')
            index += 1
        f2_time = datetime.datetime.now()
        print(f'\rCollecting vacancies\' information... done'
                          f' ({(f2_time - s2_time).seconds}.{int((f2_time - s2_time).microseconds)} secs).')
        save_data(path)
    except NameError as e:
        print('Exception:', e)
    finally:
        wd.close()
        wd.quit()
            
def save_data(path):
        print(f'Saving data to file: "{path}"...', end=' ')
        with open(path, "w", encoding='utf-8') as write_file:
            json.dump(vacancies, write_file)
        print('done.')



if __name__ == '__main__':
    s_time = datetime.datetime.now()
    get_vacancies_data('security')
    f_time = datetime.datetime.now()
    print(f'Done ({(f_time - s_time).seconds}.{int((f_time - s_time).microseconds)} secs).')