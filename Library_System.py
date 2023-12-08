from datetime import datetime, timedelta
import random
import re
import threading
import time
import pandas as pd

''' This book has several attributes
 that would be part of a library system '''

class Book:
    def __init__(self, title, author, isbn, quantity_available):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.quantity_available = quantity_available
        
''' this class extends the base class and 
add addtional attribute fiction to it as genre'''
class FictionBook(Book):
    def __init__(self, title, author, isbn, quantity_available):
        
        super().__init__(title, author, isbn, quantity_available)
        self.genre = 'Fiction'
''' this class extends the base class and 
add addtional attribute non fiction to it as genre'''
class NonFictionBook(Book):
     def __init__(self, title, author, isbn, quantity_available):
        
        super().__init__(title, author, isbn, quantity_available)
        self.genre = 'Non Fiction'

'''this borrower class has several attributes which would 
   be intialized when obj creation when then added to the file
'''
class Borrower:
    def __init__(self, name, address,unique_id,book_name,book_code):
        self.name = name
        self.address = address
        self.unique_id=unique_id
        self.borrow_book = book_name
        self.book_code=book_code
'''Borrower_Modifier class extends the Borrower class and
   add additional attributes to it like dates using pythom datetime()
 '''
class Borrower_Modifier(Borrower):
    def __init__(self, name, address, unique_id, book_name, book_code):
        super().__init__(name, address, unique_id, book_name, book_code)
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=10)

''' these three are helper function which i used in logging isbn generation 
    and validating the isbn
'''

def validate_isbn(isbn):
    # Defining the  pattern
    pattern = re.compile(r"^786-\d{7}-\d{4}-\d{3}$")
    
    # return true if pattern matches
    return bool(pattern.match(isbn))

