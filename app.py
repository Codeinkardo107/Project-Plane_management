from flask import Flask, request, jsonify
import csv
import os
import ast

app = Flask(__name__)
CSV_file = 'data.csv'


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
                row['flight_dates'] = ast.literal_eval(row['flight_dates'])
            except:
                row['flight_dates'] = []
            data.append(row)
        return data

def save_data(data):
    with open(CSV_file, mode='w', newline='') as f:
        fieldnames = ['id', 'name', 'model', 'capacity', 'flight_dates']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            row = item.copy()
            row['flight_dates'] = str(item['flight_dates'])  # store list as string
            writer.writerow(row)


# API Endpoints
@app.route('/')
def home():
    return "🛩️ Flask API for Plane Management is Running!"

@app.route('/about')
def about():
    return "This page has been created by Bhavya Yadav"

@app.route('/add_plane', methods=['POST'])
def add_plane():
    data = load_data()
    new_plane = request.json

    required_fields = ['id', 'name', 'model', 'capacity', 'flight_dates']
    if not all(field in new_plane for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        new_plane['id'] = int(new_plane['id'])
    except:
        return jsonify({'error': 'Invalid ID'}), 400

    if any(p['id'] == new_plane['id'] for p in data):
        return jsonify({'error': 'ID already exists'}), 409  # Conflict

    try:
        new_plane['capacity'] = int(new_plane['capacity'])
    except:
        new_plane['capacity'] = 0

    if isinstance(new_plane['flight_dates'], str):
        try:
            new_plane['flight_dates'] = ast.literal_eval(new_plane['flight_dates'])
        except:
            new_plane['flight_dates'] = []
    elif not isinstance(new_plane['flight_dates'], list):
        new_plane['flight_dates'] = []

    data.append(new_plane)
    save_data(data)

    return jsonify(new_plane), 201



@app.route('/add_flight/<int:plane_id>/<new_date>', methods=['POST'])
def add_flight(plane_id, new_date):
    data = load_data()
    updated = False

    for plane in data:
        if plane['id'] == plane_id:

            if new_date not in plane['flight_dates']:
                plane['flight_dates'].append(new_date)
                updated = True
                break
            else:
                return jsonify({'error': 'Date already exists'}), 400

    if updated:
        save_data(data)
        return jsonify({'message': 'Flight date added successfully'}), 200
    else:
        return jsonify({'error': 'Plane not found'}), 404




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
    updated = False
    
    for plane in data:
        if plane['id'] == plane_id:
            if date_to_remove in plane['flight_dates']:
                plane['flight_dates'].remove(date_to_remove)
                updated = True
                break
    
    if updated:
        save_data(data)
        return jsonify({'message': 'Date removed successfully'}), 200
    else:
        return jsonify({'error': 'Plane or date not found'}), 404



if __name__ == '__main__':
    app.run(debug=True)
