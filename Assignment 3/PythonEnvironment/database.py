from mysql.connector import connect
import datetime

class Database:
    # Establish connection to DB in MySQL Server
    def __init__(self, username, password) -> None:
        self.connection = connect(host="localhost", user=username, password=password, database="book_store")

    # Get cursor
    def __get_cursor__(self):
        # Correctly return a new cursor instance with buffering
        return self.connection.cursor(buffered=True)
    
    # Execute and fetch all results
    def execute_with_fetchall(self, query, params=None):
        with self.__get_cursor__() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
        
    # Execute with commit
    def execute_with_commit(self, query, params=None):
        with self.__get_cursor__() as cursor:
            cursor.execute(query, params)
            self.connection.commit()

    # get subjects
    def fetch_subjects(self):
        subject_query = "SELECT DISTINCT(subject) FROM books;"
        with self.connection.cursor() as cursor:
            cursor.execute(subject_query)
            return cursor.fetchall()
    
    def display_amount(self, subject):
        amount_books_query = "SELECT COUNT(*) FROM books WHERE subject = %s;"
        with self.connection.cursor() as cursor:
            cursor.execute(amount_books_query, (subject,))
            result = cursor.fetchone()
            return result[0] if result else 0

    def display_books(self, subject):
        book_display_query = "SELECT * FROM books WHERE subject = %s;"
        with self.connection.cursor() as cursor:
            cursor.execute(book_display_query, (subject,))
            return cursor.fetchall()
        
    def add_to_cart(self, userid, isbn, qty):
        add_query = "INSERT INTO cart (userid, isbn, qty) VALUES (%s, %s, %s);"
        with self.connection.cursor() as cursor:
            cursor.execute(add_query, (userid, isbn, qty))
            self.connection.commit()

    def get_cart(self, userid):
        cart_query = """
        SELECT c.isbn, b.title, c.qty FROM cart c
        JOIN books b ON c.isbn = b.isbn
        WHERE c.userid = %s;
        """
        with self.connection.cursor() as cursor:
            cursor.execute(cart_query, (userid,))
            return cursor.fetchall()

    def get_member_id(self, user_email):
        id_query = "SELECT userid FROM members WHERE email = %s;"
        with self.connection.cursor() as cursor:
            cursor.execute(id_query, (user_email,))
            result = cursor.fetchone()
            return result[0] if result else None

    def member_login(self, user_email, user_pass):
        login_query = "SELECT COUNT(*) FROM members WHERE email = %s AND password = %s;"
        with self.connection.cursor() as cursor:
            cursor.execute(login_query, (user_email, user_pass))
            result = cursor.fetchone()
            return result[0] == 1
    
    def author_search(self, user_author_search):
        # Format the user input to include wildcards for LIKE query
        user_input_formatted = "%" + user_author_search + "%"
        author_query = "SELECT * FROM books WHERE author LIKE %s;"
        with self.connection.cursor() as cursor:
            cursor.execute(author_query, (user_input_formatted,))
            return cursor.fetchall()
    
    def title_search(self, user_title_search):
        # Format the user input to include wildcards for LIKE query
        user_input_formatted = "%" + user_title_search + "%"
        title_query = "SELECT * FROM books WHERE title LIKE %s;"
        with self.connection.cursor() as cursor:
            cursor.execute(title_query, (user_input_formatted,))
            return cursor.fetchall()
    
    def get_book_info(self, isbn):
        book_query = "SELECT isbn, title, author, price FROM books WHERE isbn = %s;"
        with self.connection.cursor() as cursor:
            cursor.execute(book_query, (isbn,))
            result = cursor.fetchone()
            if result:
                book_info = {
                    'isbn': result[0],
                    'author': result[1],
                    'title': result[2],
                    'price': result[3]
                }
                return book_info
            else:
                return None
            
    def clear_cart(self, userid):
        clear_query = "DELETE FROM cart WHERE userid = %s;"
        with self.connection.cursor() as cursor:
            cursor.execute(clear_query, (userid,))
            self.connection.commit()

    def create_order(self, user_id, shipAddress, shipCity, shipZip):
        # Get today's date in the format that MySQL expects (YYYY-MM-DD).
        today_date = datetime.date.today().isoformat()

        # Make the SQL INSERT statement.
        order_query = """
        INSERT INTO orders (userid, created, shipAddress, shipCity, shipZip)
        VALUES (%s, %s, %s, %s, %s);
        """
        order_values = (user_id, today_date, shipAddress, shipCity, shipZip)
        
        # Execute the query with commit to insert the data into the orders table.
        with self.connection.cursor() as cursor:
            cursor.execute(order_query, order_values)
            self.connection.commit()
        
        # Retrieve the last inserted id to reference the created order.
        order_id = cursor.lastrowid
        return order_id
    
    def get_order_invoice(self, order_id):
        # Query to fetch order details and related book information
        invoice_query = """
        SELECT o.ono, o.created, b.title, b.author, d.qty, b.price, (d.qty * b.price) AS total_item_price
        FROM orders o
        JOIN odetails d ON o.ono = d.ono
        JOIN books b ON d.isbn = b.isbn
        WHERE o.ono = %s;
        """
        with self.connection.cursor() as cursor:
            cursor.execute(invoice_query, (order_id,))
            order_details = cursor.fetchall()

        # Fetch the shipping address information
        shipping_query = """
        SELECT shipAddress, shipCity, shipZip
        FROM orders
        WHERE ono = %s;
        """
        with self.connection.cursor() as cursor:
            cursor.execute(shipping_query, (order_id,))
            shipping_info = cursor.fetchone()

        # Combine order details with shipping information
        invoice_data = {
            'order_details': order_details,
            'shipping_info': shipping_info
        }
        return invoice_data
    
    def add_order_details(self, order_id, cart_items):
        detail_query = """
        INSERT INTO odetails (ono, isbn, qty, amount)
        VALUES (%s, %s, %s, %s);
        """
        with self.connection.cursor() as cursor:
            for item in cart_items:
                isbn, qty = item[0], item[2]  # Assuming cart_items is a list of tuples (isbn, title, qty)
                book_info = self.get_book_info(isbn)  # Fetch the book info to get the price
                if book_info:
                    amount = book_info['price'] * qty  # Calculate the total amount for the item
                    cursor.execute(detail_query, (order_id, isbn, qty, amount))
                else:
                    raise ValueError(f"Book info for ISBN {isbn} could not be fetched.")
            self.connection.commit()
