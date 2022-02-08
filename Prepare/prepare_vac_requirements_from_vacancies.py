import json
import os
import sys
import pyperclip
from colorama import Fore
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from pynput import keyboard
from threading import Thread

Next = None


def active():
    global Next
    print('Go next page')
    Next = True


def normalized_str(string: str, for_disp: bool = False):
    if not for_disp:
        string = str(string).replace('\\', '\\\\').replace('+', '\\+').replace('.', '\\.').replace('*', '\\*')
    return str(string).replace('&amp;', '&').replace('\xa0', ' ')


def get_vacancy_requirements(job_desc: str, reqs: list) -> str:
    wbs = '$wbs#'
    start = job_desc.find('<body')
    s = job_desc[start:]
    for v in reqs:
        try:
            # s = re.sub(fr'\b({normalized_str(v)})\W', rf'')
            res = re.findall(fr'(\b({normalized_str(v)})[^\w$])', s, re.IGNORECASE)
            # print(v, ':', res)
            if res:
                # print(res)
                for item in res:
                    text_new = f'<b style="color:red;">{wbs.join(list(item[1]))}</b>{item[0][-1:]}'
                    s = s.replace(item[0], text_new)
        except Exception as e:
            print('Exception:', e)
    job_desc = job_desc[:start] + s.replace(wbs, '')
    return job_desc


def load_req(file_path: str):
    if os.path.exists(file_path):
        print(f'Loading requirements from file: "{file_path}"...', end='')
        try:
            with open(file_path, "r") as read_file:
                data = json.load(read_file)
            print(' done.')
        except Exception as e:
            print(Fore.RED, f'(Exception: {e})')
    return data


def save_req(file_path: str, data: dict):
    # print(f'Saving requirements to file: "{file_path}"...', end='')
    try:
        with open(file_path, "w") as write_file:
            json.dump(data, write_file)
        # print(' done.')
    except Exception as e:
        print('Exception:', e)


def load(file_path: str):
    if os.path.exists(file_path):
        print(f'Loading file: "{file_path}"...', end='')
        try:
            with open(file_path, "r") as read_file:
                data: dict = json.load(read_file)
            print(' done.')
        except Exception as e:
            print(Fore.RED, f'(Exception: {e})')
    return data


# def add_req(reqs: dict):
#     while True:
#         print('List of categories:')
#         for i in enumerate(reqs.keys()):
#             print(f'[{i[0] + 1}] - {i[1]}')
#         item = input('New item:')
#         if item == '':
#             break
#         print('List of categories:')
#         for i in enumerate(reqs.keys()):
#             print(f'[{i[0] + 1}] - {i[1]}')
#         category = input('What category is item from (choose number or enter name to create new one)? ')
#         cat = list(reqs.keys())
#         if category == '':
#             break
#         if category.isdigit():
#             category = cat[int(category) - 1]
#         if category not in cat:
#             reqs[category] = list()
#         if item not in reqs[category]:
#             reqs[category].append(item.lower())
#     return reqs

def add_req(reqs: list):
    global Next
    item = ''
    pyperclip.copy('')
    while not (len(item) or Next):
        item = pyperclip.paste()
        if item.lower() not in reqs and len(item):
            print('Item:', item)
            reqs.append(item.lower())
            reqs.sort(key=lambda s: len(s), reverse=True)
    return reqs


def get_text(vacancies: list, reqs: list):
    global Next
    driver = Service(os.getcwd() + "/chromedriver(linux)")
    chrome_option = Options()
    wd = webdriver.Chrome(options=chrome_option, service=driver)
    path = os.path.abspath('vacancy.html')
    url = 'file://' + path
    for data in vacancies:
        Next = False
        html = str(data).encode().decode('utf-8')
        with open(path, 'w') as f:
            for item in html:
                try:
                    f.write(item)
                except:
                    pass
        wd.get(url)
        while True:
            print('Press <Ctrl>+Z to go next page', file=sys.stderr)
            html = get_vacancy_requirements(str(data).encode().decode('utf-8'), reqs).encode().decode('utf-8')
            with open(path, 'w') as f:
                for item in html:
                    try:
                        f.write(item)
                    except Exception as e:
                        print('Exception:', e)
                        pass
            wd.refresh()
            reqs = add_req(reqs)
            save_req('ALL_REQUIREMENTS.json', reqs)
            if Next:
                break


