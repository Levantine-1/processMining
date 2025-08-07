import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import io

from flask import Flask, request, make_response, send_file
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
        ticket_number = _ # A simple ticket number because using UUID makes the graph ugly
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
            "ticket_number": ticket_number,
            "customer_id": customer["customer_id"],
            "transaction_method": transaction_method,
            "payment_method": payment_method,
            "timestamp": timestamp.isoformat(),
            "items": items_list,
        })
    return transactions


def generate_event_data(transactions): # This part is mostly AI generated
    all_events = []
    for transaction in transactions:
        base_time = datetime.fromisoformat(transaction["timestamp"])
        events = []
        minutes = 0

        # Order placed
        events.append({
            "transaction_id": transaction["transaction_id"],
            "ticket_number": transaction["ticket_number"],
            "event": "order placed",
            "timestamp": (base_time + timedelta(minutes=minutes)).isoformat()
        })
        minutes += random.randint(1, 3)

        # Payment processed
        events.append({
            "transaction_id": transaction["transaction_id"],
            "ticket_number": transaction["ticket_number"],
            "event": "payment processed",
            "timestamp": (base_time + timedelta(minutes=minutes)).isoformat()
        })
        minutes += random.randint(1, 3)

        # Each item prepared
        for item in transaction["items"]:
            events.append({
                "transaction_id": transaction["transaction_id"],
                "ticket_number": transaction["ticket_number"],
                "event": f"item prepared ({item['item_id']})",
                "timestamp": (base_time + timedelta(minutes=minutes)).isoformat()
            })
            minutes += random.randint(1, 2)

        # Order delivered
        events.append({
            "transaction_id": transaction["transaction_id"],
            "ticket_number": transaction["ticket_number"],
            "event": "order delivered",
            "timestamp": (base_time + timedelta(minutes=minutes)).isoformat()
        })
        minutes += random.randint(1, 2)

        # Randomly cancel the order
        if random.random() < 0.1:  # 10% chance to cancel
            events.append({
                "transaction_id": transaction["transaction_id"],
                "ticket_number": transaction["ticket_number"],
                "event": "order cancelled",
                "timestamp": (base_time + timedelta(minutes=minutes)).isoformat()
            })

        all_events.extend(events)
    return all_events


def get_sample_data(entries):
    customers = generate_customers(number_of_customers=entries)
    items = get_items()
    transactions = generate_transactions(customers, items)
    events = generate_event_data(transactions)
    return customers, items, transactions, events


def print_sample_data(sample_data):
    customers, items, transactions, events = sample_data

    print("Customers:")
    for c in customers:
        print(c)

    print("\nItems:")
    for i in items:
        print(i)

    print("\nTransactions:")
    for t in transactions:
        print(t)

    print("\nEvents:")
    for e in events:
        print(e)


@app.route('/sample_data', methods=['GET'])
def js_sample_data():
    entries = request.args.get('entries', default=10, type=int)
    customers, items, transactions, events = get_sample_data(entries)
    if entries < 1:
        return make_response({"error": "Number of entries must be at least 1"}, 400)
    if entries > 1000:
        return make_response({"error": "Number of entries must not exceed 1000"}, 400)

    response = {
        "customers": customers,
        "items": items,
        "transactions": transactions,
        "events": events
    }

    return make_response(response, 200)


