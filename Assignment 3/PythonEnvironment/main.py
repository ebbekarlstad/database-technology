from database import Database
from getpass import getpass
from menu import print_header, print_options, check_choice

class Application:
    def __init__(self, db):
        self.db = db

    def main_menu(self):
        options = ["Member Login", "New Member Registration", "Quit"]
        while True:
            print_header("Welcome to the book store database!")
            print_options(options)
            choice = check_choice(len(options))

            if choice == 1:
                self.member_menu()
            elif choice == 2:
                self.new_member_menu()
            else:
                break

    def member_menu(self):
        print_header("Member Menu")

        user_mail = input("Enter email: ")
        user_pass = input("Enter password: ")

        # Check credentials using the Database method
        if not self.db.member_login(user_mail, user_pass):
            print("Invalid email or password. Try again!")
            return  # Return to the previous menu or exit
        self.userid = self.db.get_member_id(user_mail)

        options = ["Browse by subject", "Search by Author/Title", "Checkout", "Logout"]

        while True:
            print_header("Member Menu")
            print_options(options)
            choice = check_choice(len(options))

            if choice == 1:
                subjects = self.db.fetch_subjects()

                # Print all subjects and save the chosen one
                print("\nAvailable Subjects:")
                for index, subject in enumerate(subjects, start=1):
                    print(f"{index}. {subject[0]}")
                subject_choice = int(input("\nType in your option: "))
                chosen_subject = subjects[subject_choice - 1][0]

                # Print amount books
                amount = self.db.display_amount(chosen_subject)
                print(f"\nThere are {amount} books on this subject")

                # Display books in subject user chose (2 at a time)
                display_books = self.db.display_books(chosen_subject)
                isbn_list = [book[0] for book in display_books]

                for i in range(0, len(display_books), 2):
                    for book in display_books[i:i+2]:
                        print(f"ISBN: {book[0]}\nAuthor: {book[1]}\nTitle: {book[2]}\nPrice: {book[3]}\nSubject: {book[4]}\n")

                    # Ask the user if they want to continue after every two books
                    continue_prompt = input("Press 'n' + ENTER to see more books, ENTER to go back to the menu, or enter an ISBN to add to the cart: ")

                    if continue_prompt == 'n':
                        print()
                        continue
                    elif continue_prompt == '':
                        break  # Use break to exit the loop and return to the main menu.
                    elif continue_prompt in isbn_list:
                        try:
                            qty = int(input("Enter quantity: "))
                            if qty > 0:
                                self.db.add_to_cart(self.userid, continue_prompt, qty)
                                print("Added to cart!\n")
                            else:
                                print("Invalid quantity. Please enter a positive number.")
                        except ValueError:
                            print("Please enter a valid number for the quantity.")

            if choice == 2:
                search_options = ["Search Author", "Search Title", "Back to member menu"]
                print("\nEnter search choice:")

                print_options(search_options)
                
                # Functions for searching starts here
                search_choice = check_choice(len(search_options))

                if search_choice == 1:
                    user_author_search = input("Enter author or part of author: ")
                    author_result = self.db.author_search(user_author_search)
                    isbn_list = [book[0] for book in author_result]

                    for i in range(0, len(author_result), 2):
                        for book in author_result[i:i+2]:
                            print(f"\nISBN: {book[0]}\nAuthor: {book[1]}\nTitle: {book[2]}\nPrice: {book[3]}\nSubject: {book[4]}")
                    
                        continue_prompt = input("Press 'n' + ENTER to see more books, ENTER to go back to the menu, or enter an ISBN to add to the cart: ")
                    
                        if continue_prompt == 'n':
                            print()
                            continue
                        elif continue_prompt == '':
                            break  # Use break to exit the loop and return to the main menu.
                        elif continue_prompt in isbn_list:
                            try:
                                qty = int(input("Enter quantity: "))
                                if qty > 0:
                                    self.db.add_to_cart(self.userid, continue_prompt, qty)
                                    print("Added to cart!\n")
                                else:
                                    print("Invalid quantity. Please enter a positive number.")
                            except ValueError:
                                print("Please enter a valid number for the quantity.")
                
                elif search_choice == 2:
                    user_title_search = input("Enter title or part of title: ")
                    title_result = self.db.title_search(user_title_search)
                    isbn_list = [book[0] for book in title_result]
                    
                    for i in range(0, len(title_result), 2):
                        for book in title_result[i:i+2]:
                            print(f"\nISBN: {book[0]}\nAuthor: {book[1]}\nTitle: {book[2]}\nPrice: {book[3]}\nSubject: {book[4]}")

                        continue_prompt = input("Press 'n' + ENTER to see more books, ENTER to go back to the menu, or enter an ISBN to add to the cart: ")

                        if continue_prompt == 'n':
                            print()
                            continue
                        elif continue_prompt == '':
                            break  # Use break to exit the loop and return to the main menu.
                        elif continue_prompt in isbn_list:
                            try:
                                qty = int(input("Enter quantity: "))
                                if qty > 0:
                                    self.db.add_to_cart(self.userid, continue_prompt, qty)
                                    print("Added to cart!\n")
                                else:
                                    print("Invalid quantity. Please enter a positive number.")
                            except ValueError:
                                print("Please enter a valid number for the quantity.")

            elif choice == 3:  # Checkout option
                cart_items = self.db.get_cart(self.userid)
                if not cart_items:
                    print("Your cart is empty.")
                else:
                    total_price = 0
                    print("Your cart items:")
                    for item in cart_items:
                        isbn, title, qty = item  # Assuming cart stores isbn, title, and qty
                        book_info = self.db.get_book_info(isbn)
                        if book_info:
                            price = book_info['price']
                            print(f"ISBN: {isbn}, Title: {title}, Author: {book_info['author']}, Quantity: {qty}, Price per item: ${price}")
                            total_price += price * qty
                        else:
                            print(f"Error fetching details for ISBN: {isbn}")

                    print(f"Total price: ${total_price}")

                    # Confirm checkout
                    confirm = input("Proceed to checkout? (y/n): ")
                    if confirm.lower() == 'y':
                        # Get shipping details from the user
                        shipAddress = input("Enter shipping address: ")
                        shipCity = input("Enter shipping city: ")
                        shipZip = input("Enter shipping ZIP code: ")

                        # Create the order and get the order ID
                        order_id = self.db.create_order(self.userid, shipAddress, shipCity, shipZip)

                        # Add order details
                        self.db.add_order_details(order_id, cart_items)

                        # Clear the cart after checkout
                        self.db.clear_cart(self.userid)

                        # Display the invoice
                        self.display_invoice(order_id)
                    else:
                        print("Checkout canceled.")



            
            
            elif choice == len(options):  # The last option is to go back or logout
                break
            else:
                print("Option selected is not implemented yet.")

    def display_invoice(self, order_id):
        # Fetch order details
        order_invoice = self.db.get_order_invoice(order_id)

        print("\nInvoice: ")
        print(f"Order Number: {order_id}")
        print(f"Order Date: {order_invoice['order_details'][0][1]}")
        print(f"Shipping Address: {order_invoice['shipping_info'][0]}")
        print(f"Shipping City: {order_invoice['shipping_info'][1]}")
        print(f"Shipping Zip: {order_invoice['shipping_info'][2]}")

        total_cost = 0
        for item in order_invoice['order_details']:
            print(f"Title: {item[2]}, Author: {item[3]}, Quantity: {item[4]}, Price per item: ${item[5]}, Total Price: ${item[6]}")
            total_cost += item[6]

        print(f"Total Order Cost: ${total_cost}")

    def new_member_menu(self):
        print_header("Welcome to the new member registration menu!")
        fname = input("Enter fname: ")
        lname = input("Enter lname: ")
        address = input("Enter address: ")
        city = input("Enter city: ")
        zip = input("Enter zip: ")
        phone = input("Enter phone: ")
        email = input("Enter email: ")
        userPassword = getpass("Enter password: ")

        # Prepare and execute the SQL INSERT statement
        insert_query = """
        INSERT INTO members (fname, lname, address, city, zip, phone, email, password)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        insert_values = (fname, lname, address, city, zip, phone, email, userPassword)
        self.db.execute_with_commit(insert_query, insert_values)

        print("You have registered! Going back to the main menu.")

def check_credentials():
    while True:
        username = input("Enter SQL Server Username: ")
        password = getpass("Enter SQL Server Password: ")
        try:
            db = Database(username, password)
            return db
        except:  # noqa: E722
            print("Connection to SQL Server has failed. Try again.")

def main():
    db = check_credentials()
    app = Application(db)
    app.main_menu()

if __name__ == "__main__":
    main()
