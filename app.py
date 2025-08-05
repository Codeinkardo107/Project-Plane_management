from flask import Flask, request, jsonify
import csv, os, ast, datetime
from flask_cors import CORS
from chat_model import process_chat
from chat_page import pdf_text

app = Flask(__name__)
CORS(app)
CSV_file = 'flat_data.csv'


# Utility Functions
def load_data():
    if not os.path.exists(CSV_file):
        return []
    with open(CSV_file, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            try:
                row['id'] = int(row['id'])
            except (ValueError, TypeError):
                row['id'] = None
            try:
                row['capacity'] = int(row['capacity'])
            except (ValueError, TypeError):
                row['capacity'] = 0
            try:
                row['from'] = row.get('from', '')
            except:
                row['from'] = []
            try:
                row['to'] = row.get('to', '')
            except:
                row['to'] = []
            try:
                row['status'] = row.get('status', 'Unknown')
            except:
                row['status'] = 'Unknown'

            data.append(row)
        return data
    

def save_data(data):
    with open(CSV_file, mode='w', newline='') as f:
        fieldnames = ['id', 'name', 'model', 'capacity', 'date', 'from', 'to', 'status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            writer.writerow({
                'id': item['id'],
                'name': item['name'],
                'model': item['model'],
                'capacity': item['capacity'],
                'date': item['date'],
                'from': item['from'],
                'to': item['to'],
                'status': item['status']
            })


# API Endpoints
@app.route('/')
def home():
    return "🛩️ Flask API for Plane Management is Running!. \U0001F600"


@app.route('/about')
def about():
    return "This page has been created by Bhavya Yadav"


@app.route('/add_plane', methods=['POST'])
def add_plane():
    try:
        data = load_data()
        new_plane = request.json

        required_fields = ['id', 'name', 'model', 'capacity', 'date', 'from', 'to', 'status']
        missing = [field for field in required_fields if field not in new_plane]

        if missing:
            return jsonify({'error': f"Missing required fields: {', '.join(missing)}"}), 400

        try:
            new_plane['id'] = int(new_plane['id'])
        except:
            return jsonify({'error': 'Invalid ID'}), 400

        try:
            new_plane['date'] = str(new_plane['date'])
        except:
            return jsonify({'error': 'Invalid date'}), 400

        # Check for duplicate
        for flight in data:
            if (flight['id'] == new_plane['id'] and
                flight['date'] == new_plane['date'] and
                flight['from'] == new_plane['from'] and
                flight['to'] == new_plane['to']):
                return jsonify({'error': 'Flight already exists'}), 409

        data.append(new_plane)
        save_data(data)

        return jsonify({'message': 'Flight added successfully'}), 201

    except Exception as e:
        # Catch unexpected errors and return them as JSON
        return jsonify({'error': f"❌ Internal Server Error: {str(e)}"}), 500




@app.route('/add_flight/<int:plane_id>/<new_date>/<from1>/<to1>/<status1>', methods=['POST'])
def add_flight(plane_id, new_date, from1, to1, status1):
    data = load_data()

    # Check if such a flight already exists
    for flight in data:
        if (flight['id'] == plane_id and
            flight['date'] == new_date and
            flight['from'] == from1 and
            flight['to'] == to1):
            return jsonify({'error': 'Flight already exists'}), 400

    # Find base plane info
    plane = next((f for f in data if f['id'] == plane_id), None)
    if not plane:
        return jsonify({'error': 'Plane not found'}), 404

    new_plane = {
        'id': plane_id,
        'name': plane['name'],
        'model': plane['model'],
        'capacity': plane['capacity'],
        'date': new_date,
        'from': from1,
        'to': to1,
        'status': status1
    }

    data.append(new_plane)
    save_data(data)
    return jsonify({'message': 'Flight added successfully'}), 200




@app.route('/planes', methods=['GET'])
def list_planes():
    data = load_data()
    return jsonify(data), 200


@app.route('/delete_plane/<int:plane_id>', methods=['DELETE'])
def delete_plane(plane_id):
    data = load_data()
    updated = [p for p in data if p['id'] != plane_id]

    if len(updated) == len(data):
        return jsonify({'error': 'Plane not found'}), 404
    save_data(updated)
    return jsonify({'message': f'Plane with ID {plane_id} deleted.'}), 200


@app.route('/delete_flight/<int:plane_id>/<date_to_remove>', methods=['POST'])
def delete_flight(plane_id, date_to_remove):
    data = load_data()
    updated = [p for p in data if not (p['id'] == plane_id and p['date'] == date_to_remove)]

    if len(updated) <  len(data):
        save_data(updated)
        return jsonify({'message': 'Date removed successfully'}), 200
    else:
        return jsonify({'error': 'Plane or date not found'}), 404



@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    try:
        response = process_chat(user_input, pdf_text)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"response": f"❌ Error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
