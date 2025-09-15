import sqlite3
from datetime import datetime

DATABASE = "tickets_r_us_final.db"


class Theatre:
    """The theatres are the locations each having their own capacity where you can book to view a movie"""
    def __init__(self, theatre_id, theatre_name, theatre_capacity):
        self._theatre_id = theatre_id
        self._theatre_name = theatre_name
        self._theatre_capacity = theatre_capacity
        self._movies = {}

    # ---- getters ----
    def get_id(self):
        return self._theatre_id

    def get_name(self):
        return self._theatre_name

    def get_capacity(self):
        return self._theatre_capacity

    # ---- movies management ----
    def add_movie(self, movie):
        self._movies[movie.get_id()] = movie

    def has_movie(self, movie_id):
        return movie_id in self._movies

    def get_movie(self, movie_id):
        return self._movies.get(movie_id)

    def iter_movies(self):
        return self._movies.values()

    def get_movie_ids(self):
        return set(self._movies.keys())


class Movie:
    """Movies can be booked in their assigned thatres with each one having a specific price and showtime. 
    The amount of tickets purchased for a movie determines the remaining capacity in the theatre for that movie based on the assigned theatres original capacity"""
    def __init__(self, movie_id, theatre_id, movie_title, ticket_price, show_time, tickets_purchased):
        self._movie_id = movie_id
        self._theatre_id = theatre_id
        self._movie_title = movie_title
        self._ticket_price = ticket_price
        self._show_time = show_time
        self._tickets_purchased = tickets_purchased

    # ---- getters/setters ----
    def get_id(self):
        return self._movie_id

    def get_theatre_id(self):
        return self._theatre_id

    def get_title(self):
        return self._movie_title

    def get_price(self):
        return self._ticket_price

    def set_price(self, new_price: float):
        self._ticket_price = float(new_price)

    def get_show_time(self):
        return self._show_time

    def set_show_time(self, new_time: str):
        self._show_time = new_time

    def get_tickets_purchased(self):
        return self._tickets_purchased

    # ---- business logic ----
    def tickets_available(self, theatre_capacity):
        return theatre_capacity - self._tickets_purchased

    def purchase_tickets(self, quantity, theatre_capacity):
        if quantity < 1 or quantity > self.tickets_available(theatre_capacity):
            raise ValueError("Invalid ticket quantity")
        self._tickets_purchased += quantity

    def cancel_tickets(self, quantity):
        if quantity < 1 or quantity > self._tickets_purchased:
            raise ValueError("Invalid ticket quantity")
        self._tickets_purchased -= quantity


def load_data():
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    cursor.execute("SELECT id, name, capacity FROM theatre")
    all_theatres = {}
    for theatre_id, theatre_name, theatre_capacity in cursor.fetchall():
        all_theatres[theatre_id] = Theatre(theatre_id, theatre_name, theatre_capacity)

    cursor.execute(
        "SELECT id, theatre_id, title, price, show_time, tickets_purchased FROM movie"
    )
    for movie_id, theatre_id, movie_title, ticket_price, show_time, tickets_purchased in cursor.fetchall():
        movie = Movie(movie_id, theatre_id, movie_title, ticket_price, show_time, tickets_purchased)
        if theatre_id in all_theatres:
            all_theatres[theatre_id].add_movie(movie)

    return connection, all_theatres


def list_theatres(theatres):
    for theatre in theatres.values():
        print(f"{theatre.get_id()}: {theatre.get_name()} (capacity {theatre.get_capacity()})")


def list_movies(theatre: Theatre):
    theatre_capacity = theatre.get_capacity()
    for movie in theatre.iter_movies():
        available = movie.tickets_available(theatre_capacity)
        print(
            f"{movie.get_id()}: {movie.get_title()} @ {movie.get_show_time()} | ${movie.get_price():.2f} | available {available}"
        )


def list_sales(connection):
    cursor = connection.execute("SELECT id, movie_id, qty, sale_time, total_price FROM sale")
    for sale_id, movie_id, quantity, sale_time, total_price in cursor.fetchall():
        print(f"{sale_id}: movie {movie_id} qty {quantity} time {sale_time} total ${total_price:.2f}")


