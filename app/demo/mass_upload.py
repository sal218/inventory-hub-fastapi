import csv
import json
import requests

# URL for login and adding items (adjust the port if necessary)
login_url = "http://127.0.0.1:8000/login"
upload_url = "http://127.0.0.1:8000/inventory/add"

# Replace with valid credentials
login_payload = {
    "username": "Enter User Name",  # Replace with a valid username
    "password": "Password to that account"   # Replace with the corresponding password
}

# Start a session to persist cookies
session = requests.Session()

# Log in to obtain the authentication cookie
login_response = session.post(login_url, data=login_payload)
if login_response.status_code not in (200, 302):
    print("Login failed:", login_response.text)
    exit(1)
else:
    print("Login successful.")

# Path to the CSV file (ensure it’s in the same directory or adjust the path accordingly)
csv_file_path = "inventory_items.csv"

# Open and read the CSV file
with open(csv_file_path, mode="r", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Prepare form data for each item.
        # The /inventory/add endpoint expects the following form fields:
        # name, description, quantity, price, category, category_id.
        # Note: The backend handles category creation if category_id is empty.
        data = {
            "name": row["name"],
            "description": row.get("description", ""),
            "quantity": row["quantity"],
            "price": row["price"],
            "category": row["category"],
            "category_id": row.get("category_id", "")
        }
        response = session.post(upload_url, data=data)
        if response.status_code in (200, 302):
            print(f"Uploaded: {data['name']}")
        else:
            print(f"Failed to upload {data['name']}: {response.status_code} - {response.text}")