# def prepare_vac_requirements(directory_name: str) -> None:
#     if not os.path.exists(directory_name):
#         print('This directory does not exist!')
#         sys.exit()
#     files = os.listdir(directory_name)
#     for i in range(len(files)):
#         print(f'[{i + 1}] - {files[i]}')
#     file_name = input('What file do you want to save to (choose number or enter name to create new one)? ')
#     if file_name.isdigit():
#         file_name = files[int(file_name) - 1]
#     data = dict()
#     if os.path.exists(directory_name + '/' + file_name):
#         print(f'Loading data from file: "{file_name}"...', end='')
#         try:
#             with open(directory_name + '/' + file_name, "r") as read_file:
#                 data: dict = json.load(read_file)
#             print(' done.')
#         except Exception as e:
#             print(Fore.RED, f'(Exception: {e})')
#     while True:
#         ans = input('Would you like to:\n[0] - add items to all categories;\n[1] - edit categories\n[2] - exit\n?\n>')
#         if ans == '0':
#             while True:
#                 item = input('New item:')
#                 if item == '':
#                     break
#                 print('List of categories:')
#                 for i in enumerate(data.keys()):
#                     print(f'[{i[0] + 1}] - {i[1]}')
#                 category = input('What category is item from (choose number or enter name to create new one)? ')
#                 cat = list(data.keys())
#                 if category == '':
#                     break
#                 if category.isdigit():
#                     category = cat[int(category) - 1]
#                 if category not in cat:
#                     data[category] = list()
#                 if item not in data[category]:
#                     data[category].append(item.lower())
#         elif ans == '1':
#             while True:
#                 print('List of categories:')
#                 for i in enumerate(data.keys()):
#                     print(f'[{i[0] + 1}] - {i[1]}')
#                 category = input(
#                     'What category do you want to choose (choose number or enter name to create new one)? ')
#                 cat = list(data.keys())
#                 if category == '':
#                     break
#                 if category.isdigit():
#                     category = cat[int(category) - 1]
#                 if category not in cat:
#                     data[category] = list()
#                 while True:
#                     print(f'Category: {category}.\nItems:')
#                     print(data[category])
#                     ans = input(
#                         'Would you like to:\n[0] - delete category;\n[1] - add item;\n[2] - delete item\n?\n>')
#                     if ans == '0':
#                         if input(f'Do you really want to delete "{category}" y/(n)? ') == 'y':
#                             data.pop(category)
#                             print('Category was deleted!')
#                             break
#                     elif ans == '1':
#                         it = input('New item:')
#                         if it not in data[category]:
#                             data[category].append(it.lower())
#                     elif ans == '2':
#                         it = input('Item name to delete:')
#                         if it in data[category]:
#                             data[category].remove(it)
#                     else:
#                         break
#                 if input('Do you want to continue editing categories (y)/n? ') not in ['y', 'yes', 'YES', 'Yes', '']:
#                     break
#         elif ans == '2':
#             break
#     print(f'Saving data to file: "{file_name}"...', end='')
#     try:
#         with open(directory_name + '/' + file_name, "w") as write_file:
#             json.dump(data, write_file)
#         print(' done.')
#     except Exception as e:
#         print('Exception:', e)

def requests_to_categories():
    reqs: list = load_req('ALL_REQUIREMENTS.json')
    data: dict = load_req('vacancies_requirements/ALL_REQUIREMENTS_BY_CATEGORIES.json')
    for item in reqs:
        def in_list(it):
            for k in data.keys():
                if it in data[k]:
                    return True
            return False
        if in_list(item):
            continue
        print('Item:', item)
        print('List of categories:')
        for i in enumerate(data.keys()):
            list(data[i[1]]).sort(key=lambda s: len(s), reverse=True)
            print(f'[{i[0] + 1}] - {i[1]}')
        category = input(f'What category is item from (choose number or enter name to create new one or number 0 to save witt name "{str(item).capitalize()}")? ')
        cat = list(data.keys())
        if category == '':
            break
        if category == '0':
            data[str(item).capitalize()] = list()
            data[str(item).capitalize()].append(item.lower())
        else:
            if category.isdigit():
                category = cat[int(category) - 1]
            if category not in cat:
                data[category] = list()
            if item not in data[category]:
                data[category].append(item.lower())
        save_req('vacancies_requirements/ALL_REQUIREMENTS_BY_CATEGORIES.json', data)


def add():
    h = keyboard.GlobalHotKeys({'<ctrl>+z': active})
    main = Thread(target=get_text, args=(load('jobs_desc.json'), load_req('ALL_REQUIREMENTS.json'),))
    h.start()
    main.start()
    h.join()
    main.join()


if __name__ == "__main__":
    requests_to_categories()
