import json
import os
import sys
from colorama import Fore


def prepare_vac_requirements(directory_name: str) -> None:
    if not os.path.exists(directory_name):
        print('This directory does not exist!')
        sys.exit()
    files = os.listdir(directory_name)
    for i in range(len(files)):
        print(f'[{i + 1}] - {files[i]}')
    file_name = input('What file do you want to save to (choose number or enter name to create new one)? ')
    if file_name.isdigit():
        file_name = files[int(file_name) - 1]
    data = dict()
    if os.path.exists(directory_name + '/' + file_name):
        print(f'Loading data from file: "{file_name}"...', end='')
        try:
            with open(directory_name + '/' + file_name, "r") as read_file:
                data: dict = json.load(read_file)
            print(' done.')
        except Exception as e:
            print(Fore.RED, f'(Exception: {e})')
    while True:
        ans = input('Would you like to:\n[0] - add items to all categories;\n[1] - edit categories\n[2] - exit\n?\n>')
        if ans == '0':
            while True:
                item = input('New item:')
                if item == '':
                    break
                print('List of categories:')
                for i in enumerate(data.keys()):
                    print(f'[{i[0] + 1}] - {i[1]}')
                category = input('What category is item from (choose number or enter name to create new one)? ')
                cat = list(data.keys())
                if category == '':
                    break
                if category.isdigit():
                    category = cat[int(category) - 1]
                if category not in cat:
                    data[category] = list()
                if item not in data[category]:
                    data[category].append(item.lower())
        elif ans == '1':
            while True:
                print('List of categories:')
                for i in enumerate(data.keys()):
                    print(f'[{i[0] + 1}] - {i[1]}')
                category = input(
                    'What category do you want to choose (choose number or enter name to create new one)? ')
                cat = list(data.keys())
                if category == '':
                    break
                if category.isdigit():
                    category = cat[int(category) - 1]
                if category not in cat:
                    data[category] = list()
                while True:
                    print(f'Category: {category}.\nItems:')
                    print(data[category])
                    ans = input(
                        'Would you like to:\n[0] - delete category;\n[1] - add item;\n[2] - delete item\n?\n>')
                    if ans == '0':
                        if input(f'Do you really want to delete "{category}" y/(n)? ') == 'y':
                            data.pop(category)
                            print('Category was deleted!')
                            break
                    elif ans == '1':
                        it = input('New item:')
                        if it not in data[category]:
                            data[category].append(it.lower())
                    elif ans == '2':
                        it = input('Item name to delete:')
                        if it in data[category]:
                            data[category].remove(it)
                    else:
                        break
                if input('Do you want to continue editing categories (y)/n? ') not in ['y', 'yes', 'YES', 'Yes', '']:
                    break
        elif ans == '2':
            break
    print(f'Saving data to file: "{file_name}"...', end='')
    try:
        with open(directory_name + '/' + file_name, "w") as write_file:
            json.dump(data, write_file)
        print(' done.')
    except Exception as e:
        print('Exception:', e)


if __name__ == "__main__":
    prepare_vac_requirements('vacancies_requirements')
