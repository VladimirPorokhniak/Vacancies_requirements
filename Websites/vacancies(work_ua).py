import datetime
import json
import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def normalized_str(string: str, for_disp: bool = False):
    if for_disp:
        return str(string).replace('&amp;', '&')
    else:
        return str(string).replace('\\', '\\\\').replace('+', '\\+').replace('.', '\\.').replace('*', '\\*')


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
        self.__vacancies_requirements_dir = vacancies_req_dir
        self.__vacancy_requirements: dict = dict()
        self.__vacancy_requirements_statistics: dict = dict()
        self.vacancies = list()
        self.__prepare()
        driver = Service(os.getcwd() + "/chromedriver(linux)(win).exe")
        chrome_option = Options()
        if self.__debug < 3:
            chrome_option.add_argument('--headless')
        self.__wd = webdriver.Chrome(options=chrome_option, service=driver)

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
        os.remove(file_name)
        wb.save(file_name)
        if self.__debug > 0:
            print('done.')

    def get_vacancies_data(self, search_request) -> None:
        """
        :param search_request: (split search requests by space)
        """
        self.__path = f'vacancies({"_".join(search_request.split())}).json'
        if not self.__load_data():
            try:
                if self.__debug > 0:
                    print("Collecting list of vacancies...", end=' ')
                s1_time = datetime.datetime.now()
                job_ids = self.__get_vacancy_list(search_request)
                f1_time = datetime.datetime.now()
                if self.__debug > 0:
                    print(f'done ({(f1_time - s1_time).seconds}.{int((f1_time - s1_time).microseconds)} secs).')
                    print(f'{len(job_ids)} vacancies were found!')
                s2_time = datetime.datetime.now()
                for index, job_id in enumerate(job_ids):
                    self.vacancies.append(self.__get_vacancy_info(job_id))
                    if self.__debug > 0:
                        print(f'\rCollecting vacancies\' information... {round((index + 1) / len(job_ids) * 100, 2)}%',
                              end='')
                f2_time = datetime.datetime.now()
                if self.__debug > 0:
                    print(f'\rCollecting vacancies\' information... done'
                          f' ({(f2_time - s2_time).seconds}.{int((f2_time - s2_time).microseconds)} secs).')
                    self.__save_data()
            except Exception as e:
                if self.__debug > 0:
                    print('Exception:', e)
            finally:
                self.__wd.close()
                self.__wd.quit()

    def __get_vacancy_list_work_ua(self, search_request) -> list:
        search_request = '-'.join(search_request.split())
        vacancy_list_url = f'https://www.work.ua/en/jobs-it-{search_request}/?advs=1&page='
        vacancy_list = set()
        for number in range(1, 100):
            self.__wd.get(vacancy_list_url + str(number))
            page_data = BeautifulSoup(self.__wd.page_source, 'html.parser')
            if all(i in str(page_data) for i in
                   ['There are no jobs matching your query ', ' with selected filters yet.']):
                if self.__debug > 1:
                    print(number)
                break
            vacs_data = page_data.findAll(attrs={'id': 'pjax-job-list'})
            ids = re.findall(r'<a href="/en/jobs/(\d*)/" title', str(vacs_data))
            vacancy_list.update(ids)
        return list(vacancy_list)

    def __get_vacancy_info_work_ua(self, vacancy_id: str) -> dict:
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
        self.__wd.get(vacancy_url_en)
        page_data = BeautifulSoup(self.__wd.page_source, 'html.parser')
        job_desc = str(page_data.find(attrs={'id': 'job-description'})).lower()
        main_info = normalized_str(page_data.find(attrs={'property': 'og:description'}), for_disp=True)
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
        vacancy = self.__get_vacancy_requirements(vacancy)
        return vacancy

    def __get_vacancy_requirements(self, vacancy: dict) -> dict:
        s: str = vacancy['Job description']
        for pair in self.__vacancy_requirements.items():
            index = list()
            for v in pair[1]:
                index.append(re.search(fr'\b{normalized_str(v)}\b', s))

            if any([i is not None for i in index]):
                vacancy['Job requirements'].append(pair[0])
                self.__vacancy_requirements_statistics[pair[0]] += 1
        if self.__debug > 1:
            print(f'Job requirements:\n{vacancy["Job requirements"]}')
        return vacancy


if __name__ == '__main__':
    s_time = datetime.datetime.now()
    a = Vacancy()
    a.get_vacancies_data('security')
    a.to_excel('report.xlsx')
    f_time = datetime.datetime.now()
    print(f'Done ({(f_time - s_time).seconds}.{int((f_time - s_time).microseconds)} secs).')
