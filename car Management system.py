import mysql.connector
from mysql.connector import Error
from datetime import datetime

class DatabaseManager:
    def __init__(self, host='localhost', database='carmanagement', user='root', password='hb7409hb'):
        try:
            self.connection = mysql.connector.connect(
                 host='localhost',
                user='root',
                password='hb7409hb',  # use the one you just tested
                database='carmanagement',
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
                self.create_tables()
        except Error as e:
            print("Error while connecting to MySQL", e)
            self.connection = None

    def create_tables(self):
        cursor = self.connection.cursor()
        car_table = """
        CREATE TABLE IF NOT EXISTS cars (
            id INT AUTO_INCREMENT PRIMARY KEY,
            make VARCHAR(50) NOT NULL,
            model VARCHAR(50) NOT NULL,
            year INT NOT NULL,
            vin VARCHAR(50) UNIQUE NOT NULL,
            owner VARCHAR(100) NOT NULL,
        );
        """
        booking_table = """
        CREATE TABLE IF NOT EXISTS bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            car_id INT NOT NULL,
            user VARCHAR(100) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            price DECIMAL(10,2),
            FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
        );
        """
        maintenance_table = """
        CREATE TABLE IF NOT EXISTS maintenance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            car_id INT NOT NULL,
            maintenance_date DATE NOT NULL,
            cost DECIMAL(10,2),
            description TEXT,
            FOREIGN KEY (car_id) REFERENCES cars(id) ON DELETE CASCADE
        );
        """
        user_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            role VARCHAR(20) NOT NULL
        );
        """
        for table_sql in [car_table, booking_table, maintenance_table, user_table]:
            cursor.execute(table_sql)
        self.connection.commit()
        cursor.close()

    # Car operations
    def add_car(self, make, model, year, vin, owner):
        try:
            cursor = self.connection.cursor()
            sql = "INSERT INTO cars (make, model, year, vin, owner) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (make, model, year, vin, owner))
            self.connection.commit()
            cursor.close()
            print("Car added successfully.")
        except Error as e:
            print("Failed to add car:", e)

    def get_cars(self):
        cursor = self.connection.cursor (dictionary=True)
        cursor.execute("SELECT * FROM cars")
        cars = cursor.fetchall()
        cursor.close()
        return cars

    def get_car_by_id(self, car_id):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cars WHERE id=%s", (car_id,))
        car = cursor.fetchone()
        cursor.close()
        return car

    # Booking operations
    def is_car_available(self, car_id, start_date, end_date):
        cursor = self.connection.cursor()
        sql = """
        SELECT COUNT(*) FROM bookings
        WHERE car_id = %s AND NOT (end_date < %s OR start_date > %s)
        """
        cursor.execute(sql, (car_id, start_date, end_date))
        (count,) = cursor.fetchone()
        cursor.close()
        return count == 0

    def book_car(self, car_id, user, start_date, end_date, price):
        if not self.is_car_available(car_id, start_date, end_date):
            print("Car is not available for the selected dates.")
            return False
        try:
            cursor = self.connection.cursor()
            sql = "INSERT INTO bookings (car_id, user, start_date, end_date, price) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (car_id, user, start_date, end_date, price))
            self.connection.commit()
            cursor.close()
            print("Booking successful.")
            return True
        except Error as e:
            print("Failed to book car:", e)
            return False

    def get_bookings(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT b.*, c.make, c.model FROM bookings b JOIN cars c ON b.car_id = c.id ORDER BY start_date DESC")
        bookings = cursor.fetchall()
        cursor.close()
        return bookings

    # Maintenance operations
    def add_maintenance(self, car_id, maintenance_date, cost, description):
        try:
            cursor = self.connection.cursor()
            sql = "INSERT INTO maintenance (car_id, maintenance_date, cost, description) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (car_id, maintenance_date, cost, description))
            self.connection.commit()
            cursor.close()
            print("Maintenance record added successfully.")
        except Error as e:
            print("Failed to add maintenance record:", e)

    def get_maintenance_records(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT m.*, c.make, c.model FROM maintenance m JOIN cars c ON m.car_id = c.id ORDER BY maintenance_date DESC")
        records = cursor.fetchall()
        cursor.close()
        return records

    # User operations (basic for now)
    def add_user(self, username, role):
        try:
            cursor = self.connection.cursor()
            sql = "INSERT INTO users (username, role) VALUES (%s, %s)"
            cursor.execute(sql, (username, role))
            self.connection.commit()
            cursor.close()
            print("User added successfully.")
        except Error as e:
            print("Failed to add user:", e)

    def get_users(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        return users

def main_menu():
    print("\nCore Car Management System")
    print("[1] Register a new car")
    print("[2] Book a car")
    print("[3] Track car maintenance")
    print("[4] View cars")
    print("[5] View bookings")
    print("[6] View maintenance records")
    print("[7] Add user")
    print("[8] View users")
    print("[0] Exit")

def main():
    print("Welcome to the Core Car Management System")
    db = DatabaseManager(user='root', password='your_mysql_password_here')
    while True:
        main_menu()
        choice = input("Enter your choice: ").strip()
        if choice == '1':
            make = input("Make: ").strip()
            model = input("Model: ").strip()
            year = input("Year: ").strip()
            vin = input("VIN: ").strip()
            owner = input("Owner Name: ").strip()
            if not (make and model and year.isdigit() and vin and owner):
                print("Invalid input, please try again.")
                continue
            db.add_car(make, model, int(year), vin, owner)

        elif choice == '2':
            cars = db.get_cars()
            if not cars:
                print("No cars available. Please register cars first.")
                continue
            print("Available Cars:")
            for car in cars:
                print(f"{car['id']}: {car['make']} {car['model']} ({car['year']})")
            car_id = input("Enter car ID to book: ").strip()
            if not car_id.isdigit():
                print("Invalid car ID.")
                continue
            car_id = int(car_id)
            car = db.get_car_by_id(car_id)
            if not car:
                print("Car not found.")
                continue
            user = input("User booking the car: ").strip()
            start_date = input("Start date (YYYY-MM-DD): ").strip()
            end_date = input("End date (YYYY-MM-DD): ").strip()
            price_input = input("Price (optional, leave blank if unknown): ").strip()
            price = float(price_input) if price_input else 0.0
            try:
                sd = datetime.strptime(start_date, "%Y-%m-%d").date()
                ed = datetime.strptime(end_date, "%Y-%m-%d").date()
                if ed < sd:
                    print("End date cannot be before start date.")
                    continue
                db.book_car(car_id, user, sd, ed, price)
            except Exception as e:
                print("Invalid date format. Please use YYYY-MM-DD.")

        elif choice == '3':
            cars = db.get_cars()
            if not cars:
                print("No cars available. Please register cars first.")
                continue
            print("Cars:")
            for car in cars:
                print(f"{car['id']}: {car['make']} {car['model']} ({car['year']})")
            car_id = input("Enter car ID for maintenance record: ").strip()
            if not car_id.isdigit():
                print("Invalid car ID.")
                continue
            car_id = int(car_id)
            car = db.get_car_by_id(car_id)
            if not car:
                print("Car not found.")
                continue
            date_str = input("Maintenance date (YYYY-MM-DD): ").strip()
            cost_str = input("Cost: ").strip()
            desc = input("Description: ").strip()
            try:
                maintenance_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                cost = float(cost_str) if cost_str else 0.0
                db.add_maintenance(car_id, maintenance_date, cost, desc)
            except Exception as e:
                print("Invalid input for date or cost.")

        elif choice == '4':
            cars = db.get_cars()
            if not cars:
                print("No cars available.")
            else:
                for car in cars:
                    print(f"ID: {car['id']}, {car['make']} {car['model']} ({car['year']}), VIN: {car['vin']}, Owner: {car['owner']}")

        elif choice == '5':
            bookings = db.get_bookings()
            if not bookings:
                print("No bookings found.")
            else:
                for b in bookings:
                    print(f"Booking ID: {b['id']}, Car: {b['make']} {b['model']}, User: {b['user']}, From: {b['start_date']}, To: {b['end_date']}, Price: ${b['price']}")

        elif choice == '6':
            records = db.get_maintenance_records()
            if not records:
                print("No maintenance records found.")
            else:
                for r in records:
                    print(f"Record ID: {r['id']}, Car: {r['make']} {r['model']}, Date: {r['maintenance_date']}, Cost: ${r['cost']}, Description: {r['description']}")

        elif choice == '7':
            username = input("Enter username: ").strip()
            role = input("Enter role (admin/renter): ").strip()
            if role not in ['admin', 'renter']:
                print("Invalid role. Should be 'admin' or 'renter'.")
                continue
            db.add_user(username, role)

        elif choice == '8':
            users = db.get_users()
            if not users:
                print("No users found.")
            else:
                for user in users:
                    print(f"User ID: {user['id']}, Username: {user['username']}, Role: {user['role']}")

        elif choice == '0':
            print("Exiting system.")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == '__main__':
    main()

