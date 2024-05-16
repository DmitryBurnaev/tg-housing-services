import sqlite3
from datetime import datetime

import httpx
from lxml import html


def parse_website(url):
    with httpx.Client() as client:
        response = client.get(url)    
    tree = html.fromstring(response.content)
    # Предполагаем, что таблица находится в теге <table> и имеет две колонки
    rows = tree.xpath('//table/tr')
    data = []
    for row in rows:
        columns = row.xpath('td/text()')
        if len(columns) == 2:
            data.append((columns[0], columns[1]))
    return data



# Основная функция
def main():
    url = 'http://example.com'  # Замените на актуальный URL
    db_name = 'parsed_data.db'
    
    # Парсинг сайта
    parsed_data = parse_website(url)
    
    # Создание таблицы в базе данных
    create_table(db_name)
    
    # Вставка данных в таблицу
    insert_data(db_name, response.text, parsed_data)

if __name__ == "__main__":
    main()