import sqlite3
from datetime import datetime

DATABASE = "tickets_r_us_final.db"


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

    def get_title(self):
        return self.title


def load_data():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.execute("SELECT id, name, capacity FROM theatre")
    theatres = {}
    for tid, name, cap in cur.fetchall():
        theatres[tid] = Theatre(tid, name, cap)

    cur.execute(
        "SELECT id, theatre_id, title, price, show_time, tickets_purchased FROM movie"
    )
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
        print(
            f"{m.id}: {m.get_title()} @ {m.show_time} | ${m.price:.2f} | available {avail}"
        )


def list_sales(conn):
    cur = conn.execute("SELECT id, movie_id, qty, sale_time, total_price FROM sale")
    for sid, mid, qty, stime, total in cur.fetchall():
        print(f"{sid}: movie {mid} qty {qty} time {stime} total ${total:.2f}")


def input_int(prompt, valid=None):
    while True:
        try:
            v = int(input(prompt))
            if valid is None or v in valid:
                return v
        except:
            pass


# load database and objects
conn, theatres = load_data()

# main loop
while True:
    print(
        "1) View theatres\n2) View movies by theatre \n3) Purchase tickets \n4) Cancel purchase \n5) Admin: update movie info \n6) Exit"
    )
    choice = input_int(" ")

    if choice == 1:
        list_theatres(theatres)

    elif choice == 2:
        list_theatres(theatres)
        tid = input_int("Theatre ID: ", theatres)
        list_movies(theatres[tid])

    elif choice == 3:
        list_theatres(theatres)
        tid = input_int("Theatre ID: ", theatres)
        th = theatres[tid]
        list_movies(th)
        mid = input_int("Movie ID: ", th.movies)
        m = th.movies[mid]
        if
        qty = input_int(
            f"Quantity (1-{m.available(th.capacity)}): ",
            set(range(1, m.available(th.capacity) + 1)),
        )
        try:
            m.purchase(qty, th.capacity)
            conn.execute(
                "INSERT INTO sale(movie_id, qty, sale_time, total_price) VALUES (?,?,?,?)",
                (mid, qty, datetime.now().isoformat(), qty * m.price),
            )
            conn.execute(
                "UPDATE movie SET tickets_purchased = ? WHERE id = ?",
                (m.tickets_purchased, mid),
            )
            conn.commit()
            print("Purchase successful.")
        except ValueError as e:
            print(e)

    elif choice == 4:
        list_sales(conn)
        sid = input_int("Sale ID to cancel: ")
        row = conn.execute(
            "SELECT movie_id, qty FROM sale WHERE id = ?", (sid,)
        ).fetchone()
        if not row:
            print("Sale not found.")
        else:
            mid, qty = row
            for th in theatres.values():
                if mid in th.movies:
                    m = th.movies[mid]
                    break
            try:
                m.cancel(qty)
                conn.execute("DELETE FROM sale WHERE id = ?", (sid,))
                conn.execute(
                    "UPDATE movie SET tickets_purchased = ? WHERE id = ?",
                    (m.tickets_purchased, mid),
                )
                conn.commit()
                print("Cancellation successful.")
            except ValueError as e:
                print(e)

    elif choice == 5:
        list_theatres(theatres)
        tid = input_int("Theatre ID: ", theatres)
        th = theatres[tid]
        list_movies(th)
        mid = input_int("Movie ID: ", th.movies)
        m = th.movies[mid]
        new_price = input("New price (blank to skip): ").strip()
        new_time = input("New show time HH:MM (blank to skip): ").strip()
        if new_price:
            m.price = float(new_price)
        if new_time:
            m.show_time = new_time
        conn.execute(
            "UPDATE movie SET price = ?, show_time = ? WHERE id = ?",
            (m.price, m.show_time, mid),
        )
        conn.commit()
        print("Movie updated.")

    else:
        break

conn.close()
