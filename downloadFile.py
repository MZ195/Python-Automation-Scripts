from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import json
import time

if __name__ == "__main__":
    base_url = "https://horriblesubs.info/shows/"
    watch_list = [
        "yahari-ore-no-seishun-love-come-wa-machigatteiru-kan", "one-piece"]

    url = base_url + watch_list[0]
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    inp = urlopen(req)
    soup = BeautifulSoup(inp.read(), 'html.parser')
    print(soup)
    # print(soup.find('div', class_="hs-shows"))
