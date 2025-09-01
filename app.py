import os
import json
import sqlite3
import uuid
from flask import Flask, request, jsonify, redirect, session, g, render_template
from functools import wraps
from web3 import Web3
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'replace_with_a_real_secret_key'

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / 'app.db'

contract_path = BASE_DIR.parent / 'contracts' / 'ExciseTax.json'
with open(contract_path, 'r') as f:
    contract_json = json.load(f)
contract_abi = contract_json['abi']

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
if not w3.is_connected():
    raise RuntimeError("Cannot connect to Ethereum node")
w3.eth.default_account = w3.eth.accounts[0]

contract_address = "0x5c9162Ab30d6c8ae6a0fA74818176C369A65c108"
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') != role:
                return "Unauthorized", 403
            return f(*args, **kwargs)
        return decorated
    return wrapper

@app.route('/')
def index():
    if 'username' in session:
        if session['role'] == 'citizen':
            return redirect('/citizen')
        if session['role'] == 'officer':
            return redirect('/officer')
    return redirect('/login')

from flask import send_from_directory
import os

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect('/citizen' if user['role'] == 'citizen' else '/officer')
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/citizen')
@login_required
@role_required('citizen')
def citizen():
    return render_template('citizen.html')

@app.route('/officer')
@login_required
@role_required('officer')
def officer():
    return render_template('officer.html')

@app.route('/verify')
def verify():
    return render_template('verify.html')

# --- New Endpoint for verifying vehicle tax payment and number plate status ---

@app.route('/api/verify_vehicle/<string:cnic_or_vehicle_id>', methods=['GET'])
def verify_vehicle(cnic_or_vehicle_id):
    db = get_db()
    payments = db.execute("""
        SELECT receipt_id, amount,
            datetime(payment_timestamp, 'unixepoch', 'localtime') as payment_date
        FROM payments
        WHERE cnic = ? OR asset_id = ?
    """, (cnic_or_vehicle_id, cnic_or_vehicle_id)).fetchall()

    vehicle = db.execute("""
        SELECT vehicle_id, number_plate, owner_cnic FROM vehicles
        WHERE vehicle_id = ? OR owner_cnic = ?
    """, (cnic_or_vehicle_id, cnic_or_vehicle_id)).fetchone()

    payments_list = [
        {"receiptId": p["receipt_id"], "amount": p["amount"], "paymentDate": p["payment_date"]}
        for p in payments
    ]

    result = {
        "payments": payments_list,
        "vehicle": {
            "vehicleId": vehicle["vehicle_id"] if vehicle else None,
            "numberPlate": vehicle["number_plate"] if vehicle else None,
            "ownerCNIC": vehicle["owner_cnic"] if vehicle else None
        }
    }
    return jsonify(result)

# --- Existing endpoints with modification to add receipt and tracking ---

