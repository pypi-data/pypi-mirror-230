import sqlite3

import requests


def get_connection(bPath: str):
    c = sqlite3.connect(bPath+"/weather-warning.db")
    c.execute("create table if not exists weather (id INTEGER PRIMARY KEY AUTOINCREMENT, time text , message Text)")
    return c


def load_map(url):
    response = requests.request("GET", url)
    return response.content.decode('utf-8')
