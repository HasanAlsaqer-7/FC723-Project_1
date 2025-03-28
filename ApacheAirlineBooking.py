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


def generate_booking_reference():
    while True:  # Keep generating until A Unique reference is  found
        booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))  

        # Check if this booking reference already exists in the database
        cursor.execute("SELECT COUNT(*) FROM bookings WHERE booking_ref = ?", (booking_ref,))
        if cursor.fetchone()[0] == 0:
            return booking_ref  # It's unique, so it is returned
        
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
            passport_no = input("Enter passport number: ").upper()
            first_name = input("Enter first name: ").capitalize()
            last_name = input("Enter last name: ").capitalize()
            booking_ref = generate_booking_reference()
            cursor.execute("INSERT INTO bookings (booking_ref, passport_no, first_name, last_name, seat) VALUES (?, ?, ?, ?, ?)",
                           (booking_ref, passport_no, first_name, last_name, seat))
            conn.commit()
            print(f"Seat {seat} successfully booked with reference {booking_ref}.")
        else:
            print("Seat is already booked.")
    else:
        print("Invalid seat number or storage area.")

#Function that prompts the user to choose a seat and free it, removing the booking reference and database entry
def free_seat():
    # Prompt user for details to identify the booking
    seat = input("Enter seat number to free (e.g., 1A): ").upper()
    last_name_input = input("Enter your last name: ").strip().capitalize()
    booking_ref_input = input("Enter your booking reference: ").strip().upper()

    # Check if the booking exists in the database with the given seat, last name, and booking reference
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE seat = ? AND last_name = ? AND booking_ref = ?",
                   (seat, last_name_input, booking_ref_input))
    if cursor.fetchone()[0] == 0:
        print("No matching booking found. Cannot free the seat.")
        return

    # Delete the booking from the database
    cursor.execute("DELETE FROM bookings WHERE seat = ? AND last_name = ? AND booking_ref = ?",
                   (seat, last_name_input, booking_ref_input))
    conn.commit()
    print(f"Seat {seat} has been freed successfully.")




#Function that prompts the user to modify a booking by freeing the current seat and booking a new one, also changing the database entry of the booking
def modify_booking():
    #prompt user for current booking details to identify the booking to modify
    current_seat = input("Enter your currently booked seat (e.g., 1A): ").upper()
    last_name_input = input("Enter your last name: ").strip().capitalize()
    booking_ref_input = input("Enter your current booking reference: ").strip().upper()

    # Verify the current booking exists in the database
    cursor.execute("SELECT * FROM bookings WHERE seat = ? AND last_name = ? AND booking_ref = ?",
                   (current_seat, last_name_input, booking_ref_input))
    booking_data = cursor.fetchone()
    if not booking_data:
        print("No matching booking found for the current seat. Cannot modify booking.")
        return

    # ask for the new seat to change the booking
    new_seat = input("Enter the new seat you want to book (e.g., 1B): ").upper()
    # Check if the new seat is available and valid 
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE seat = ?", (new_seat,))
    if cursor.fetchone()[0] > 0:
        print("The new seat is already booked.")
        return
    if new_seat in storage_seats:
        print("The new seat is in a storage area and cannot be booked.")
        return

    # Delete the old booking record
    cursor.execute("DELETE FROM bookings WHERE seat = ? AND last_name = ? AND booking_ref = ?",
                   (current_seat, last_name_input, booking_ref_input))
    conn.commit()
    
    # Generate a new booking reference for the new seat
    new_booking_ref = generate_booking_reference()
    
    # Insert the updated booking record with the old details
    cursor.execute("INSERT INTO bookings (booking_ref, passport_no, first_name, last_name, seat) VALUES (?, ?, ?, ?, ?)",
                   (new_booking_ref, booking_data[1], booking_data[2], booking_data[3], new_seat))
    conn.commit()
    
    print(f"Booking modified: {current_seat} has been freed and {new_seat} is booked with new reference {new_booking_ref}.")

#Function that displays the current booking status of all seats

def show_booking_status():
    last_name_input = input("Enter the last name to get your booking details: ").strip().capitalize()
    
    # Query the database for all booking records
    cursor.execute("SELECT seat, booking_ref, passport_no, first_name, last_name FROM bookings")
    all_bookings_list = cursor.fetchall()
    
    # Filter booking details for the header based on the last name provided
    header_bookings = [record for record in all_bookings_list if record[4].lower() == last_name_input.lower()]
    
    # Print header with booking details for bookings matching the last name
    if header_bookings:
        print(f"Booking Details for last name '{last_name_input}':")
        for record in header_bookings:
            seat, booking_ref, passport_no, first_name, last_name = record
            print(f"Seat: {seat}, Booking Reference: {booking_ref}, Passenger: {first_name} {last_name}, Passport: {passport_no}")
        print("\nSeat Booking Layout:")
    else:
        print(f"No bookings found for last name '{last_name_input}'.\nSeat Booking Layout:")
    
    # Create a dictionary mapping seat to booking reference for the full seating layout based on all booking records from the database.
    bookings = {record[0]: record[1] for record in all_bookings_list}
    
    # width to ensure alignment
    cell_width = 4
    
    # Print the seating layout 
    for i in range(1, 81):  
        row_str = ""
        for col in "ABCXDEF":  
            seat = f"{i}{col}"  
            if col == "X":
                cell = "X "
            elif seat in bookings:
                cell = "R"
            elif seat in storage_seats:
                cell = "S"
            else:
                cell = seat
            row_str += f"{cell:>{cell_width}}"
        print(row_str)

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
