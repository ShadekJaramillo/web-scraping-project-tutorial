import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

url = 'https://listado.mercadolibre.com.co/papeleria#D[A:papeleria]&origin=UNKNOWN&as.comp_t=SUG&as.comp_v=papele&as.comp_id=SUG'

def get_items_mercadolibre(url):
    try:
        response = requests.get(url, timeout = 20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        items_html = soup.find_all('div', 'poly-card__content')

        return items_html
    except requests.exceptions.HTTPError as e:
        print(f'Error while fetching the html from {url[50]}...: {e}')

def parse_item(html_item):
    title_component = html_item.find_all('a','poly-component__title')
    current_price_component = html_item.find_all('div','poly-price__current')
    discount_component = current_price_component[0].find_all('span', "andes-money-amount__discount")
    seller_component = html_item.find_all('span', "poly-component__seller")
    rating_component = html_item.find_all('span', 'poly-reviews__rating')

    title = title_component[0].contents[0]
    link = title_component[0].get('href')
    current_price_val = current_price_component[0].find_all('span','andes-money-amount__fraction')[0].contents[0]
    discount = discount_component[0].contents[0] if discount_component else None
    seller = seller_component[0].contents[0] if seller_component else None
    rating = rating_component[0].contents[0] if rating_component else None
    
    return {
        'product': title,
        'URL': link,
        'price': current_price_val,
        'rating': rating,
        'discount': discount,
        'seller': seller
    }

if __name__ == '__main__':
    items_html = get_items_mercadolibre(url)
    items_dict = list(map(parse_item, items_html))
    df = pd.DataFrame(items_dict)
    print(df)
