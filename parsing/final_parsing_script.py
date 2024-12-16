import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from tqdm import tqdm

start_url = 'https://vtomske.ru/tag/{}'

def get_available_themes():
    start_url = 'https://vtomske.ru/'

    soup = BeautifulSoup(requests.get(start_url).text, 'html.parser')

    links = soup.find_all('a')

    tag_pairs = []

    for link in links:
        href = link.get('href', '')

        if '/tag/' in href:

            tag = href.split('/tag/')[-1]

            text = link.text.strip()

            tag_pairs.append({
                'Тэг': tag,
                'Текст': text.lower()
            })
    
    return tag_pairs[:10] #После десятого элемента рубрики дублируются

themes_list_of_dict = get_available_themes()
themes_list = []

print('На сайте представлены следующие тематики:')

for i in themes_list_of_dict:
    print(i['Текст'])
    themes_list.append(i['Текст'])

while True:
    user_input = input('Пожалуйста, укажите интересующую вас тематику: ').lower() #Пользователь указывает тематику

    if user_input in themes_list:
        print(f'Выбраная тематика: {user_input}')
        break
    else:
        print('Тематики не обнаружено. Повторите ввод.')
        continue

for i in themes_list_of_dict:
    if user_input == i['Текст']:
        tag = i['Тэг']

start_url = start_url.format(tag)

print(start_url)

#Функция, получающая окончание ссылки для получения всех страниц новостей конкретной тематики

def extract_link_pattern(inital_url):
    '''Функция возвращает ссылку, на следующую страницу (next) содержащую новости'''
    
    response = requests.get(inital_url).text

    html_structure = BeautifulSoup(response, 'html.parser')

    next_button = html_structure.findAll('a', class_= 'btn lenta_pager_next') #Содержит HTML-тэг, в формате строки

    pattern = r"\?down=\d+"

    try:
        return re.findall(pattern, str(next_button[0]))[0]
    except:
        return 0

def form_link_list(initial_url):
    '''Функция получает начальную ссылку на новостную тематику с сайта vtomske.ru в след. формате:
    https://vtomske.ru/tag/russia
    И возвращает список ссылок на все страницы новостей по данной новостной тематике.'''
    
    
    string_to_be_formatted = f"{initial_url}{{}}"

    links_list = []

    links_list.append(initial_url)

    while True:
        next_pattern = extract_link_pattern(initial_url) #Переменная содержит в себе паттерн продолжения

        if next_pattern == 0:
            break #Цикл прекращается, если на странице отсутсвует кнопка 'Раньше' == Новости по тематике закончились.

        next_link = string_to_be_formatted.format(next_pattern) #Форматируем строку - ссылку, добавляя в нее продолжение

        links_list.append(next_link) #Сохраняем ссылку в список ссылок

        initial_url = next_link

    return links_list

def extract_news_links(url):
    '''Функция, позволяющая извлечь список URL для всех новостей, находящихся на странице.
    Возвращает список (python list), состоящий из завершенных URL'''
    response = requests.get(url).text

    soup = BeautifulSoup(response, 'html.parser')

    raw_list = soup.findAll('a', class_="lenta_material") #Содержит в список, из которого следует извлечь ссылку на новость

    extract_pattern = r'href="(.*?)"' #паттерн регулярного выражения, позволяющий выделить окончание новости

    urls_final_list = []

    for tag in raw_list:
        
        tag = str(tag)

        result = re.findall(extract_pattern, tag)

        urls_final_list.append(result[0])

    return urls_final_list

def extract_title_and_text(news_url):
    '''Функция извлекает следующий аспекты из новостной статьи:
    1. Новостной заголовок.
    2. Текст новостной статьи.
    3. Дату публикации.
    4. Тэги.
    На вход получает ссылку на конкретную новость.'''

    start_link = 'https://vtomske.ru'

    full_link_url = start_link + news_url

    beautiful_html_structure = BeautifulSoup(requests.get(full_link_url).text, 'html.parser')

    headline = beautiful_html_structure.findAll('h1')[0]

    article_text = beautiful_html_structure.findAll('p')

    #Извлечение даты

    publication_date = beautiful_html_structure.findAll('time', class_="material-date")

    date_pattern = r'\d{4}-\d{2}-\d{2}'

    date = re.findall(date_pattern, str(publication_date))[0]

    #/Извлечение даты

    #Извлечение тегов

    tags_raw = beautiful_html_structure.findAll('div', class_="material-tags")

    tags_pattern = r">\w+<"

    tags = re.findall(tags_pattern, str(tags_raw))

    for index in range(0, len(tags)):
        tags[index] = tags[index].replace(">", "").replace("<", "")

    #/Излвечение тэгов

    #Возвращаем результат

    final_dict = {
        'Заголовок': str(headline),
        'Текст новости': str(article_text),
        'Дата публикации': str(date),
        'Тэги': str(tags)
    }
    
    return final_dict

def parse(theme_url):
    '''Функция, осуществляющая парсинг конкретной тематике с сайта vtomske.ru.
    Ссылка должна вести на существующую тематику и иметь ввиду, типа:
    https://vtomske.ru/tag/russia
    Возвращает датафрейм и сохраняет его в активную директорию'''
    news_pages = form_link_list(theme_url)

    print(f"По выбранной тематике на сайте представлено {len(news_pages)} страниц новостей")

    print('Процесс сбора новостей запущен...\nПрогресс обработки страниц:')

    information_list = [] #Лист, содержащий в себе информацию по каждой новости

    for page in tqdm(news_pages):
        news_list = extract_news_links(page) #Список, содержащий в себе ссылки на конкретные новости с одной страницы.

        for news in news_list:
            news_info = extract_title_and_text(news)
            information_list.append(news_info)
    
    final_df = pd.DataFrame(information_list)

    final_df.to_csv(f'новости_тематики_{user_input}.csv')

    return final_df

news_df = parse(start_url)