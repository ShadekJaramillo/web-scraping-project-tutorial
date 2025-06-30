from bs4 import BeautifulSoup
import requests
import sqlite3
import pandas as pd

URLs = [
    'https://listado.mercadolibre.com.co/arte-papeleria-merceria/papeleria/papeleria_Desde_0_NoIndex_True',
    'https://listado.mercadolibre.com.co/arte-papeleria-merceria/papeleria/papeleria_Desde_49_NoIndex_True',
    'https://listado.mercadolibre.com.co/arte-papeleria-merceria/papeleria/papeleria_Desde_97_NoIndex_True'
]

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

    obj_title = title_component[0].contents[0]
    obj_link = title_component[0].get('href')
    obj_price = current_price_component[0].find_all('span','andes-money-amount__fraction')[0].contents[0]
    obj_discount = discount_component[0].contents[0] if discount_component else None
    obj_seller = seller_component[0].contents[0] if seller_component else None
    obj_rating = rating_component[0].contents[0] if rating_component else None

    title = str(obj_title) if obj_title else None
    link = str(obj_link) if obj_link else None
    price = int(str(obj_price).replace('.','')) if obj_price else None
    discount = int(str(obj_discount).replace('% OFF','')) if obj_discount else 0
    seller = str(obj_seller) if obj_seller else None
    rating = float(obj_rating) if obj_rating else None
    
    return {
        'product': title,
        'URL': link,
        'price': price,
        'discount_percentage': discount,
        'seller': seller,
        'rating': rating
    }

def create_dataframe(items):
    items_dict = list(map(parse_item, items))
    df = pd.DataFrame(items_dict)
    df.set_index('URL', drop=True, inplace=True)   
    return df

def load_to_database(name:str, df:pd.DataFrame, *args, **kwargs):
    with sqlite3.connect('src/Mercadolibre products.db') as connection:
        try:
            df.to_sql(name, connection, *args, **kwargs)
        except ValueError as e:
            print(f'An error ocurred while adding the table to the database, this is likely because the database already contains that table:\n    {e}')

def create_db():
    with sqlite3.connect('src/Mercadolibre products.db') as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS papeleria(
            URL TEXT PRIMARY KEY,
            product VARCHAR(100),
            price INT,
            discount_percentage INT,
            seller VARCHAR(20),
            rating DECIMAL(2,1)
            );
            """
        )

def main():
    create_db()
    items_html = get_items_mercadolibre(URLs[0])
    df = create_dataframe(items_html)
    load_to_database('stationery_most_relevant', df, if_exists='append')


if __name__ == '__main__':
    main()
