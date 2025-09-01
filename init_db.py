import sqlite3
from pathlib import Path
import random
import string

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'app.db'

def create_schema(conn):
    sql_commands = """
    DROP TABLE IF EXISTS users;
    DROP TABLE IF EXISTS vehicles;
    DROP TABLE IF EXISTS payments;
    DROP TABLE IF EXISTS ownership_transfers;

    CREATE TABLE users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('citizen', 'officer'))
    );

    CREATE TABLE vehicles (
        vehicle_id TEXT PRIMARY KEY,
        owner_cnic TEXT NOT NULL,
        number_plate TEXT,
        number_plate_applied INTEGER DEFAULT 0,
        number_plate_approved INTEGER DEFAULT 0,
        number_plate_receipt_id TEXT,
        number_plate_dispatch_status TEXT DEFAULT 'pending'
    );

    CREATE TABLE payments (
        receipt_id TEXT PRIMARY KEY,
        citizen_name TEXT NOT NULL,
        cnic TEXT NOT NULL,
        asset_id TEXT NOT NULL,
        amount INTEGER NOT NULL,
        payment_timestamp INTEGER NOT NULL
    );

    CREATE TABLE ownership_transfers (
        transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT NOT NULL,
        old_owner_cnic TEXT NOT NULL,
        new_owner_cnic TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('requested', 'approved')),
        receipt_id TEXT,
        dispatch_status TEXT DEFAULT 'pending'
    );
    """
    conn.executescript(sql_commands)

def random_string(length=32):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def insert_sample_data(conn):
    # Insert 2 users
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('citizen1', 'password123', 'citizen'))
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('officer1', 'password123', 'officer'))

    owner_cnic_prefix = "12345-1234567-"
    citizen_names = ["Ali", "Sara", "Ahmed", "Nida", "Saad", "Fatima", "Hassan", "Ayesha", "Bilal", "Zara"]

    for i in range(1, 51):
        vehicle_id = f"veh{i:03d}"
        owner_cnic = owner_cnic_prefix + str(random.randint(10, 99))

        conn.execute("INSERT INTO vehicles(vehicle_id, owner_cnic) VALUES (?, ?)", (vehicle_id, owner_cnic))

        for _ in range(random.randint(1, 2)):
            receipt_id = random_string()
            citizen_name = random.choice(citizen_names)
            amount = random.choice([1000, 1500, 2000, 2500, 3000])
            payment_timestamp = 1685000000 + random.randint(0, 10000000)  # example UNIX timestamp
            conn.execute("""
            INSERT INTO payments(receipt_id, citizen_name, cnic, asset_id, amount, payment_timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (receipt_id, citizen_name, owner_cnic, vehicle_id, amount, payment_timestamp))

        # Insert ownership transfer on every 10th vehicle
        if i % 10 == 0:
            transfer_receipt_id = random_string()
            new_owner_cnic = owner_cnic_prefix + str(random.randint(20, 99))
            conn.execute("""
            INSERT INTO ownership_transfers(vehicle_id, old_owner_cnic, new_owner_cnic, status, receipt_id, dispatch_status)
            VALUES (?, ?, ?, 'requested', ?, 'pending')
            """, (vehicle_id, owner_cnic, new_owner_cnic, transfer_receipt_id))

    conn.commit()

if __name__ == '__main__':
    with sqlite3.connect(DB_PATH) as conn:
        print("Creating schema...")
        create_schema(conn)
        print("Inserting sample data...")
        insert_sample_data(conn)
        print("DB setup complete!")