def log_timestamp(func):
    # Decorator to log timestamp of book borrowings and returns
    def wrapper(*args, **kwargs):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        result = func(*args, **kwargs)
        with open('logs.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] {func.__name__} executed.\n")
        return result
    return wrapper

def generate_isbn():
        # Generate random numbers for the ISBN components
        prefix = "786"
        seven = str(random.randint(1000000, 9999999))
        four = str(random.randint(1000, 9999))
        three = str(random.randint(100, 999))
        # Formating  the ISBN
        isbn = f"{prefix}-{seven}-{four}-{three}"
        return isbn



class Library:
    
    def __init__(self):
        self.lock=threading.Lock()
    
    def show_books(self):
        # exceptional handling for the file
        try:
            books_df = pd.read_csv('books.csv')
            # Check if books.csv is empty
            if books_df.empty:
                print("No books available in the library.")
                return
        except FileNotFoundError:
            print("File not found")
            return
        result = books_df.loc[:, ['Title', 'ISBN','Quantity_Available']]
        print(result.to_string(index=False))

    
    def add_book(self):
        book_title=input('Enter the book title : ')
        book_author=input('Enter the book author : ')
        book_isbn=generate_isbn()

        try:
            book_quantity=int(input('Enter the quantity of book :'))
        except Exception as e:
            print('Please Enter only integer values')
            return
        
        book_genre=input('Enter the book genre e.g(fiction or non fiction) :')
        if book_genre.lower() =='fiction':
            
            book_obj=FictionBook(book_title,book_author,book_isbn,book_quantity)
            dic={
                'Title':[book_obj.title],'Author':[book_obj.author],
                'ISBN':[book_obj.isbn],'Quantity_Available':[book_obj.quantity_available],
                'Genre':[book_obj.genre]
            }

            book_data=pd.DataFrame(dic)
            book_data.to_csv('books.csv',mode='a',header=False ,index=False)
            print(f"Book has been added : {book_title}")
        elif book_genre.lower() == 'non fiction':
            book_obj=NonFictionBook(book_title,book_author,book_isbn,book_quantity)
            dic={
                    'Title':[book_obj.title],'Author':[book_obj.author],
                    'ISBN':[book_obj.isbn],'Quantity_Available':[book_obj.quantity_available],
                    'Genre':[book_obj.genre]
                }

            book_data=pd.DataFrame(dic)
            book_data.to_csv('books.csv',mode='a',header=False ,index=False)
            print(f"{book_title} : has been added to Library")
        else:
            print('You entered an incorrect Genre')
  

   # this method is used for adding user to the library system 
    def register_user(self):
        print('Welcome to our Library!')

        # Get user name input
        user_name = input('Please enter your name for registration: ')

        # Check if each word in the user_name consists only of characters
        if all(word.isalpha() for word in user_name.split()):
            print(f"Hello, {user_name}!")
            
            # Get user address
            address = input('Enter your address: ')
            # Get and validate CNIC
            try:
                user_id = int(input('Please enter your CNIC without dashes (e.g., 3450295178257): '))
                if len(str(user_id)) != 13:
                    print('Invalid CNIC number. It should be 13 digits.')
                else:
                    # Saving user data to users.csv file
                    try:
                        user_data = pd.DataFrame({
                            'Name': [user_name],
                            'Address': [address],
                            'UniqueID': [user_id]
                        })
                        # mode was a
                        user_data.to_csv('users.csv', mode='a',header=False ,index=False)
                        print(f"User : {user_id} has been added to the system")
                    except Exception as e:
                        print(e)
            
            except ValueError:
                print('Invalid input. Please enter a valid numerical CNIC.')
        else:
            print("Invalid name. Please enter only characters.")
    
    @log_timestamp
    def borrow_book(self):
        # using threading lock function to lock the resources
        with self.lock:
            # exceptional handling for file
            try:
                books_df = pd.read_csv('books.csv')
                # Check if books.csv is empty
                if books_df.empty:
                    print("No books available in the library.")
                    return
            except FileNotFoundError:
                print("file not found.")
                return

            try:
                user_id=int(input('Enter your Unique ID :'))
            except ValueError:
                print(' Error : ID is 13 digit unique (e.g : 3450214953585) digits only')
                return
            
            user_df=pd.read_csv('users.csv')
            if (user_id) in user_df['UniqueID'].values:
                user_info = user_df.loc[user_df['UniqueID'] == user_id, ['Name', 'Address']].iloc[0]
                user_name = user_info['Name']
                user_address = user_info['Address']
                print(f'welcome {user_name} ! ')
                isbn_input=input('Enter book ISBN (e.g 786-1234567-4567-789 ) \n')
                isbn_checker=validate_isbn(isbn_input)
                if isbn_checker:           
                    book_df=pd.read_csv('books.csv')
                    if isbn_input in book_df['ISBN'].values:
                        book_info = book_df.loc[book_df['ISBN'] == isbn_input, ['Title', 'Quantity_Available']].iloc[0]
                        book_name = book_info['Title']
                        quantity_available = book_info['Quantity_Available']

                        if int(quantity_available) > 0:
                            print(f"The book is '{book_name}' and quantity Available: {quantity_available}")
                            choice_input=input('Do you want it to borrow ? y | n : \n')
                            if choice_input=='y':
                                borrower_obj=Borrower_Modifier(user_name,user_address,user_id,book_name,isbn_input)
                                dic={
                                        'Borrower Name':[borrower_obj.name],
                                        'Borrower Adress':[borrower_obj.address],
                                        'Unique Id':[borrower_obj.unique_id],
                                        'Book code':[borrower_obj.book_code],
                                        'Book Name':[borrower_obj.borrow_book],
                                        'Borrow date':[borrower_obj.start_date],
                                        'End Borrow date':[borrower_obj.end_date],
                                    }

                                borrows_data=pd.DataFrame(dic)
                                borrows_data.to_csv('borrowers.csv',mode='a',header=False ,index=False)
                                print(f"{borrower_obj.borrow_book} has been borrowed by {borrower_obj.name}")
                                # update the record
                                
                                book_df['Quantity_Available'] = book_df['Quantity_Available'].astype(int)
                                book_df.loc[book_df['ISBN'] == str(isbn_input), 'Quantity_Available'] -= 1
                                book_df.to_csv('books.csv',  index=False)
                                print('Record Updated ')

                            else:
                                print('happy reading !')

                        else:
                            print(f"The book with ISBN {isbn_input} is '{book_name}', but it is out of Stock.")
                    else:
                        print(f"No book found with ISBN {isbn_input}")
                else :
                    print('You Entered an Incorrect ISBN !')
            else :
                print('Incorrect ID or user dose not exist !')
    
    @log_timestamp
    def return_book(self):
        with self.lock:
            isbn_input = input('Enter book ISBN (e.g., 786-1234567-4567-789): ')
            isbn_checker = validate_isbn(isbn_input)

            if isbn_checker:
                borrower_df = pd.read_csv('borrowers.csv')

                # Check if the book has been borrowed
                if isbn_input in borrower_df['Book code'].values:
                    # Count the number of copies borrowed
                    copies_borrowed = borrower_df[borrower_df['Book code'] == isbn_input].shape[0]

                    # Update borrowers.csv by removing entries with the specified ISBN
                    borrower_df = borrower_df[borrower_df['Book code'] != isbn_input]
                    borrower_df.to_csv('borrowers.csv', index=False)
                    print(f"Book with ISBN {isbn_input} have been returned.")

                    # Update books.csv (assuming you have a valid ISBN in books.csv)
                    books_df = pd.read_csv('books.csv')
                    book_index = books_df.index[books_df['ISBN'] == isbn_input].tolist()
                    if book_index:
                        # Increment the quantity by the count of copies borrowed
                        books_df.at[book_index[0], 'Quantity_Available'] += copies_borrowed
                        books_df.to_csv('books.csv', index=False)
                        print(f'Book quantity updated.')
                else:
                    print(f"The book with ISBN {isbn_input} is not currently borrowed.")
            else:
                print('You entered an incorrect ISBN!')
    
    # this method is for showing borrowers info
    def show_borrowers(self):
        # doing exceptional handling for file
        try:
            borrower_df = pd.read_csv('borrowers.csv')
            # Check if file is empty
            if borrower_df.empty:
                print("There are Currently no borrowers")
                return
        except FileNotFoundError:
            print("File not found")
            return
        result = borrower_df.loc[:, ['Borrower Name', 'Borrower Adress','Book Name']]
        print(result.to_string(index=False))
    def calculate_average(self):
        try:
            # Reading the file
            borrower_df = pd.read_csv('borrowers.csv')    
            # Check if the file is empty
            if borrower_df.empty:
                print("No borrowers found.")
                return 
            # Group by 'Unique Id' and calculate the count of books borrowed
            borrower_grouped = borrower_df.groupby('Unique Id')['Book code'].count()
            # Calculate the average by mean function
            average_books = borrower_grouped.mean()
            print(f"Average quantity of books borrowed per borrower: {average_books:.2f}")
        except FileNotFoundError:
            print("File not found.")
            return 

# end of library class
 
''' this concurency_handling function is for threading purpose when
    borrow book method is called is locks the resources to avoid the 
    race conditions, similar for book return method
'''
def concurency_handling(obj, operation):
    if operation == 'borrow':
        borrow_thread = threading.Thread(target=obj.borrow_book)
        borrow_thread.start()
        borrow_thread.join()
    elif operation == 'return':
        return_thread = threading.Thread(target=obj.return_book)
        return_thread.start()
        return_thread.join()
    else:
        print("Invalid operation")  
   
                    
                    
            
# Function to display the menu and get user input
def display_menu():
    print('***************************************\n')
    print('Welcome to Library Management System\n')
    print("Enter 1. To Display all the books")
    print('Enter 2. To add the books')
    print("Enter 3. To Borrow a book")
    print("Enter 4. To return a book")
    print("Enter 5. To register yourself")
    print("Enter 6. To Display borrowers")
    print("Enter 7. To Display Average of books Borrowed ")
    print("Enter 8. To Quit")

    
lib=Library()

while True:
    display_menu()
    try:
        opt = int(input(''))

        if opt == 1:
            lib.show_books()

        elif opt == 2:
            lib.add_book()

        elif opt == 3:
            # lib.borrow_book()
            concurency_handling(lib,'borrow')

        elif opt == 4:
            concurency_handling(lib,'return')

        elif opt == 5:
            lib.register_user()
        
        elif opt ==6:
            lib.show_borrowers()
        
        elif opt ==7:
            lib.calculate_average()

        elif opt == 8:
            print('Thank you for using the System .....')
            break  # Exit the while loop

        else:
            print('Invalid choice! ', opt, 'Please try again')
    except Exception as e:
        print('Please enter a Valid choice')