def input_int(prompt, valid=None):
    while True:
        try:
            value = int(input(prompt))
            if valid is None or value in valid:
                return value
        except:
            pass


# load database and objects
connection, theatres = load_data()

# main loop
while True:
    print(
        "1) View theatres\n2) View movies by theatre \n3) Purchase tickets \n4) Cancel purchase \n5) Admin: update movie info \n6) Exit"
    )
    menu_choice = input_int(" ")

    if menu_choice == 1:
        list_theatres(theatres)

    elif menu_choice == 2:
        list_theatres(theatres)
        theatre_choice = input_int("Theatre ID: ", set(theatres.keys()))
        list_movies(theatres[theatre_choice])

    elif menu_choice == 3:
        list_theatres(theatres)
        theatre_choice = input_int("Theatre ID: ", set(theatres.keys()))
        selected_theatre = theatres[theatre_choice]
        list_movies(selected_theatre)
        movie_choice = input_int("Movie ID: ", selected_theatre.get_movie_ids())
        selected_movie = selected_theatre.get_movie(movie_choice)
        theatre_capacity = selected_theatre.get_capacity()
        available_tickets = selected_movie.tickets_available(theatre_capacity)
        if available_tickets == 0:
            print("No tickets available.")
            continue
        quantity = input_int(
            f"Quantity (1-{available_tickets}): ",
            set(range(1, available_tickets + 1)),
        )
        try:
            selected_movie.purchase_tickets(quantity, theatre_capacity)
            connection.execute(
                "INSERT INTO sale(movie_id, qty, sale_time, total_price) VALUES (?,?,?,?)",
                (movie_choice, quantity, datetime.now().isoformat(), quantity * selected_movie.get_price()),
            )
            connection.execute(
                "UPDATE movie SET tickets_purchased = ? WHERE id = ?",
                (selected_movie.get_tickets_purchased(), movie_choice),
            )
            connection.commit()
            print("Purchase successful.")
        except ValueError as e:
            print(e)

    elif menu_choice == 4:
        list_sales(connection)
        sale_choice = input_int("Sale ID to cancel: ")
        row = connection.execute(
            "SELECT movie_id, qty FROM sale WHERE id = ?", (sale_choice,)
        ).fetchone()
        if not row:
            print("Sale not found.")
        else:
            movie_id, quantity = row
            selected_movie = None
            for theatre in theatres.values():
                if theatre.has_movie(movie_id):
                    selected_movie = theatre.get_movie(movie_id)
                    break
            if selected_movie is None:
                print("Movie not found.")
                continue
            try:
                selected_movie.cancel_tickets(quantity)
                connection.execute("DELETE FROM sale WHERE id = ?", (sale_choice,))
                connection.execute(
                    "UPDATE movie SET tickets_purchased = ? WHERE id = ?",
                    (selected_movie.get_tickets_purchased(), movie_id),
                )
                connection.commit()
                print("Cancellation successful.")
            except ValueError as e:
                print(e)

    elif menu_choice == 5:
        list_theatres(theatres)
        theatre_choice = input_int("Theatre ID: ", set(theatres.keys()))
        selected_theatre = theatres[theatre_choice]
        list_movies(selected_theatre)
        movie_choice = input_int("Movie ID: ", selected_theatre.get_movie_ids())
        selected_movie = selected_theatre.get_movie(movie_choice)
        new_price = input("New price (blank to skip): ").strip()
        new_time = input("New show time HH:MM (blank to skip): ").strip()
        if new_price:
            selected_movie.set_price(float(new_price))
        if new_time:
            selected_movie.set_show_time(new_time)
        connection.execute(
            "UPDATE movie SET price = ?, show_time = ? WHERE id = ?",
            (selected_movie.get_price(), selected_movie.get_show_time(), movie_choice),
        )
        connection.commit()
        print("Movie updated.")

    else:
        break

connection.close()
