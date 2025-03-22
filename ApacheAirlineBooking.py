import random
import string
import sqlite3

# Initialize SQLite database
conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

# Create bookings table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        booking_ref TEXT PRIMARY KEY,
        passport_no TEXT,
        first_name TEXT,
        last_name TEXT,
        seat TEXT UNIQUE
    )
''')
conn.commit()

# Initial seating data: A dictionary simulating seat status.
seats = {f"{row}{col}": "F" for row in range(1, 81) for col in "ABCDEF"}

# Define storage area seats
storage_seats = {"77D", "77E", "77F", "78D", "78E", "78F"}

# Dictionary to store booked seats along with their booking references
booked_seats = {}

# Global set to keep track of all generated booking references.
existing_refs = set()

def generate_booking_reference():
    """
    Generate a unique 8-character alphanumeric booking reference.
    """
    while True:
        ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if ref not in existing_refs:
            existing_refs.add(ref)
            return ref

def display_menu():
    print("\n--- Apache Airlines Seat Booking ---")
    print("1. Check availability of seat")
    print("2. Book a seat")
    print("3. Free a seat")
    print("4. Show booking status")
    print("5. Modify booking")
    print("6. Exit program")
    
    
   
#Function that prompts the user to choose a seat and check its availability
def check_availability():
    seat = input("Enter seat number to check (e.g., 1A): ").upper()
    if seat in seats:
        cursor.execute("SELECT booking_ref FROM bookings WHERE seat = ?", (seat,))
        result = cursor.fetchone()
        if result:
            print(f"Seat {seat} is Reserved with reference {result[0]}")
        elif seat in storage_seats:
            print(f"Seat {seat} is a Storage Area (Not Bookable)")
        else:
            print(f"Seat {seat} is Available")
    else:
        print("Invalid seat number.")

#Function that prompts the user to choose a seat and book it, generating a booking reference and a database entry
def book_seat():
    seat = input("Enter seat number to book (e.g., 1A): ").upper()
    if seat in seats and seat not in storage_seats:
        cursor.execute("SELECT * FROM bookings WHERE seat = ?", (seat,))
        if cursor.fetchone() is None:
            passport_no = input("Enter passport number: ")
            first_name = input("Enter first name: ")
            last_name = input("Enter last name: ")
            booking_ref = generate_booking_reference()
            cursor.execute("INSERT INTO bookings (booking_ref, passport_no, first_name, last_name, seat) VALUES (?, ?, ?, ?, ?)",
                           (booking_ref, passport_no, first_name, last_name, seat))
            conn.commit()
            booked_seats[seat] = booking_ref
            print(f"Seat {seat} successfully booked with reference {booking_ref}.")
        else:
            print("Seat is already booked.")
    else:
        print("Invalid seat number or storage area.")

#Function that prompts the user to choose a seat and free it, removing the booking reference and database entry
def free_seat():
    seat = input("Enter seat number to free (e.g., 1A): ").upper()
    cursor.execute("DELETE FROM bookings WHERE seat = ?", (seat,))
    conn.commit()
    if seat in booked_seats:
        del booked_seats[seat]
        print(f"Seat {seat} is now free.")
    else:
        print("Seat is not booked or does not exist.")

#Function that prompts the user to modify a booking by freeing the current seat and booking a new one, also changing the database entry of the booking
def modify_booking():
    current_seat = input("Enter your currently booked seat (e.g., 1A): ").upper()
    cursor.execute("SELECT * FROM bookings WHERE seat = ?", (current_seat,))
    booking_data = cursor.fetchone()
    if not booking_data:
        print("The specified current seat is not booked.")
        return
    new_seat = input("Enter the new seat you want to book (e.g., 1B): ").upper()
    cursor.execute("SELECT * FROM bookings WHERE seat = ?", (new_seat,))
    if cursor.fetchone():
        print("The new seat is already booked.")
        return
    cursor.execute("DELETE FROM bookings WHERE seat = ?", (current_seat,))
    conn.commit()
    booking_ref = generate_booking_reference()
    cursor.execute("INSERT INTO bookings (booking_ref, passport_no, first_name, last_name, seat) VALUES (?, ?, ?, ?, ?)",
                   (booking_ref, booking_data[1], booking_data[2], booking_data[3], new_seat))
    conn.commit()
    booked_seats[new_seat] = booking_ref
    print(f"Booking updated: {current_seat} freed and {new_seat} booked with new reference {booking_ref}.")

#Function that displays the current booking status of all seats

def show_booking_status():
    cursor.execute("SELECT seat, booking_ref FROM bookings")
    bookings = dict(cursor.fetchall())
    for i in range(1, 81):  # Rows 1 to 80
        for j, col in enumerate("ABCXDEF"):  # Columns A-F and aisle X
            seat = f"{i}{col}"  # Seat identifier
            formatted_seat = f" {seat}" if i < 10 else seat  # Add space for alignment
            if col == "X":
                print("X", end="  ")  # Print aisle
            elif seat in bookings:
                print("R", end="  ")  # Print booked seats
            elif seat in storage_seats:
                print("S", end="  ")  # Print storage area
            else:
                print(formatted_seat, end="  ")  # Print available seat with spacing fix
        print()  # New line after each row

# Main loop
while True:
    display_menu()
    choice = input("Select an option (1-6): ")
    if choice == "1":
        check_availability()
    elif choice == "2":
        book_seat()
    elif choice == "3":
        free_seat()
    elif choice == "4":
        show_booking_status()
    elif choice == "5":
        modify_booking()
    elif choice == "6":
        print("Exiting program. Goodbye!")
        break
    else:
        print("Invalid choice. Please select a valid option.")
