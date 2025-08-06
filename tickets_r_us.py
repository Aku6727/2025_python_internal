import sqlite3
from datetime import datetime

DATABASE = "tickets_r_us_final.db"
connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

class Theatre:
    def __init__(self, id, name, capacity):
        self.id = id
        self.name = name
        self.capacity = capacity
        self.movies = {}

class Movie:
    def __init__(self, id, theatre_id, title, price, show_time, tickets_purchased):
        self.id = id
        self.theatre_id = theatre_id
        self.title = title
        self.price = price
        self.show_time = show_time
        self.tickets_purchased = tickets_purchased

    def available(self, capacity):
        return capacity - self.tickets_purchased

    def purchase(self, qty, capacity):
        if qty < 1 or qty > self.available(capacity):
            raise ValueError("invalid quantity")
        self.tickets_purchased += qty

    def cancel(self, qty):
        if qty < 1 or qty > self.tickets_purchased:
            raise ValueError("invalid quantity")
        self.tickets_purchased -= qty

def load_data():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.execute("SELECT id, name, capacity FROM theatre")
    theatres = {}
    for tid, name, cap in cur.fetchall():
        theatres[tid] = Theatre(tid, name, cap)

    cur.execute("SELECT id, theatre_id, title, price, show_time, tickets_purchased FROM movie")
    for mid, tid, title, price, show_time, purchased in cur.fetchall():
        m = Movie(mid, tid, title, price, show_time, purchased)
        if tid in theatres:
            theatres[tid].movies[mid] = m

    return conn, theatres

def list_theatres(theatres):
    for t in theatres.values():
        print(f"{t.id}: {t.name} (capacity {t.capacity})")

def list_movies(theatre):
    for m in theatre.movies.values():
        avail = m.available(theatre.capacity)
        print(f"{m.id}: {m.title} @ {m.show_time} | ${m.price:.2f} | available {avail}")

def list_sales(conn):
    cur = conn.execute("SELECT id, movie_id, qty, sale_time, total_price FROM sale")
    for sid, mid, qty, stime, total in cur.fetchall():
        print(f"{sid}: movie {mid} qty {qty} time {stime} total ${total:.2f}")

