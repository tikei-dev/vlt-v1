from abc import ABC, abstractmethod
import csv
from datetime import datetime
import random

# Abstract Base Class for tickets
class Ticket(ABC):
    def __init__(self, ticket_id, date, setnumber=None):
        self.ticket_id = ticket_id
        self.date = datetime.strptime(date, "%Y-%m-%d")  # Store date as a datetime object
        self.setnumber = setnumber or [''] * 6  # Default to a list of 6 empty strings if not provided

    @abstractmethod
    def get_info(self):
        pass

    @abstractmethod
    def to_csv_row(self):
        pass

    @classmethod
    @abstractmethod
    def from_csv_row(cls, row):
        pass


# Concrete Implementation for Auto Ticket
class AutoTicket(Ticket):
    def __init__(self, ticket_id, date, product, setnumber=None):
        super().__init__(ticket_id, date, setnumber)
        self.product = product

    def get_info(self):
        setnumber_str = ", ".join(self.setnumber)
        return (
            f"Auto Ticket [ID: {self.ticket_id}, "
            f"Date: {self.date.strftime('%Y-%m-%d')}, product: {self.product}, setnumber: {setnumber_str}]"
        )

    def to_csv_row(self):
        return [
            self.ticket_id,
            "Auto",
            self.date.strftime("%Y-%m-%d"),
            self.product,
            ", ".join(self.setnumber),  # Convert list to comma-separated string
        ]

    @classmethod
    def from_csv_row(cls, row):
        ticket_id, _, date_str, product, setnumber_str = row
        setnumber = setnumber_str.split(", ")  # Convert comma-separated string back to list
        if len(setnumber) != 6:
            raise ValueError("setnumber must have exactly 6 elements")
        return cls(ticket_id, date_str, product, setnumber)


# Ticket Manager Class
class TicketManager:
    def __init__(self):
        self.product = []
        self.next_id = 1  # Start the ticket ID counter from 1

    def add_ticket(self, ticket):
        if isinstance(ticket, Ticket):
            self.product.append(ticket)
            self.update_next_id()
        else:
            raise ValueError("Invalid ticket type")

    def update_next_id(self):
        # Find the highest ticket ID and set next_id to the next number
        max_id = max((int(t.ticket_id) for t in self.product), default=0)
        self.next_id = max_id + 1

    def create_auto_ticket(self, date=None, product=None, setnumber=None, min_value=1, max_value=45):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        if product is None:
            product = "Unknown"
        
        if setnumber is None:
            setnumber = [str(random.randint(min_value, max_value)) for _ in range(6)]
        
        if len(setnumber) != 6:
            raise ValueError("setnumber must have exactly 6 elements")

        ticket_id = str(self.next_id)
        Auto_ticket = AutoTicket(ticket_id, date, product, setnumber)
        self.add_ticket(Auto_ticket)
        print("Auto Ticket added.")

    def list_product(self):
        for ticket in self.product:
            print(ticket.get_info())

    def save_to_csv(self, filename):
        try:
            with open(filename, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    ["Ticket ID", "Type", "Date", "Product", "Setnumber"]
                )
                for ticket in self.product:
                    writer.writerow(ticket.to_csv_row())
            print(f"Product saved to {filename}.")
        except IOError as e:
            print(f"Failed to save product: {e}")

    def load_from_csv(self, filename):
        self.product = []
        try:
            with open(filename, "r") as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    ticket_type = row[1]

                    if ticket_type == "Auto":
                        ticket = AutoTicket.from_csv_row(row)
                    else:
                        continue
                    self.product.append(ticket)
            self.update_next_id()  # Update the ID counter based on loaded product
        except IOError as e:
            print(f"Failed to load product: {e}")

    def search_ticket_by_id(self, ticket_id):
        # Search for a ticket by its ID
        for ticket in self.product:
            if ticket.ticket_id == ticket_id:
                return ticket
        print("Ticket not found.")
        return None


# Functions for Menu Options
def add_Auto_ticket(manager):
    try:
        date = input("Enter Date (YYYY-MM-DD) or press Enter for today's date: ").strip()
        if date == "":
            date = None  # Use today's date
        product = input("Enter product: ").strip() or None
        
        setnumber_input = input("Enter setnumber (6 comma-separated values or press Enter to generate random numbers): ").strip()
        if setnumber_input:
            setnumber = [val.strip() for val in setnumber_input.split(",")]
            if len(setnumber) != 6:
                raise ValueError("You must enter exactly 6 values for setnumber.")
        else:
            min_value = int(input("Enter minimum value for random setnumber: ").strip())
            max_value = int(input("Enter maximum value for random setnumber: ").strip())
            manager.create_auto_ticket(date, product, setnumber=None, min_value=min_value, max_value=max_value)
            return
        
        manager.create_auto_ticket(date, product, setnumber)
    except ValueError as e:
        print(f"Error: {e}")

def list_all_product(manager):
    print("Listing all products:")
    manager.list_product()

def save_product_to_csv(manager):
    # filename = input("Enter filename to save product (e.g., product.csv): ").strip()
    filename = "product.csv"
    manager.save_to_csv(filename)

def search_ticket_by_id(manager):
    ticket_id = input("Enter the ticket ID to search: ").strip()
    ticket = manager.search_ticket_by_id(ticket_id)
    if ticket:
        print(ticket.get_info())

def exit_program():
    print("Exiting...")
    exit()

# Main Menu Function
def main_menu():
    manager = TicketManager()

    # Optionally load existing product from a file
    filename = "product.csv"
    manager.load_from_csv(filename)

    # Directly list all products when the application starts
    print("\nListing all products:")
    manager.list_product()

    menu_options = {
        "1": lambda: add_Auto_ticket(manager),
        "2": lambda: list_all_product(manager),
        "3": lambda: save_product_to_csv(manager),
        "4": lambda: search_ticket_by_id(manager),
        "5": exit_program,
    }

    while True:
        print("\nTicket Manager Menu")
        print("1. Add Auto Ticket")
        print("2. List All products")
        print("3. Save products to CSV")
        print("4. Search Ticket by ID")
        print("5. Exit")
        choice = input("Enter your choice: ").strip()

        action = menu_options.get(choice)
        if action:
            action()
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main_menu()
