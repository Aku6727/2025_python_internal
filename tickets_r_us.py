import sqlite3
from datetime import datetime

DATABASE = r"C:\Github\2025_python_internal\tickets_r_us_final.db"



class Theatre:
    """The theatres are the locations each having their own capacity where you can book to view a movie"""
    def __init__(self, theatre_id, theatre_name, theatre_capacity):
        self._theatre_id = theatre_id
        self._theatre_name = theatre_name
        self._theatre_capacity = theatre_capacity
        self._movies = {}

    # ---- getters ----
    def get_id(self):
        """Get the id of the theatre"""
        return self._theatre_id

    def get_name(self):
        """Get the name of the theatre"""
        return self._theatre_name

    def get_capacity(self):
        """Get the capacity of the theatre"""
        return self._theatre_capacity

    # ---- movies management ----
    def add_movie(self, movie):
        """Add a movie to the theatre"""
        self._movies[movie.get_id()] = movie

    def has_movie(self, movie_id):
        """Check if the theatre has a movie by id"""
        return movie_id in self._movies

    def get_movie(self, movie_id):
        """Get a movie by id"""
        return self._movies.get(movie_id)

    def iter_movies(self):
        """Iterate over all movies in the theatre"""
        return self._movies.values()

    def get_movie_ids(self):
        """Get a list of all movie ids in the theatre"""
        return list(self._movies.keys())


class Movie:
    """Movies can be booked in their assigned theatres with each one having a specific price and showtime. 
    The amount of tickets purchased for a movie determines the remaining capacity in the theatre for that movie based on the assigned theatre's original capacity"""
    def __init__(self, movie_id, theatre_id, movie_title, ticket_price, show_time, tickets_purchased):
        self._movie_id = movie_id
        self._theatre_id = theatre_id
        self._movie_title = movie_title
        self._ticket_price = ticket_price
        self._show_time = show_time
        self._tickets_purchased = tickets_purchased

    # ---- getters/setters ----
    def get_id(self):
        """Get the id of the movie"""
        return self._movie_id

    def get_theatre_id(self):
        """Get the id of the theatre the movie is assigned to"""
        return self._theatre_id

    def get_title(self):
        """Get the title of the movie"""
        return self._movie_title

    def get_price(self):
        """Get the price of the movie ticket"""
        return self._ticket_price

    def set_price(self, new_price: float):
        """Set a new price for the movie ticket"""
        self._ticket_price = float(new_price)

    def get_show_time(self):
        """Get the show time of the movie"""
        return self._show_time

    def set_show_time(self, new_time: str):
        """Set a new show time for the movie"""
        self._show_time = new_time

    def get_tickets_purchased(self):
        """Get the number of tickets purchased for the movie"""
        return self._tickets_purchased

    # ---- business logic ----
    def tickets_available(self, theatre_capacity):
        """Get the number of tickets available for the movie based on the theatre capacity"""
        return theatre_capacity - self._tickets_purchased

    def purchase_tickets(self, quantity, theatre_capacity):
        """Purchase a number of tickets for the movie if available"""
        if quantity < 1 or quantity > self.tickets_available(theatre_capacity):
            raise ValueError("Invalid ticket quantity")
        self._tickets_purchased += quantity

    def cancel_tickets(self, quantity):
        """Cancel a number of tickets for the movie if previously purchased"""
        if quantity < 1 or quantity > self._tickets_purchased:
            raise ValueError("Invalid ticket quantity")
        self._tickets_purchased -= quantity

# Non-class functions
def load_data():
    """Load data from the database and return a connection and a dictionary of theatres"""
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()
    # load theatres
    cursor.execute("SELECT id, name, capacity FROM theatre")
    theatres = {}
    for theatre_id, theatre_name, theatre_capacity in cursor.fetchall():
        theatres[theatre_id] = Theatre(theatre_id, theatre_name, theatre_capacity)
    # load movies
    cursor.execute(
        "SELECT id, theatre_id, title, price, show_time, tickets_purchased FROM movie"
    )
    for movie_id, theatre_id, movie_title, ticket_price, show_time, tickets_purchased in cursor.fetchall():
        movie = Movie(movie_id, theatre_id, movie_title, ticket_price, show_time, tickets_purchased)
        if theatre_id in theatres:
            theatres[theatre_id].add_movie(movie)

    return connection, theatres


