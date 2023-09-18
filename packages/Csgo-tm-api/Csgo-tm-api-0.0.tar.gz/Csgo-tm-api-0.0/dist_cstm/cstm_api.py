import requests


class CsgotmApi:

    def __init__(self, token):
        self.base_url = 'https://market.csgo.com/api/v2/'
        self.token = token

    def get_auto_price(self, param):
        response = requests.get(f'{self.base_url}prices/orders/RUB.json').json()
        for i in response['items']:
            if i['market_hash_name'] == param:
                price = i['price']*0.95
                answer = (f"Цена автопродажи ({i['market_hash_name']}): {int(price*1.05)} RUB\n\nС учетом комиссии:"
                          f"\nКарта: {int(price*0.97-50)} RUB\nQiwi: {int(price*0.9)} RUB\n")
                return answer

    def get_inventory(self):
        response = requests.get(f'{self.base_url}my-inventory/?key={self.token}').json()
        items = []
        for i in response['items']:
            items.append(i['market_hash_name'])
        return items

    def check_sum(self, items: dict)-> str:
        response = requests.get(f'{self.base_url}prices/orders/RUB.json').json()
        price = 0
        for i in response['items']:
            for param in items:
                if i['market_hash_name'] == param:
                    price += i['price']

        return f'Карта: {int(price*0.97-50)} QIWI: {int(price*0.9)}'
