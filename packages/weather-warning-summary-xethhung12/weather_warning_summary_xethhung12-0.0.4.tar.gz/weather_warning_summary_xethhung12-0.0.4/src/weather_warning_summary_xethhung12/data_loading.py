import sqlite3

import requests


def get_connection(bPath: str):
    dbPath = bPath+"/weather-warning.db"
    print(dbPath)
    c = sqlite3.connect(dbPath)
    c.execute("create table if not exists weather (id INTEGER PRIMARY KEY AUTOINCREMENT, time text , message Text)")
    return c


def load_map(url):
    response = requests.request("GET", url)
    return response.content.decode('utf-8')
