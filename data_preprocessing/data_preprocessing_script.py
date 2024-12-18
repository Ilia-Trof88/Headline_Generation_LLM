import pandas as pd
import re

user_input = input('Пожалуйста, введите название файла. Файл должен находится в директории скрипта и иметь расширение .csv\n:')

while True:
    if user_input.endswith('.csv') or user_input.endswith('.xlsx'):
        print('Указан корректный файл')
        break
    else:
        print('Указанный файл отсутсвует в директории и/или имеет недопустимое расширение. Повторите ввод')
        
    user_input = input('Введите название файла\n:')

def data_prep(target_string:str) -> str:
    '''Выполняет предобработку полученной строки. Удаляет HTML-тэги и подстроки в виде ссылок.
    
    Args:
        target_string (str): Непредобработанная строка
    
    Returns:
        str: Предобработанная строка
    '''
    #I. Опишем паттерн для удаления нежелательной подстроки внутри новости#

    sub_string_pattern = r"<a[^>]*>" #[^>] - означает: "Найди все, что не является '>' ноль или более раз"

    #/I. Опишем паттерн для удаления нежелательной подстроки внутри новости#

    #II. Опишем паттерн для удаления HTML-разметки#

    tag_pattern = r"</*\w*\d*>"

    #/II. Опишем паттерн для удаления HTML-разметки#

    #III. Выполним операции преобразования.

    target_string = re.sub(sub_string_pattern, '', target_string)

    target_string = re.sub(tag_pattern, '', target_string)
    
    return target_string.replace('[', '').replace(']', '').strip()


if user_input.endswith('.csv'):
    try:
        df = pd.read_csv(user_input)
    except:
        print('Произошла ошибка при чтении файла. Убедитесь в корректности данных')
elif user_input.endswith('.xlsx'):
    try:
        df = pd.read_excel(user_input)
    except:
        print('Произошла ошибка при чтении файла. Убедитесь в корректности данных')

df.drop(columns = ['Unnamed: 0'], inplace = True)

print('Процесс предобработки запущен...')

needed_cols = list(df.columns)

for col in needed_cols:
    df[col] = df[col].apply(data_prep)

print('Процесс предобработки завершился успешно.')

while True:

    user_format = input("Введите формат в котором вы хотите сохранить файл: xlsx или csv: ")

    correctness_flag = False

    allowed_formats = ['xlsx', 'csv']

    if user_format != allowed_formats[0] and user_format != allowed_formats[-1]:
        print(f'Введен недопустимый формат. Вы ввели: {user_format}\n Допустимые форматы xlsx и csv. Повторите ввод')
    
    elif user_format in allowed_formats:
        print(f'Введен корректный формат. Ваш файл будет сохранен в расшиирении {user_format}')
        
        file_name = input('Введите название файла (любое, совместимое с вашей файловой системой): ')
        break
    
if user_format == 'csv':
    df.to_csv(f'{file_name}.csv')
else:
    df.to_excel(f'{file_name}.xlsx')

print(f"Файл успешно сохранен под названием {file_name}.{user_format}")

    