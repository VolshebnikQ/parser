import requests
import time
import os
import pandas as pd

from random import randint
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from threading import Thread
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
from fp.fp import FreeProxy

class Dragon():
    # API получения своего IP
    mirror_place = 'http://checkip.dyndns.org'

    def __init__(self):
        #Количество одновременных подключений
        self.DRAGON_FRIENDS = 10
        self.DRAGONS_ACTIVE = 0
        #Заголовки запросов
        self.LEGEND = {'User-Agent': ''}
        #Время
        self.TIME_PURCHASE = 10
        # PROXY
        self.OUTFITS = []
        self.PLACES_TREASURES = pd.read_csv('habr.csv')
        self.CURRENT_OUTFIT = {}

    # Сгенирировать заголовок user_agent
    def invent_legends(self):
        self.LEGEND['User-Agent'] = generate_user_agent()

    # Посмотреть на свой IP
    def how_do_I_look(self):
        get_up_and_follow_desire = requests.Session()
        #get_up_and_follow_desire.proxies = {"http": proxy, "https": proxy}

        find_mirror = get_up_and_follow_desire.get(self.mirror_place).content
        mirror = BeautifulSoup(find_mirror, 'html.parser')

        return mirror.find('body').text.split(' ')[3]  # type: ignore

    # Записать proxy в файла
    def arrange_outfits_hangers(self):
        dataframe = pd.DataFrame(self.OUTFITS)
        dataframe.to_csv('proxies.csv', header=None, index=None, sep=',')  # type: ignore

    # Получить proxy из файла
    def what_outfits_there_are(self):
        dataframe = pd.read_csv('proxies.csv', header=None)

        self.OUTFITS = dataframe[0].tolist()

    # Получить бесплатные proxy
    def find_disguise_outfits(self, wardrobe_limit: int):
        count_outfits = len(self.OUTFITS)
        lets_go = self.DRAGON_FRIENDS

        def went_to_store():
            self.OUTFITS.append(FreeProxy(rand=True, elite=True).get())
            self.DRAGONS_ACTIVE -= 1

        errors = 0
        sleep_time = 0

        while count_outfits < wardrobe_limit:
            count_outfits = len(self.OUTFITS)

            if wardrobe_limit - count_outfits < self.DRAGON_FRIENDS:
                lets_go = wardrobe_limit - count_outfits

            if errors >= 10:
                break
            try:
                for i in range(lets_go):
                    dragon_friend = Thread(target=went_to_store)
                    self.DRAGONS_ACTIVE += 1
                    dragon_friend.start()

                while self.DRAGONS_ACTIVE >= self.DRAGON_FRIENDS and sleep_time != 5:
                    time.sleep(0.1)
                    sleep_time += 0.1

                sleep_time = 0
            except Exception as e:
                errors += 1

    # Записать уже обработанную строку
    def remember_empty_treasury(self, index: int):
        f = open('last_index.txt','w')
        f.write(str(index))
        f.close()

    def where_robbery_stop(self):
        last_treasury = 0
        try:
            f = open('last_index.txt','r')
            last_treasury = f.read()
            f.close()
        except:
            pass

        if last_treasury == '':
            last_treasury = 0

        return int(last_treasury)

    # Спарсить всё необходимое
    def find_treasures(self):
        self.find_disguise_outfits(1000)

        def find_disguise():
            self.OUTFITS.append(FreeProxy(rand=True, elite=True, \
                                timeout = self.TIME_PURCHASE).get())

        # Запись в файл
        def hide_loot(url: str, index: int, soup: BeautifulSoup):
            if not os.path.isdir("data"):
                os.mkdir("data")

            self.remember_empty_treasury(index)
            name = soup.find('div', {'class': 'user-page-sidebar__title'}).h1.get_text(strip=True)  # type: ignore
            html = str(soup)
            
            f = open(f'data/{index}-{name}.txt','w')
            f.write(url+'\n')
            f.write(name+'\n')
            f.write(html+'\n')

            f.close()
            print(name)
            self.DRAGONS_ACTIVE -= 1

        # Отправить запрос для парсинга
        def fly_to_treasure(url: str, index: int, recursion = 0):
            unconquered_land = url
            try:
                if self.CURRENT_OUTFIT == '':
                    count_OUTFITS = len(self.OUTFITS)
                    if count_OUTFITS <= 0:
                        find_disguise()
                    num_in_outfits = randint(0, count_OUTFITS - 1)
                    self.CURRENT_OUTFIT = self.OUTFITS[num_in_outfits]

                outfit = self.CURRENT_OUTFIT
                to_treasure = requests.Session()
                to_treasure.proxies = {'http': outfit, 'https': outfit}  # type: ignore

                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                to_treasure.mount('http://', adapter)
                to_treasure.mount('https://', adapter)

                self.invent_legends()

                result = to_treasure.get(unconquered_land, headers=self.LEGEND, timeout=self.TIME_PURCHASE)
                if result.status_code != 200:
                    self.CURRENT_OUTFIT = ''
                    self.OUTFITS.pop(num_in_outfits)  # type: ignore
                    raise
                looted = result.content
                soup = BeautifulSoup(looted, 'html.parser')

                hide_loot(url, index, soup)
            except:
                if recursion < 10:
                    fly_to_treasure(unconquered_land, index, recursion+1)

        last_treasury = self.where_robbery_stop()
        sleep_time = 0

        for index, row in self.PLACES_TREASURES[last_treasury:20].iterrows():
            unconquered_land = row['url']

            self.DRAGONS_ACTIVE += 1
            dragon_friend = Thread(target=fly_to_treasure, args=(unconquered_land, index))
            dragon_friend.start()

            while self.DRAGONS_ACTIVE >= self.DRAGON_FRIENDS:
                time.sleep(0.1)
                sleep_time += 0.1
                if sleep_time >= 1:
                    break
            sleep_time = 0

def main():
    Green_Dragon = Dragon()

    Green_Dragon.find_treasures()

if __name__ == '__main__':
    main()
