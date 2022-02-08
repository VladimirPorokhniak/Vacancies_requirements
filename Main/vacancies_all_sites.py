import datetime
import json
import os
import re
import sys
import time
import threading
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as c_Options
from selenium.webdriver.chrome.service import Service as c_Service
from selenium.webdriver.firefox.options import Options as f_Options
from selenium.webdriver.firefox.service import Service as f_Service
from selenium.webdriver.common.by import By


class Vacancy:
    def __init__(self, vacancies_req_dir: str = 'vacancies_requirements', show: int = 1, def_param: bool = True):
        """
        :param vacancies_req_dir: path to folder with files with vacancies' requirements
        :param show: 0 - show nothing; 1 - default show; 2 - show debug; 3 - show all.
        :param def_param: uses parameters by default
        """
        self.__debug = show
        self.__path = None
        self.def_param = def_param
        self.__vacancies_requirements_dir = os.path.dirname(__file__) + '/' + vacancies_req_dir
        self.__vacancy_requirements: dict = dict()
        self.__vacancy_requirements_statistics: dict = dict()
        self.__vacancies_links = {'work_ua_links': [], 'dou_ua_links': []}
        self.vacancies = list()
        self.__jobs_desc = []
        self.__prepare()
        # # driver = Service(os.getcwd() + "/chromedriver(linux)")
        # driver = f_Service(os.getcwd() + "/Vacancies_requirements/WebDrivers/geckodriver(linux)")
        # option = f_Options()
        # if self.__debug < 3:
        #      # option.add_argument('--headless')
        #     pass
        # # self.__wd1 = webdriver.Chrome(options=option, service=driver)
        # # self.__wd2 = webdriver.Chrome(options=option, service=driver)
        # self.__wd1 = webdriver.Firefox(options=option, service=driver)
        # # self.__wd2 = webdriver.Firefox(options=option, service=driver)
        # # self.__wd3 = webdriver.Chrome(options=chrome_option, service=driver)

    def __load_data(self):
        if not os.path.exists(self.__path):
            return False
        if self.__debug > 0 and (not self.def_param):
            ans = input(f'Do you want to load data from "{self.__path}" (y)/n?\n>')
        else:
            ans = 'no'
        if not (ans in ['y', 'yes', 'YES', 'Yes', '']):
            return False
        if self.__debug > 0:
            print(f'Loading data from file: "{self.__path}"...', end=' ')
        with open(self.__path, "r") as read_file:
            self.vacancies = json.load(read_file)
        if self.__debug > 0:
            print('done.')
        return True

    def __save_data(self):
        if os.path.exists(self.__path):
            if self.__debug > 0 and (not self.def_param):
                ans = input(
                    f'This file exists!\nCould it overwrite file "{self.__path}" (y) or enter new file name?\n>')
            else:
                ans = 'y'
            if not (ans in ['y', '']):
                self.__path = ans
        if self.__debug > 0:
            print(f'Saving data to file: "{self.__path}"...', end=' ')
        with open(self.__path, "w") as write_file:
            json.dump(self.vacancies, write_file)
        with open('jobs_desc.json', "w", encoding='utf-8') as write_file:
            json.dump(self.__jobs_desc, write_file)
        if self.__debug > 0:
            print('done.')

    def __prepare(self):
        if self.__debug > 0:
            print(f'Preparing...', end=' ')
        reqs = os.listdir(f'{self.__vacancies_requirements_dir}/')
        for req in reqs:
            with open(f'{self.__vacancies_requirements_dir}/{req}', "r") as read_file:
                r = json.load(read_file)
                self.__vacancy_requirements = self.__vacancy_requirements | r
        for k in self.__vacancy_requirements.keys():
            self.__vacancy_requirements_statistics[k] = 0
        if self.__debug > 0:
            print('done.')
        if self.__debug > 0:
            print(f'Files:\n{reqs}')

    def to_excel(self, file_name: str) -> None:
        """
        :param file_name: name of Excel file to safe to
        """
        if self.__debug > 0:
            print(f'Saving data to Excel: "{file_name}"...', end=' ')
        import openpyxl
        wb = openpyxl.workbook.Workbook()
        report = wb.active
        report.append(list(self.vacancies[0].keys()))
        for item in self.vacancies:
            item['More'] = '; '.join(item['More'])
            item['Job requirements'] = '; '.join(item['Job requirements'])
            report.append(list(item.values()))

        report.append([])
        report.append(list(self.__vacancy_requirements_statistics.keys()))
        report.append(list(self.__vacancy_requirements_statistics.values()))
        wb.save(file_name)
        if self.__debug > 0:
            print('done.')

    def __normalized_str(self, string, for_disp: int = 0):
        if for_disp == 0:
            string = str(string).replace('\\', '\\\\').replace('+', '\\+').replace('.', '\\.').replace('*', '\\*')
        if for_disp == 2:
            string1 = ''
            for l in str(string):
                try:
                    print(l, file=open(os.devnull, 'w'))
                except UnicodeEncodeError:
                    pass
                except Exception as e:
                    if self.__debug > 1:
                        print('Exception:', e)
                else:
                    string1 += l
            string = re.sub(r'[a-zа-яёїє]*(([a-zа-яёїє])([A-ZА-ЯЁЇЄ]))', r'\2 \3', str(string1))
        return str(string).replace('&amp;', '&').replace('\xa0', ' ')

    def __get_vacancy_list_dou_ua(self, search_request, webdriver):
        search_request = "+".join(search_request.split())
        vacancy_list_url = f'https://jobs.dou.ua/vacancies/?category=Security&search={search_request}&descr=1'
        webdriver.get(vacancy_list_url)
        try:
            link = webdriver.find_element(By.LINK_TEXT, value='English')
            link.click()
        except Exception as e:
            if self.__debug > 1:
                print('Exception:', e)
        time.sleep(0.5)
        for number in range(1, 100):
            time.sleep(0.5)
            try:
                link = webdriver.find_element(By.LINK_TEXT, value='More jobs')
                link.click()
            except Exception as e:
                if self.__debug > 1:
                    print('Exception:', e)
                    print(number)
                break
        page_data = BeautifulSoup(webdriver.page_source, 'html.parser')
        vacancy_list = set(re.findall(r'<a class="vt" href="(.*?)">', str(page_data)))
        self.__vacancies_links['dou_ua_links'] = list(vacancy_list)

    def __get_vacancy_list_work_ua(self, search_request, webdriver):
        search_request = '-'.join(search_request.split())
        vacancy_list_url = f'https://www.work.ua/en/jobs-it-{search_request}/?advs=1&page='
        vacancy_list = set()
        for number in range(1, 100):
            webdriver.get(vacancy_list_url + str(number))
            page_data = BeautifulSoup(webdriver.page_source, 'html.parser')
            if all(i in str(page_data) for i in
                   ['There are no jobs matching your query ', ' with selected filters yet.']):
                if self.__debug > 1:
                    print(number)
                break
            vacs_data = page_data.findAll(attrs={'id': 'pjax-job-list'})
            ids = re.findall(r'<a href="/en/jobs/(\d*)/" title', str(vacs_data))
            vacancy_list.update(ids)
        self.__vacancies_links['work_ua_links'] = list(vacancy_list)

    def __get_vacancy_info_dou_ua(self, vacancy_url: str, webdriver):
        vacancy = {
            'Date of publishing': '',
            'Seniority level': '',
            'Position name': '',
            'Company': '',
            'City': '',
            'Salary': '',
            'Job requirements': list(),
            'More': list(),
            'Job description': '',
            'Source': 'Dou.ua',
            'Source link': vacancy_url,
        }
        webdriver.get(vacancy_url + '?switch_lang=en')
        page_data = BeautifulSoup(webdriver.page_source, 'html.parser')
        vacancy['Date of publishing'] = \
            re.search(r'\n\t\t\t(.*)\n\n\t\t',
                      self.__normalized_str(page_data.find(attrs={'class': 'date'}), 1)).groups()[
                0]
        vacancy['Position name'] = re.search(r'<h1 class="g-h2">(.*)</h1>',
                                             self.__normalized_str(page_data.find(attrs={'class': 'g-h2'}),
                                                                   1)).groups()[0]
        vacancy['City'] = re.search(r'<span class="place"> (.*)</span>',
                                    self.__normalized_str(page_data.find(attrs={'class': 'place'}), 1)).groups()[0]
        vacancy['Company'] = re.search(r'<a href="(.*)">(.*)</a>',
                                       self.__normalized_str(page_data.find(attrs={'class': 'l-n'}), 1)).groups()[1]
        salary = re.search(r'<span class="salary">(.*)</span>',
                           self.__normalized_str(page_data.find(attrs={'class': 'salary'}), 1))
        vacancy['Salary'] = salary.groups()[0] if salary else ''
        vacancy['Job description'] = self.__normalized_str(
            page_data.find(attrs={'class': 'text b-typo vacancy-section'}).text, 2)
        self.__jobs_desc.append(self.__normalized_str(page_data, 2))
        # vacancy['Seniority level'] =
        # vacancy['More'] =
        vacancy = self.__get_vacancy_requirements(vacancy)
        self.vacancies.append(vacancy)

    def __get_vacancy_info_work_ua(self, vacancy_id: str, webdriver):
        vacancy_url_ua = f'https://www.work.ua/jobs/{vacancy_id}/'
        vacancy_url_en = f'https://www.work.ua/en/jobs/{vacancy_id}/'
        vacancy = {
            'Date of publishing': '',
            'Seniority level': '',
            'Position name': '',
            'Company': '',
            'City': '',
            'Salary': '',
            'Job requirements': list(),
            'More': list(),
            'Job description': '',
            'Source': 'Work.ua',
            'Source link': vacancy_url_ua,
        }
        webdriver.get(vacancy_url_en)
        page_data = BeautifulSoup(webdriver.page_source, 'html.parser')
        job_desc = self.__normalized_str((page_data.find(attrs={'id': 'job-description'})).text, 2)
        self.__jobs_desc.append(self.__normalized_str(page_data, 2))
        main_info = self.__normalized_str(page_data.find(attrs={'property': 'og:description'}), 1)
        if self.__debug > 1:
            print('Job description:', job_desc)
        vacancy['Job description'] = job_desc
        info = re.search(r'content="(.*) needs a (.*)\. Work in (.*?)(,( salary - ([^,]*),)?\s{2}(((.*)?'
                         r'(, more than (\d*) years? of experience)(, (.*))?)|(.*)))?\.', main_info).groups()
        vacancy['Position name'] = info[1]
        vacancy['Company'] = info[0]
        vacancy['City'] = info[2]
        vacancy['Salary'] = info[5] if info[5] else ''
        vacancy['Seniority level'] = f'{info[10]}+' if info[10] else ''
        vacancy['More'] = info[13].split(', ') if info[13] else (
                info[8].split(', ') + (info[12].split(', ') if info[12] else [])) if (
                info[8] or info[12] or info[13]) else []
        date = re.search(r'Job from\xa0(.*) (.*), (.*)</span>',
                         str(page_data.find(attrs={'class': 'cut-bottom-print'}))).groups()
        vacancy['Date of publishing'] = '-' if 'not' in date else f'{date[1]} {date[0]} {date[2]}'
        if 'remote' in vacancy['More']:
            vacancy['City'] += ', remote'
            vacancy['More'].remove('remote')
        vacancy = self.__get_vacancy_requirements(vacancy)
        self.vacancies.append(vacancy)

    def __get_vacancy_requirements(self, vacancy: dict) -> dict:
        s: str = vacancy['Job description'].lower()
        for pair in self.__vacancy_requirements.items():
            index = list()
            for v in pair[1]:
                index.append(re.search(fr'\b{self.__normalized_str(v)}\b', s))

            if any([i is not None for i in index]):
                vacancy['Job requirements'].append(pair[0])
                self.__vacancy_requirements_statistics[pair[0]] += 1
        if self.__debug > 1:
            print(f'Job requirements:\n{vacancy["Job requirements"]}')
        vacancy['Job requirements'].sort()
        return vacancy

    def get_vacancies_data(self, search_request) -> None:
        """
        :param search_request: (split search requests by space)
        """
        driver = f_Service(os.getcwd() + "/Vacancies_requirements/WebDrivers/geckodriver(linux)")
        option = f_Options()
        if self.__debug < 3:
            option.headless = True
        self.__wd1 = webdriver.Firefox(options=option, service=driver)
        self.__path = f'vacancies({"_".join(search_request.split())}).json'
        if not self.__load_data():
            try:
                if self.__debug > 0:
                    print("Collecting list of vacancies...", end=' \n')
                s1_time = datetime.datetime.now()
                self.__get_vacancy_list_work_ua(search_request, self.__wd1)
                self.__get_vacancy_list_dou_ua(search_request, self.__wd1)
                all_jobs = len(self.__vacancies_links['dou_ua_links']) + len(self.__vacancies_links['work_ua_links'])
                f1_time = datetime.datetime.now()
                if self.__debug > 0:
                    print(f'done ({(f1_time - s1_time).seconds}.{int((f1_time - s1_time).microseconds)} secs).')
                    print(f'{all_jobs} vacancies were found!')
                s2_time = datetime.datetime.now()
                index = 0
                for job in self.__vacancies_links['work_ua_links']:
                    self.__get_vacancy_info_work_ua(job, self.__wd1)
                    if self.__debug > 0:
                        print(f'\rCollecting vacancies\' information... {round((index + 1) / all_jobs * 100, 2)}%',
                              end='')
                    index += 1
                for job in self.__vacancies_links['dou_ua_links']:
                    self.__get_vacancy_info_dou_ua(job, self.__wd1)
                    if self.__debug > 0:
                        print(f'\rCollecting vacancies\' information... {round((index + 1) / all_jobs * 100, 2)}%',
                              end='')
                    index += 1
                f2_time = datetime.datetime.now()
                if self.__debug > 0:
                    print(f'\rCollecting vacancies\' information... done'
                          f' ({(f2_time - s2_time).seconds}.{int((f2_time - s2_time).microseconds)} secs).')
                    self.__save_data()
            except Exception as e:
                if self.__debug > 0:
                    print('Exception:', e)
            finally:
                self.__wd1.close()
                self.__wd1.quit()

    def get_vacancies_data_th(self, search_request) -> None:
        """
        :param search_request: (split search requests by space)
        """
        driver = c_Service(os.getcwd() + "/Vacancies_requirements/WebDrivers/chromedriver(linux)")
        option = c_Options()
        if self.__debug < 3:
            option.headless = True
        self.__wd1 = webdriver.Chrome(options=option, service=driver)
        self.__wd2 = webdriver.Chrome(options=option, service=driver)
        self.__path = f'vacancies({"_".join(search_request.split())}).json'
        if not self.__load_data():
            try:
                if self.__debug > 0:
                    print("Collecting list of vacancies...", end=' ')
                s1_time = datetime.datetime.now()
                job_ids_work_ua = threading.Thread(target=self.__get_vacancy_list_work_ua, args=(search_request, self.__wd1),
                                                   name='work_ua(1)')
                job_ids_dou_ua = threading.Thread(target=self.__get_vacancy_list_dou_ua, args=(search_request, self.__wd2),
                                                  name='dou1_ua(1)')
                job_ids_work_ua.start()
                job_ids_dou_ua.start()
                job_ids_work_ua.join()
                job_ids_dou_ua.join()
                f1_time = datetime.datetime.now()
                all_jobs = len(self.__vacancies_links['dou_ua_links']) + len(self.__vacancies_links['work_ua_links'])
                if self.__debug > 0:
                    print(f'done ({(f1_time - s1_time).seconds}.{int((f1_time - s1_time).microseconds)} secs).')
                    print(f'{all_jobs} vacancies were found!')
                s2_time = datetime.datetime.now()
                index1 = 0
                index2 = 0

                def work_ua():
                    nonlocal index1, index2
                    for job in self.__vacancies_links['work_ua_links']:
                        self.__get_vacancy_info_work_ua(job, self.__wd1)
                        if self.__debug > 0:
                            print(
                                f'\rCollecting vacancies\' information... {round((index1 + index2 + 1) / all_jobs * 100, 2)}%',
                                end='')
                        index1 += 1

                def dou_ua():
                    nonlocal index1, index2
                    for job in self.__vacancies_links['dou_ua_links']:
                        self.__get_vacancy_info_dou_ua(job, self.__wd2)
                        if self.__debug > 0:
                            print(
                                f'\rCollecting vacancies\' information... {round((index1 + index2 + 1) / all_jobs * 100, 2)}%',
                                end='')
                        index2 += 1

                job_ids_work_ua = threading.Thread(target=work_ua, name='work_ua(2)')
                job_ids_dou_ua = threading.Thread(target=dou_ua, name='dou2_ua(2)')
                job_ids_work_ua.start()
                job_ids_dou_ua.start()
                job_ids_work_ua.join()
                job_ids_dou_ua.join()
                f2_time = datetime.datetime.now()
                if self.__debug > 0:
                    print(f'\rCollecting vacancies\' information... done'
                          f' ({(f2_time - s2_time).seconds}.{int((f2_time - s2_time).microseconds)} secs).')
                    self.__save_data()
            except Exception as e:
                if self.__debug > 0:
                    print('Exception:', e)
            finally:
                if self.__debug > 0:
                    print('Closing web-drivers...', end=' ')
                self.__wd1.close()
                self.__wd2.close()
                # self.__wd3.close()
                self.__wd1.quit()
                self.__wd2.quit()
                # self.__wd3.quit()
                if self.__debug > 0:
                    print('done.')


if __name__ == '__main__':
    s_time = datetime.datetime.now()
    a = Vacancy()
    a.get_vacancies_data_th('security')
    a.to_excel('report(all).xlsx')
    f_time = datetime.datetime.now()
    print(f'Done ({(f_time - s_time).seconds}.{int((f_time - s_time).microseconds)} secs).')