@app.route('/', methods=['GET'])
def index(): # This part is mostly AI generated
    html = '''
<html>
<head>
  <title>Levantine Demo</title>
</head>
<body>
  <h2>Process Mining Demo</h2>
  Number of customer transactions to generate: <input type="number" id="entriesInput" value="100" min="1" style="width:60px;">
  <button id="generateBtn">Generate</button>
  <br><br>
  <label>Customers: Randomly Generated</label><br>
  <textarea id="customersBox" rows="10" cols="80" readonly></textarea><br><br>
  <label>Items: A fixed dictionary of items and prices from In-n-out</label><br>
  <textarea id="itemsBox" rows="10" cols="80" readonly></textarea><br><br>
  <label>Transactions: For each customer, generate a transaction with some items</label><br>
  <textarea id="transactionsBox" rows="10" cols="80" readonly></textarea><br><br>
  <label>Events: For each transaction, generate events for every step</label><br>
  <textarea id="eventsBox" rows="10" cols="80" readonly></textarea><br><br>
  <br>
  Process Mining Concept Demonstrated: Performance Analysis
  <img id="cookTimeChart" style="display:none; max-width:600px; margin-top:10px;" />
  <br><br>
  <br>
  <img id="itemsByMethodChart" style="display:none; max-width:600px; margin-top:10px;" />
  <script>
  let lastSampleData = null;

  function fetchChart(endpoint, imgId) {
    if (!lastSampleData) return;
    fetch(endpoint, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(lastSampleData)
    })
    .then(response => response.blob())
    .then(blob => {
      const url = URL.createObjectURL(blob);
      document.getElementById(imgId).src = url;
      document.getElementById(imgId).style.display = 'block';
    });
  }

  document.getElementById('generateBtn').onclick = function() {
    var entries = document.getElementById('entriesInput').value || 10;
    fetch('/sample_data?entries=' + encodeURIComponent(entries))
      .then(response => response.json())
      .then(data => {
        lastSampleData = data;
        document.getElementById('customersBox').value = JSON.stringify(data.customers, null, 2);
        document.getElementById('itemsBox').value = JSON.stringify(data.items, null, 2);
        document.getElementById('transactionsBox').value = JSON.stringify(data.transactions, null, 2);
        document.getElementById('eventsBox').value = JSON.stringify(data.events, null, 2);

        // Auto-fetch and display charts
        fetchChart('/cook_time_chart', 'cookTimeChart');
        fetchChart('/items_by_transaction_method_chart', 'itemsByMethodChart');
      })
      .catch(error => {
        document.getElementById('customersBox').value = 'Error: ' + error;
        document.getElementById('itemsBox').value = '';
        document.getElementById('transactionsBox').value = '';
        document.getElementById('eventsBox').value = '';
      });
  };
</script>
</body>
</html>
    '''
    return html


@app.route('/cook_time_chart', methods=['POST'])
def get_chart_for_cook_time_per_food_item(): # This function is mostly AI generated
    sample_data = request.get_json(force=True)
    events_dataframe = pd.DataFrame(sample_data['events'])
    items_df = pd.DataFrame(sample_data['items'])
    item_id_to_name = dict(zip(items_df['item_id'], items_df['name']))

    item_prepared_events = events_dataframe[events_dataframe['event'].str.startswith('item prepared')]
    payment_processed_events = events_dataframe[events_dataframe['event'] == 'payment processed']

    item_prepared_events = item_prepared_events.copy()
    item_prepared_events['item_id'] = item_prepared_events['event'].str.extract(r'\((.*?)\)')

    payment_times = payment_processed_events[['transaction_id', 'timestamp']].rename(
        columns={'timestamp': 'payment_time'})
    item_prepared_events = item_prepared_events.merge(payment_times, on='transaction_id', how='left')

    item_prepared_events['prepared_time'] = pd.to_datetime(item_prepared_events['timestamp'])
    item_prepared_events['payment_time'] = pd.to_datetime(item_prepared_events['payment_time'])
    item_prepared_events['cook_time_min'] = (item_prepared_events['prepared_time'] - item_prepared_events['payment_time']).dt.total_seconds() / 60

    item_prepared_events['item_name'] = item_prepared_events['item_id'].map(item_id_to_name)

    avg_cook_times = item_prepared_events.groupby('item_name')['cook_time_min'].mean().sort_values()

    fig, ax = plt.subplots(figsize=(8, 4))
    avg_cook_times.plot(kind='barh', ax=ax, title='Average Cook Time per Item (minutes)')
    ax.set_ylabel('Item')
    ax.set_xlabel('Average Cook Time (min)')
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return make_response(send_file(buf, mimetype='image/png'))


@app.route('/items_by_transaction_method_chart', methods=['POST'])
def plot_total_items_by_transaction_method(): # This part is mostly AI generated
    sample_data = request.get_json(force=True)
    transactions = pd.DataFrame(sample_data['transactions'])

    rows = []
    for _, row in transactions.iterrows():
        for item in row['items']:
            rows.append({
                'transaction_method': row['transaction_method'],
                'quantity': item['quantity']
            })
    items_df = pd.DataFrame(rows)
    totals = items_df.groupby('transaction_method')['quantity'].sum().sort_values()

    fig, ax = plt.subplots(figsize=(8, 4))
    totals.plot(kind='barh', color='skyblue', ax=ax, title='Total Items Ordered by Transaction Method')
    ax.set_xlabel('Total Items Ordered')
    ax.set_ylabel('Transaction Method')
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return make_response(send_file(buf, mimetype='image/png'))


def main():
    sample_data = get_sample_data(6)
    print_sample_data(sample_data)

    get_chart_for_cook_time_per_food_item(sample_data)
    plot_total_items_by_transaction_method(sample_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)