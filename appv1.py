import os
import requests
import json
from tqdm import tqdm

# API endpoint
api_base_url = "https://api.diplomazonebd.com/results"

# Load JSON data from file
def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Check if the record exists
def record_exists(roll_number, semester):
    params = {'roll_number': roll_number, 'semester': semester}
    response = requests.get(api_base_url, params=params)
    if response.status_code == 200:
        results = response.json()
        return len(results) > 0
    elif response.status_code == 404:
        print(f"Error checking record: {response.status_code}")
        print("Response:", response.text)
        return False
    else:
        print(f"Error checking record: {response.status_code}")
        print("Response:", response.text)
        return False

# Update existing record
def update_record(data):
    response = requests.put(api_base_url, json=data)
    if response.status_code == 200:
        print("Record updated successfully.")
    else:
        print(f"Error updating record: {response.status_code}")
        print("Response:", response.text)

# Insert new record
def insert_record(data):
    response = requests.post(api_base_url, json=data)
    if response.status_code == 201:
        print("Record inserted successfully.")
    else:
        print(f"Error inserting record: {response.status_code}")
        print("Response:", response.text)

# Process each record in JSON data
def process_records(data):
    for record in tqdm(data, desc="Processing records", unit="record"):
        roll_number = record.get('roll_number')
        semester = record.get('result_semester')

        if not roll_number or not semester:
            print(f"Missing roll_number or result_semester in record: {record}")
            continue

        # Ensure GPA is set based on the status
        status = record.get("result", {}).get("status", "")
        gpa = record.get("result", {}).get("GPA", None)

        # Handle GPA based on status
        if status == "failed":
            gpa = "null"  # GPA should be set to "null" for failed status
        elif status == "passed" and gpa is None:
            print(f"Error: GPA is required for passed status in record: {record}")
            continue

        # Create a new record with the desired format
        new_record = {
            "roll_number": record.get("roll_number"),
            "status": status,
            "GPA": gpa,  # GPA is handled as per the status
            "failed_subjects": record.get("result", {}).get("failed_subjects"),
            "institute_code": record.get("institute_code"),
            "institute_name": record.get("institute_name"),
            "district": record.get("district"),
            "result_date": record.get("result_date"),
            "result_semester": record.get("result_semester"),
            "regulation": record.get("regulation"),
            "trade": record.get("trade"),
            "examination_held": record.get("examination_held")
        }

        # Check if record exists
        if record_exists(roll_number, semester):
            update_record(new_record)
        else:
            insert_record(new_record)

# Process all JSON files in a directory
def process_directory(directory):
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    for filename in tqdm(json_files, desc="Processing files", unit="file"):
        file_path = os.path.join(directory, filename)
        print(f"Processing file: {file_path}")
        data = load_json(file_path)
        process_records(data)

# Main function
def main():
    directory = input("Enter the directory path containing JSON files: ")
    if not os.path.isdir(directory):
        print("Invalid directory path.")
        return
    process_directory(directory)

if __name__ == "__main__":
    main()
