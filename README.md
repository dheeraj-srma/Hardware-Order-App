# Hardware-Order-App


A mobile-first web application designed to replace manual and WhatsApp-based ordering for hardware dealers. The system allows dealers to place structured orders, which are instantly stored in a centralized Google Sheet.

Built using Python, Streamlit, and Google Sheets as a lightweight backend.

---

## Problem Statement

In many small and mid-scale hardware businesses, dealers place orders through:

- Phone calls
- WhatsApp messages
- Handwritten notes

This leads to:

- Unstructured orders
- Missing item details
- Human errors
- Difficult order tracking

This project solves the problem by creating a simple digital ordering portal that dealers can use directly from their mobile phones.

---

## Features

### Dealer Side
- Mobile-friendly interface
- No login required
- Category-based product selection
- Multi-item ordering within each category
- Automatic order ID generation
- Instant order submission

### Business Side
- Real-time order storage in Google Sheets
- Structured order records
- Easy filtering and tracking
- No complex database required

---

## Tech Stack

- Frontend: Streamlit (Python)
- Backend database: Google Sheets
- Language: Python
- Deployment: Streamlit Cloud

---

## How It Works

1. Dealer opens the order link on their phone.
2. Enters dealer name and shop name.
3. Selects a category.
4. Selects multiple items within that category.
5. Enters quantities.
6. Submits the order.
7. Order is instantly saved to Google Sheets.

---

## Example Order Flow

Category: Gold

Selected items:
- Basin Mixer → Qty: 5
- Angle Valve → Qty: 2

Saved in Google Sheets as:

Order ID: ORD-20260207-001  
Dealer: Rajesh  
Shop: Noida Hardware  
Items:
- Basin Mixer (Gold) → 5
- Angle Valve (Gold) → 2

---

## Project Structure

hardware-order-portal/
- app.py
- requirements.txt
- logo.png
- .gitignore
- .streamlit/
  - secrets.toml (not included in repo)

---

## Installation (Local Setup)

1. Clone the repository  
git clone https://github.com/yourusername/hardware-order-portal.git  
cd hardware-order-portal  

2. Install dependencies  
pip install -r requirements.txt  

3. Add secrets file  
Create a folder named `.streamlit` and inside it create a file:

secrets.toml

Paste your Google service account credentials inside.

4. Run the app  
streamlit run app.py  

---

## Google Sheets Structure

### Inventory sheet

Columns:
- Item Name
- Category
- SKU

Example:
Basin Mixer | Basin | BM-001  
Angle Valve | Valve | AV-010  

### Orders sheet

Columns:
- Order ID
- Timestamp
- Dealer Name
- Shop Name
- Item Name
- Category
- SKU
- Qty

---

## Security Note

The file `.streamlit/secrets.toml` contains sensitive credentials and is excluded using `.gitignore`.

Never upload this file to GitHub.

---

## Future Improvements

- Admin dashboard for order tracking
- Dealer login system
- PDF invoice generation
- WhatsApp order notifications
- Inventory stock management
- Sales analytics dashboard

---

## Author

Dheeraj Sharma  
Developed as a real-world solution for a hardware distribution business.