@app.route('/api/request_ownership_transfer', methods=['POST'])
@login_required
@role_required('citizen')
def request_ownership_transfer():
    data = request.json
    receipt_id = str(uuid.uuid4())
    try:
        tx_hash = contract.functions.requestOwnershipTransfer(data['vehicleId'], data['newOwnerCNIC']).transact()
        w3.eth.wait_for_transaction_receipt(tx_hash)
        db = get_db()
        db.execute("""
            INSERT INTO ownership_transfers (vehicle_id, old_owner_cnic, new_owner_cnic, status, receipt_id)
            VALUES (?, ?, ?, 'requested', ?)
        """, (data['vehicleId'], session.get('username'), data['newOwnerCNIC'], receipt_id))
        db.commit()
        return jsonify({'tx_hash': tx_hash.hex(), 'receiptId': receipt_id, 'status': 'Ownership Transfer Requested'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/apply_number_plate', methods=['POST'])
@login_required
@role_required('citizen')
def apply_number_plate():
    data = request.json
    receipt_id = str(uuid.uuid4())
    try:
        tx_hash = contract.functions.applyNumberPlate(data['vehicleId']).transact()
        w3.eth.wait_for_transaction_receipt(tx_hash)
        db = get_db()
        db.execute("""
            UPDATE vehicles
            SET number_plate_applied = 1,
                number_plate_approved = 0,
                number_plate_receipt_id = ?,
                number_plate_dispatch_status = 'pending'
            WHERE vehicle_id = ?
        """, (receipt_id, data['vehicleId']))
        db.commit()
        return jsonify({'tx_hash': tx_hash.hex(), 'receiptId': receipt_id, 'status': 'Number Plate Application Submitted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# --- New API endpoints to track dispatch status and update ---

@app.route('/api/track_receipt/<string:receipt_id>', methods=['GET'])
@login_required
def track_receipt(receipt_id):
    db = get_db()
    # Try finding receipt in ownership transfers
    transfer = db.execute("""
        SELECT vehicle_id, status, dispatch_status
        FROM ownership_transfers WHERE receipt_id = ?
    """, (receipt_id,)).fetchone()

    if transfer:
        return jsonify({
            "type": "ownership_transfer",
            "vehicleId": transfer["vehicle_id"],
            "status": transfer["status"],
            "dispatchStatus": transfer["dispatch_status"]
        })

    # Check in number plate applications
    plate = db.execute("""
        SELECT vehicle_id, number_plate_approved, number_plate_dispatch_status
        FROM vehicles WHERE number_plate_receipt_id = ?
    """, (receipt_id,)).fetchone()

    if plate:
        return jsonify({
            "type": "number_plate_application",
            "vehicleId": plate["vehicle_id"],
            "approved": plate["number_plate_approved"],
            "dispatchStatus": plate["number_plate_dispatch_status"]
        })

    return jsonify({"error": "Receipt not found"}), 404

@app.route('/api/pay_tax', methods=['POST'])
@login_required
@role_required('citizen')
def pay_tax():
    data = request.json
    try:
        tx_hash = contract.functions.payTax(data['citizenName'], data['cnic'], data['assetId'], int(data['amount'])).transact()
        w3.eth.wait_for_transaction_receipt(tx_hash)
        db = get_db()
        db.execute(
            "INSERT INTO payments (receipt_id, citizen_name, cnic, asset_id, amount, payment_timestamp) VALUES (?, ?, ?, ?, ?, strftime('%s', 'now'))",
            (tx_hash.hex(), data['citizenName'], data['cnic'], data['assetId'], int(data['amount']))
        )
        db.commit()
        return jsonify({'receiptId': tx_hash.hex(), 'status': 'Success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/register_vehicle', methods=['POST'])
@login_required
@role_required('citizen')
def register_vehicle():
    data = request.json
    try:
        tx_hash = contract.functions.registerVehicle(data['ownerCNIC'], data['vehicleId']).transact()
        w3.eth.wait_for_transaction_receipt(tx_hash)
        db = get_db()
        db.execute("INSERT OR IGNORE INTO vehicles (vehicle_id, owner_cnic) VALUES (?, ?)", (data['vehicleId'], data['ownerCNIC']))
        db.commit()
        return jsonify({'tx_hash': tx_hash.hex(), 'status': 'Vehicle Registered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/payments', methods=['GET'])
@login_required
@role_required('officer')
def get_payments():
    db = get_db()
    rows = db.execute("SELECT receipt_id, citizen_name, asset_id, amount FROM payments").fetchall()
    payments = [{'receiptId': r['receipt_id'], 'citizenName': r['citizen_name'], 'assetId': r['asset_id'], 'amount': r['amount']} for r in rows]
    return jsonify(payments)


@app.route('/api/approve_ownership_transfer', methods=['POST'])
@login_required
@role_required('officer')
def approve_ownership_transfer():
    data = request.json
    vehicle_id = data.get('vehicleId')
    if not vehicle_id:
        return jsonify({"error": "vehicleId required"}), 400

    db = get_db()
    try:
        # Update ownership_transfers status to approved for the requested transfer of the vehicle
        db.execute("""
            UPDATE ownership_transfers
            SET status = 'approved'
            WHERE vehicle_id = ? AND status = 'requested'
        """, (vehicle_id,))
        db.commit()
        return jsonify({"status": "Ownership transfer approved for vehicle " + vehicle_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/approve_number_plate', methods=['POST'])
@login_required
@role_required('officer')
def approve_number_plate():
    data = request.json
    vehicle_id = data.get('vehicleId')
    if not vehicle_id:
        return jsonify({"error": "vehicleId required"}), 400

    db = get_db()
    try:
        db.execute("""
            UPDATE vehicles
            SET number_plate_approved = 1
            WHERE vehicle_id = ? AND number_plate_applied = 1 AND number_plate_approved = 0
        """, (vehicle_id,))
        db.commit()
        return jsonify({"status": f"Number plate approved for vehicle {vehicle_id}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pending_numberplates', methods=['GET'])
@login_required
@role_required('officer')
def pending_numberplates():
    db = get_db()
    rows = db.execute("SELECT vehicle_id, owner_cnic FROM vehicles WHERE number_plate_applied = 1 AND number_plate_approved = 0").fetchall()
    applications = [{'vehicleId': r['vehicle_id'], 'ownerCNIC': r['owner_cnic']} for r in rows]
    return jsonify(applications)

@app.route('/api/pending_ownershiptransfers', methods=['GET'])
@login_required
@role_required('officer')
def pending_ownershiptransfers():
    db = get_db()
    rows = db.execute("SELECT vehicle_id, old_owner_cnic, new_owner_cnic FROM ownership_transfers WHERE status = 'requested'").fetchall()
    transfers = [{'vehicleId': r['vehicle_id'], 'oldOwnerCNIC': r['old_owner_cnic'], 'newOwnerCNIC': r['new_owner_cnic']} for r in rows]
    return jsonify(transfers)


@app.route('/api/update_dispatch_status', methods=['POST'])
@login_required
@role_required('officer')
def update_dispatch_status():
    data = request.json
    receipt_id = data.get('receiptId')
    new_status = data.get('dispatchStatus')  # 'pending', 'dispatched', 'received'

    db = get_db()

    # Try update ownership_transfers table
    updated = db.execute("""
        UPDATE ownership_transfers
        SET dispatch_status = ?
        WHERE receipt_id = ?
    """, (new_status, receipt_id)).rowcount

    # If not found in ownership_transfers, update vehicles table
    if updated == 0:
        updated = db.execute("""
            UPDATE vehicles
            SET number_plate_dispatch_status = ?
            WHERE number_plate_receipt_id = ?
        """, (new_status, receipt_id)).rowcount

    db.commit()

    if updated > 0:
        return jsonify({"status": "Dispatch status updated"})
    else:
        return jsonify({"error": "Receipt not found"}), 404

# --- Other unchanged endpoints below ---

# (keep all your previous endpoints exactly as before, e.g. payments, vehicle registration, approvals, etc.)

# Run server
if __name__ == "__main__":
    app.run(debug=True)