def list_theatres(theatres):
    """Display all theatres and their capacity"""
    print("="*50)
    # display theatres with all their details
    for theatre in theatres.values():    
        print(f"{theatre.get_id()}: {theatre.get_name()} (capacity {theatre.get_capacity()})")
    print("="*50)


def list_movies(theatre: Theatre):
    """Display all movies for a given theatre"""
    print("="*50)
    theatre_capacity = theatre.get_capacity()
    # display movies with all their details
    for movie in theatre.iter_movies():
        available = movie.tickets_available(theatre_capacity)
        print(
            f"{movie.get_id()}: {movie.get_title()} @ {movie.get_show_time()} | ${movie.get_price():.2f} | available {available}"
        )
    print("="*50)


def list_sales(connection):
    """Display all sales made"""
    print("="*50)
    cursor = connection.execute("SELECT id, movie_id, qty, sale_time, total_price FROM sale")
    # display sales with all their details
    for sale_id, movie_id, quantity, sale_time, total_price in cursor.fetchall():
        print(f"{sale_id}: movie {movie_id} qty {quantity} time {sale_time} total ${total_price:.2f}")
    print("="*50)


def input_int(prompt, valid=None):
    """Ask for an integer input and keep retrying until valid"""
    while True:
        try:
            # strip whitespace and convert to int
            value = int(input(prompt).strip())
            # check if valid
            if valid is None or value in valid:
                return value
            else:
                # create a string of valid parameters for the user
                valid_parameter = ""
                for i in range (len(valid)):
                    validi = str(valid[i]) + ", "
                    valid_parameter = valid_parameter + validi
                if len(valid)>5:
                    print(f"Please enter one of: {valid[0]} - {valid[len(valid)-1]}")
                else:
                    print(f"Please enter one of: {valid_parameter}")
        except ValueError:
            # catch non-integer inputs
            print("Please enter a valid number.")

def is_valid_time(time_str: str):
    """Check if string is a valid 24h time in HH:MM format."""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

# load database and objects
connection, theatres = load_data()

