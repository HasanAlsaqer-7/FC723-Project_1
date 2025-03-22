# Initial seating data: A dictionary simulating seat status.
seats = {f"{row}{col}": "F" for row in range(1, 81) for col in "ABCDEF"}

# Define storage area seats
storage_seats = {"77D", "77E", "77F", "78D", "78E", "78F"}

# Example booked seats (can be modified dynamically in the program)
booked_seats = {"1A", "5B", "10C", "15D", "20E", "25F"}


def display_menu():
    print("\n--- Apache Airlines Seat Booking ---")
    print("1. Check availability of seat")
    print("2. Book a seat")
    print("3. Free a seat")
    print("4. Show booking status")
    print("5. Modify booking")
    print("6. Exit program")

def check_availability():
    seat = input("Enter seat number to check (e.g., 1A): ").upper()
    if seat in seats:
        if seat in booked_seats:
            print(f"Seat {seat} is Reserved")
        elif seat in storage_seats:
            print(f"Seat {seat} is a Storage Area (Not Bookable)")
        else:
            print(f"Seat {seat} is Available")
    else:
        print("Invalid seat number.")

def book_seat():
    seat = input("Enter seat number to book (e.g., 1A): ").upper()
    if seat in seats and seat not in storage_seats:
        if seat not in booked_seats:
            booked_seats.add(seat)
            print(f"Seat {seat} successfully booked.")
        else:
            print("Seat is already booked.")
    else:
        print("Invalid seat number or storage area.")

def free_seat():
    seat = input("Enter seat number to free (e.g., 1A): ").upper()
    if seat in booked_seats:
        booked_seats.remove(seat)
        print(f"Seat {seat} is now free.")
    else:
        print("Seat is not booked or does not exist.")

def modify_booking():
    current_seat = input("Enter your currently booked seat (e.g., 1A): ").upper()
    if current_seat not in booked_seats:
        print("The specified current seat is not booked.")
        return
    new_seat = input("Enter the new seat you want to book (e.g., 1B): ").upper()
    if new_seat not in seats or new_seat in storage_seats:
        print("Invalid new seat number or storage area.")
        return
    if new_seat in booked_seats:
        print("The new seat is already booked.")
        return
    # Process modification: free the current seat and book the new seat.
    booked_seats.remove(current_seat)
    booked_seats.add(new_seat)
    print(f"Booking updated: {current_seat} freed and {new_seat} booked successfully.")

def show_booking_status():
    for i in range(1, 81):  # Rows 1 to 80
        for j, col in enumerate("ABCXDEF"):  # Columns A-F and aisle X
            seat = f"{i}{col}"  # Seat identifier
            formatted_seat = f" {seat}" if i < 10 else seat  # Add space for alignment
            if col == "X":
                print("X", end="  ")  # Print aisle
            elif seat in booked_seats:
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
