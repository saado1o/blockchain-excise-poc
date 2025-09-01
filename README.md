# Blockchain Excise Officer Dashboard

## Overview

This project is a **Blockchain-based Excise Tax Management Dashboard** designed to help excise officers manage vehicle tax payments, number plate applications, and ownership transfers securely and transparently using blockchain technology and a web interface.

---

## Table of Contents
- [Motivation](#motivation)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Setup & Usage](#setup--usage)
- [API Endpoints](#api-endpoints)
- [Testing & Debugging](#testing--debugging)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Motivation

Manual excise tax and vehicle ownership management is often cumbersome, error-prone, and lacks transparency. This project leverages **Ethereum blockchain smart contracts** combined with a **Flask-based web dashboard** for officers and citizens to enhance:

- Secure and immutable proof of tax payments  
- Transparent and auditable ownership transfers  
- Efficient approval workflows for excise officers  
- Real-time tracking of transactions and dispatch status

---

## Features

- Citizen login and tax payment submission  
- Vehicle ownership registration and transfer requests  
- Number plate application and approval workflows  
- Officer dashboard for viewing payments, pending approvals, and updating dispatch status  
- Blockchain-backed transaction verification using Ethereum smart contracts  
- Responsive, Bootstrap-based UI with dynamic data loading  
- Role-based access control (citizen vs officer)

---

## Architecture

**Components:**
- **Frontend:** Flask-rendered templates with Bootstrap, JavaScript for dynamic updates
- **Backend:** Flask REST API serving data and connecting to SQLite database
- **Blockchain:** Ethereum Ganache local node running smart contracts for transaction recording
- **Database:** SQLite manages transaction metadata, approval statuses, and user info

---

## Technology Stack

- Python 3.11+ and Flask  
- SQLite database  
- Web3.py to interact with Ethereum node  
- Ethereum smart contracts (Solidity) deployed on Ganache  
- Frontend: HTML5, CSS3, Bootstrap 5, Vanilla JavaScript  
- GitHub for version control and collaboration  

---

## Getting Started

### Prerequisites

- Python 3.11+  
- Node.js and npm (for Ganache)  
- Ganache for Ethereum local blockchain  
- Git for version control  

### Installation Steps

1. Clone the repository:
git clone https://github.com/yourusername/blockchain-excise-dashboard.git
cd blockchain-excise-dashboard

text

2. Set up Python virtual environment and install packages:
python -m venv .venv
source .venv/bin/activate # On Windows use '.venv\Scripts\activate'
pip install -r requirements.txt

text

3. Start Ganache Ethereum local blockchain and deploy contracts.

4. Run the Flask backend server:
python app.py

text

5. Navigate to `http://localhost:5000` in your browser

---

## Project Structure

blockchain-excise-dashboard/
├── app.py # Main Flask backend app
├── contracts/ # Solidity contracts and compiled JSON ABI
├── static/
│ ├── css/
│ ├── js/
│ └── officer.js # Dashboard JavaScript
├── templates/
│ ├── base.html # Base Jinja2 template
│ ├── officer.html # Officer dashboard template
│ └── ... # Other templates
├── requirements.txt # Python dependencies
├── README.md # Project documentation
└── docs/
└── architecture_diagram.png

text

---

## Setup & Usage

- Register users as citizen or officer through the login system
- Citizens can pay tax, request vehicle registration, ownership transfer, and number plate application
- Officers can log in to the dashboard to view payments, pending approvals, and approve them
- Officers can update dispatch statuses for number plates or ownership transfer documents
- All relevant actions are recorded on the blockchain and synced with SQLite database

---

## API Endpoints

- `/api/payments` - List payments (officer)  
- `/api/pending_numberplates` - Pending number plate applications (officer)  
- `/api/pending_ownershiptransfers` - Pending ownership transfers (officer)  
- `/api/approve_number_plate` - Approve number plate (officer)  
- `/api/approve_ownership_transfer` - Approve ownership transfer (officer)  
- `/api/pay_tax` - Citizen tax payment submission  
- `/api/request_ownership_transfer` - Citizen ownership transfer request  
- `/api/apply_number_plate` - Citizen number plate application  
- `/api/track_receipt/<receipt_id>` - Track transaction/dispatch status  

(Refer to `app.py` for detailed request/response formats)

---

## Testing & Debugging

- Use Postman or curl commands to test backend APIs  
- Use browser DevTools (console & network tab) for frontend debugging  
- Logs in Flask server console help diagnose issues  
- Write unit tests for API and integration tests as needed

---

## Contributing

Contributions welcome! Please fork repository, create feature branch, and submit pull requests for review.

---

## License

MIT License - See LICENSE file for details.

---
