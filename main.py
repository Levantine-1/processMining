import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

from flask import Flask, request, make_response

app = Flask(__name__)

def generate_customers(number_of_customers):
    fake = Faker('en_US')
    customers = []
    for _ in range(number_of_customers):
        customer_id = str(uuid.uuid4()).split("-")[0]
        firstname = fake.first_name()
        lastname = fake.last_name()
        gender = random.choice(['male', 'female'])
        dob = fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat()
        address = fake.address().replace('\n', ', ')
        customers.append({
            "customer_id": customer_id,
            "firstname": firstname,
            "lastname": lastname,
            "gender": gender,
            "dob": dob,
            "address": address,
        })
    return customers

def get_items():
    items = [ # IN-N-OUT Menu from an image from Nov 2023
        {"item_id": str(uuid.uuid4()).split("-")[0], "name": "Double Double Cheeseburger", "price": 6.40},
        {"item_id": str(uuid.uuid4()).split("-")[0], "name": "Cheeseburger", "price": 4.65},
        {"item_id": str(uuid.uuid4()).split("-")[0], "name": "Hamburger", "price": 4.20},
        {"item_id": str(uuid.uuid4()).split("-")[0], "name": "French Fries", "price": 2.50},
        {"item_id": str(uuid.uuid4()).split("-")[0], "name": "Small Soft Drink", "price": 2.30},
        {"item_id": str(uuid.uuid4()).split("-")[0], "name": "Medium Soft Drink", "price": 2.45},
        {"item_id": str(uuid.uuid4()).split("-")[0], "name": "Large Soft Drink", "price": 2.65},
        {"item_id": str(uuid.uuid4()).split("-")[0], "name": "Extra Large Soft Drink", "price": 2.85},
        {"item_id": str(uuid.uuid4()).split("-")[0], "name": "Shakes", "price": 3.20},
        {"item_id": str(uuid.uuid4()).split("-")[0], "name": "Milk", "price": 0.99},
        {"item_id": str(uuid.uuid4()).split("-")[0], "name": "Hot Cocoa", "price": 2.45},
        {"item_id": str(uuid.uuid4()).split("-")[0], "name": "Coffee", "price": 1.45}
    ]
    return items

def generate_transactions(customers, items):
    transactions = []
    base_time = datetime.now()
    num_customers = len(customers)

    for _ in range(num_customers):
        transaction_id = str(uuid.uuid4())
        customer = customers[_]
        num_items = random.randint(1, 4) # Number of types of different items purchased
        purchased_items = random.sample(items, num_items)
        items_list = []
        for item in purchased_items:
            quantity = random.randint(1, 5) # Number of each item purchased
            items_list.append({
                "item_id": item["item_id"],
                "quantity": quantity
            })
        timestamp = base_time + timedelta(hours=random.randint(0, 1000))

        transaction_method = random.choice(["Front Counter", "Drive Thru", "Online Order"])
        payment_method = random.choice(["Credit Card", "Debit Card", "Cash", "Mobile Payment"])
        transactions.append({
            "transaction_id": transaction_id,
            "customer_id": customer["customer_id"],
            "transaction_method": transaction_method,
            "payment_method": payment_method,
            "timestamp": timestamp.isoformat(),
            "items": items_list,
        })
    return transactions


def get_sample_data(entries):
    customers = generate_customers(number_of_customers=entries)
    items = get_items()
    transactions = generate_transactions(customers, items)
    return customers, items, transactions


def print_sample_data(sample_data):
    customers, items, transactions = sample_data

    print("Customers:")
    for c in customers:
        print(c)

    print("\nItems:")
    for i in items:
        print(i)

    print("\nTransactions:")
    for t in transactions:
        print(t)


@app.route('/sample_data', methods=['GET'])
def js_sample_data():
    entries = request.args.get('entries', default=10, type=int)
    customers, items, transactions = get_sample_data(entries)

    response = {
        "customers": customers,
        "items": items,
        "transactions": transactions
    }

    return make_response(response, 200)


@app.route('/', methods=['GET'])
def index():
    html = '''
    <html>
      <head>
        <title>Sample Data Generator</title>
      </head>
      <body>
        <h2>Sample Data Generator</h2>
        Number of entries to generate: <input type="number" id="entriesInput" value="10" min="1" style="width:60px;">
        <button id="generateBtn">Generate</button>
        <br><br>
        <label>Customers:</label><br>
        <textarea id="customersBox" rows="10" cols="80" readonly></textarea><br><br>
        <label>Items:</label><br>
        <textarea id="itemsBox" rows="10" cols="80" readonly></textarea><br><br>
        <label>Transactions:</label><br>
        <textarea id="transactionsBox" rows="10" cols="80" readonly></textarea>
        <script>
          document.getElementById('generateBtn').onclick = function() {
            var entries = document.getElementById('entriesInput').value || 10;
            fetch('/sample_data?entries=' + encodeURIComponent(entries))
              .then(response => response.json())
              .then(data => {
                document.getElementById('customersBox').value = JSON.stringify(data.customers, null, 2);
                document.getElementById('itemsBox').value = JSON.stringify(data.items, null, 2);
                document.getElementById('transactionsBox').value = JSON.stringify(data.transactions, null, 2);
              })
              .catch(error => {
                document.getElementById('customersBox').value = 'Error: ' + error;
                document.getElementById('itemsBox').value = '';
                document.getElementById('transactionsBox').value = '';
              });
          };
        </script>
      </body>
    </html>
    '''
    return html


def main():
    sample_data = get_sample_data(10)
    print_sample_data(sample_data)

if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=5000)