# main loop
while True:
    # Print the menu options
    print(
        "1) View theatres\n2) View movies by theatre \n3) Purchase tickets \n4) Cancel purchase \n5) Admin: update movie info \n6) Exit"
    )
    # Get user menu choice
    menu_choice = input_int("")
    # Handle menu choices

    # View theatres if user choice = 1
    if menu_choice == 1:
        list_theatres(theatres)

    # View movies by theatre if user choice = 2
    elif menu_choice == 2:
        list_theatres(theatres)
        # ask for theatre id until valid
        theatre_id = input_int("Theatre ID: ", list(theatres.keys()))
        theatre = theatres[theatre_id]
        # list the movies for the selected theatre
        list_movies(theatre)

    # Purchase tickets if user choice = 3
    elif menu_choice == 3:
        # ask for theatre id until valid
        list_theatres(theatres)
        theatre_id = input_int("Theatre ID: ", list(theatres.keys()))
        theatre = theatres[theatre_id]
        # list the movies for the selected theatre
        list_movies(theatre)
        # ask for movie id until valid
        movie_id = input_int("Movie ID: ", theatre.get_movie_ids())
        # get the movie object
        movie = theatre.get_movie(movie_id)
        # ask for quantity until valid
        theatre_capacity = theatre.get_capacity()
        available_tickets = movie.tickets_available(theatre_capacity)
        # if no tickets available, skip to next iteration of main loop
        if available_tickets == 0:
            print("No tickets available.")
            continue
        # ask for quantity until valid
        quantity = input_int(
            f"Quantity (1-{available_tickets}): ",
            list(range(1, available_tickets + 1)),
        )
        # try to purchase tickets and update database
        try:
            # Update the object in memory
            movie.purchase_tickets(quantity, theatre_capacity)
            # Update the database to record the sale
            connection.execute(
                "INSERT INTO sale(movie_id, qty, sale_time, total_price) VALUES (?,?,?,?)",
                (movie_id, quantity, datetime.now().isoformat(), quantity * movie.get_price()),
            )
            # Update the database to reflect the tickets purchased
            connection.execute(
                "UPDATE movie SET tickets_purchased = ? WHERE id = ?",
                (movie.get_tickets_purchased(), movie_id),
            )
            # Commit the changes
            connection.commit()
            # Print success message
            print("Purchase successful.")
            print("="*50)
        # catch invalid quantity error
        except ValueError as e:
            print(e)

    # Cancel purchase if user choice = 4
    elif menu_choice == 4:
        # list all sales
        list_sales(connection)
        # if no sales, skip to next iteration of main loop
        if len(connection.execute("SELECT id FROM sale").fetchall()) == 0:
            print("No sales to cancel.")
            continue
        # ask for sale id until valid
        sale_id = input_int("Sale ID to cancel: ")
        row = connection.execute(
            "SELECT movie_id, qty FROM sale WHERE id = ?", (sale_id,)
        ).fetchone()
        if not row:
            print("Sale not found.")
        else:
            movie_id, quantity = row
            movie = None
            for theatre in theatres.values():
                if theatre.has_movie(movie_id):
                    movie = theatre.get_movie(movie_id)
                    break
            if movie is None:
                print("Movie not found.")
                continue
            try:
                # Update the object in memory
                movie.cancel_tickets(quantity)

                # Delete the sale record
                connection.execute("DELETE FROM sale WHERE id = ?", (sale_id,))

                # Update the database to refund the tickets
                connection.execute(
                    "UPDATE movie SET tickets_purchased = ? WHERE id = ?",
                    (movie.get_tickets_purchased(), movie_id),
                )
                # Commit the changes
                connection.commit()
                # Print success message
                print("Cancellation successful.")
                print(f"Tickets refunded. Available tickets: {movie.tickets_available(theatre.get_capacity())}")
            # catch invalid quantity error
            except ValueError as e:
                print(e)

    # Admin: update movie info if user choice = 5
    elif menu_choice == 5:
        # ask for theatre id until valid
        list_theatres(theatres)
        # ask for theatre id until valid
        theatre_id = input_int("Theatre ID: ", list(theatres.keys()))
        theatre = theatres[theatre_id]
        # list the movies for the selected theatre
        list_movies(theatre)
        movie_id = input_int("Movie ID: ", theatre.get_movie_ids())
        movie = theatre.get_movie(movie_id)  
        # ask for new price and/or new show time
        new_values_ask = True
        while new_values_ask == True:
            # ask for new price and/or new show time
            new_price = input("New price (blank to skip): ").strip()
            new_time = input("New show time HH:MM (blank to skip): ").strip()
            # if both blank, skip to next iteration of main loop
            if new_price == "" and new_time == "":
                print("No changes made.")
                new_values_ask = False
            else:
                # validate and set new values
                if new_price != "":
                    # validate price
                    try:
                        new_price_float = float(new_price)
                        if new_price_float < 0:
                            print("Price must be non-negative.")
                            continue
                        movie.set_price(new_price_float)
                    except ValueError:
                        print("Invalid price format.")
                        continue
                # validate time
                if new_time != "":
                    # validate time
                    if not is_valid_time(new_time):
                        print("Invalid time format. Please use HH:MM in 24-hour format.")
                        continue
                    movie.set_show_time(new_time)
                new_values_ask = False 
    
        # update the database
        connection.execute(
            "UPDATE movie SET price = ?, show_time = ? WHERE id = ?",
            (movie.get_price(), movie.get_show_time(), movie_id),
        )
        # commit the changes
        connection.commit()
        print("Movie updated.")

    # Exit if user choice = 6
    elif menu_choice == 6:
        print("Exiting...")
        break
    
    # Handle invalid menu choice
    else:
        pass

connection.close()
