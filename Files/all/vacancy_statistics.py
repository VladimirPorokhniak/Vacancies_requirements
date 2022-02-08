from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import re
import json
from bs4 import BeautifulSoup


class Vacancy:
    def __init__(self, file_to_save: str, debug: int = 0):
        self.__debug = debug
        self.__path = file_to_save
        self.__vacancy_requirements: dict = dict()
        self.__vacancy_requirements_statistics:dict = dict()
        self.vacancies = list()
        self.__prepare()
        # if os.path.exists(self.__path):
        #     ans = input(f'Do you want to load data from "{self.__path}" (y)/n?\n>')
        #     if ans in ['y', 'yes', 'YES', 'Yes', '']:
        #         self.__load_info()
        driver = Service(os.getcwd() + "/chromedriver(linux)(win).exe")
        chrome_option = Options()
        if self.__debug < 2:
            chrome_option.add_argument('--headless')
        self.__wd = webdriver.Chrome(service=driver, options=chrome_option)

    def __load_info(self):
        print(f'Loading data from file: "{self.__path}"...')
        with open(self.__path, "r") as read_file:
            self.vacancies = json.load(read_file)
        print('Data has loaded.')

    def __save_info(self):
        # if os.path.exists(self.__path):
        #     ans = input(f'This file exists! \nCould it overwrite file "{self.__path}" (y) or enter new file name?\n>')
        #     if ans not in ['y', 'yes', 'YES', 'Yes', '']:
        #         self.__path = ans
        print(f'Saving data to file: "{self.__path}"...')
        with open(self.__path, "w") as write_file:
            json.dump(self.vacancies, write_file)
        print('Data has saved.')

    def __prepare(self):
        print(f'Preparing...', end=' ')
        reqs = os.listdir('../vacancies_requirements/')
        print(reqs)
        for req in reqs:
            with open(f'vacancies_requirements/{req}', "r") as read_file:
                r = json.load(read_file)
                self.__vacancy_requirements = self.__vacancy_requirements | r
        for k in self.__vacancy_requirements.keys():
            self.__vacancy_requirements_statistics[k] = 0
        print('done.')

    def to_excel(self, file_name: str):
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

        pass

    def get_vacancies_data(self, search_request) -> None:
        try:
            print("Gathering list of vacancies...", end=' ')
            job_ids = self.__get_vacancy_list(search_request)
            print(' done.')
            print(f'{len(job_ids)} vacancies were found! ')
            print('Gathering vacancies\' information...', end=' ')
            for job_id in job_ids:
                self.vacancies.append(self.__get_vacancy_info(job_id))
            print(' done.')
        except Exception as e:
            if self.__debug > 0:
                print('Exception:', e)
        finally:
            self.__save_info()
            self.__wd.quit()

    def __get_vacancy_list(self, search_request) -> list:
        search_request = '-'.join(search_request.split())
        vacancy_list_url = f'https://www.work.ua/en/jobs-it-{search_request}/?advs=1&page='
        vacancy_list = set()
        for number in range(1, 100):
            self.__wd.get(vacancy_list_url + str(number))
            page_data = str(BeautifulSoup(self.__wd.page_source, 'html.parser')).replace('&amp;', '&')
            if all(i in page_data for i in ['There are no jobs matching your query ', ' with selected filters yet.']):
                if self.__debug:
                    print(number)
                break
            i_s = page_data.find('<div id="pjax-job-list">')
            l = page_data[i_s + 26:]
            i_f = l.find('<nav>')
            l_data = (l[:i_f].split('<a name='))[1:]
            for vac in l_data:
                b = re.search(r'"(.*)"></a>(.*)', str(vac)).groups()
                vacancy_list.add(b[0])
                if self.__debug > 0:
                    print(b[0])
        return list(set(vacancy_list))

    def __get_vacancy_info(self, vacancy_id: str) -> dict:
        vacancy_url_ua = f'https://www.work.ua/jobs/{vacancy_id}/'
        vacancy_url_en = f'https://www.work.ua/en/jobs/{vacancy_id}/'
        vacancy = {
            'Date of publishing': '',
            'Seniority level': '',
            'Position name': '',
            'Company': '',
            'City': '',
            "Salary": '',
            'Job requirements': list(),
            "More": list(),
            'Job description': '',
            'Source': 'Work.ua',
            'Source link': vacancy_url_ua,
        }

        self.__wd.get(vacancy_url_en)
        page_data = str(BeautifulSoup(self.__wd.page_source, 'html.parser')).replace('&amp;', '&')

        i_s = page_data.find('og:title')
        i_f = page_data.find('og:image')
        main_info = (page_data[i_s:i_f]).split('<')
        i_s = page_data.find('<div id="job-description">')
        job_desc = page_data[i_s + 26:]
        i_f = job_desc.find('</div>')
        job_desc = job_desc[:i_f].lower()
        if self.__debug > 0:
            print('Job description:', job_desc)
        vacancy['Job description'] = job_desc

        for m_i in range(len(main_info)):
            if "description" in main_info[m_i]:
                s = ((((main_info[m_i].split('content="'))[1]).split('"'))[0]).replace('  ', ' ')
                b = re.search(r'(.*) needs a (.*). Work in (.*).', str(s)).groups()
                b2 = b[2].split(', ')
                vacancy['Position name'] = b[1]
                vacancy['Company'] = b[0]
                vacancy['City'] = b2[0]
                for i in b2[1:]:
                    if 'salary' in i:
                        vacancy['Salary'] = re.search(r'salary - (.*)', str(i)).groups()[0]
                    elif 'experience' in i:
                        vacancy['Seniority level'] = '{0}+'.format(
                            str(re.search(r'more than (.*) year(.*)', str(i)).groups()[0]))
                    else:
                        vacancy['More'].append(i)
        index = page_data.find('"text-muted"')
        s = ((((page_data[index:index + 50].split('>'))[1]).split('<'))[0])[9:]
        date = re.match(r'(.*) (.*), (.*)', str(s)).groups()
        vacancy['Date of publishing'] = '-' if 'not' in s else f'{date[1]} {date[0]} {date[2]}'
        vacancy = self.__get_vacancy_requirements(vacancy)
        return vacancy

    def __get_vacancy_requirements(self, vacancy: dict) -> dict:
        for pair in self.__vacancy_requirements.items():
            print(pair)
            for v in pair[1]:
                s: str = vacancy['Job description']
                print(s)
            index = re.search(fr'\b{v}\b', )

            print(index)
            if index:
                vacancy['Job requirements'].append(pair[0])
                self.__vacancy_requirements_statistics[pair[0]] += 1
        # print(vacancy)
        return vacancy


if __name__ == '__main__':
    import datetime
    s_time = datetime.datetime.now()
    a = Vacancy('vacancies.json')

    a.get_vacancies_data('security')
    a.to_excel('report.xlsx')
    f_time = datetime.datetime.now()
    print(f'Done ({(f_time - s_time).seconds}.{int((f_time - s_time).microseconds)} secs).')
