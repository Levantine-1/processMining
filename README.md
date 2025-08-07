# Process Mining Demo

This project is a Flask-based web application that generates synthetic customers, transactions, and event data which is used to generate charts with Matplotlib.
It demonstrates process mining concept: Performance Analysis. 

## Features

- Generate random customer, item, transaction, and event data
- Visualize average cook time per food item
- Visualize total items ordered by transaction method
- Simple web interface for data exploration

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip

### Installation

1. Clone the repository:
2. Install dependencies: pip install -r requirements.txt

### Running the App

Start the Flask server: python processmining.py

Visit `http://localhost:5000` in your browser.

## API Endpoints

- `/sample_data?entries=N` (GET): Generate sample data with N customer transactions.
- `/cook_time_chart` (POST): Returns a PNG chart of average cook time per item.
- `/items_by_transaction_method_chart` (POST): Returns a PNG chart of total items ordered by transaction method.

## File Structure

- `processmining.py` — Main application code
- `requirements.txt` — Python dependencies