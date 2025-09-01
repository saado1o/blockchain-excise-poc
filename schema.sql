DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS payments;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('citizen', 'officer'))
);

CREATE TABLE payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  receipt_id TEXT UNIQUE NOT NULL,
  citizen_name TEXT NOT NULL,
  cnic TEXT,
  asset_id TEXT NOT NULL,
  amount INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT UNIQUE NOT NULL,
    owner_cnic TEXT NOT NULL,
    number_plate TEXT,
    number_plate_applied INTEGER DEFAULT 0,   -- 0=false,1=true
    number_plate_approved INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ownership_transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id TEXT NOT NULL,
    old_owner_cnic TEXT NOT NULL,
    new_owner_cnic TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('requested', 'approved', 'rejected')) DEFAULT 'requested'
);

-- Drop existing tables if desired
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS ownership_transfers;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('citizen', 'officer'))
);

CREATE TABLE payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  receipt_id TEXT UNIQUE NOT NULL,
  citizen_name TEXT NOT NULL,
  cnic TEXT,
  asset_id TEXT NOT NULL,
  amount INTEGER NOT NULL
);

CREATE TABLE vehicles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  vehicle_id TEXT UNIQUE NOT NULL,
  owner_cnic TEXT NOT NULL,
  number_plate TEXT,
  number_plate_applied INTEGER DEFAULT 0,
  number_plate_approved INTEGER DEFAULT 0
);

CREATE TABLE ownership_transfers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  vehicle_id TEXT NOT NULL,
  old_owner_cnic TEXT NOT NULL,
  new_owner_cnic TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('requested', 'approved', 'rejected')) DEFAULT 'requested'
);

-- Existing tables ...

ALTER TABLE ownership_transfers
ADD COLUMN receipt_id TEXT;

ALTER TABLE ownership_transfers
ADD COLUMN dispatch_status TEXT DEFAULT 'pending';

ALTER TABLE vehicles
ADD COLUMN number_plate_receipt_id TEXT;

ALTER TABLE vehicles
ADD COLUMN number_plate_dispatch_status TEXT DEFAULT 'pending';
