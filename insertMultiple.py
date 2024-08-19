import os
import requests
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# API endpoint
api_base_url = "https://api.diplomazonebd.com/results"

# Load JSON data from file
def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Insert new record
def insert_record(data):
    response = requests.post(api_base_url, json=data)
    if response.status_code == 201:
        return "Record inserted successfully."
    else:
        return f"Error inserting record: {response.status_code}, Response: {response.text}"

# Process a single record
def process_single_record(record):
    roll_number = record.get('roll_number')
    semester = record.get('result_semester')

    if not roll_number or not semester:
        return f"Missing roll_number or result_semester in record: {record}"

    # Ensure GPA is set based on the status
    status = record.get("result", {}).get("status", "")
    gpa = record.get("result", {}).get("GPA", None)

    # Handle GPA based on status
    if status == "failed":
        gpa = "null"  # GPA should be set to "null" for failed status
    elif status == "passed" and gpa is None:
        return f"Error: GPA is required for passed status in record: {record}"

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

    return insert_record(new_record)

# Process each record in JSON data in parallel
def process_records(data, max_workers=4):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_record, record): record for record in data}
        for future in tqdm(as_completed(futures), desc="Processing records", total=len(data), unit="record"):
            result = future.result()
            results.append(result)
            if "Error" in result:
                print(result)
    return results

# Process all JSON files in a directory
def process_directory(directory, max_workers=4):
    if not os.path.isdir(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in the directory '{directory}'.")
        return

    print(f"Found {len(json_files)} JSON file(s) in the directory '{directory}'.")
    
    for filename in tqdm(json_files, desc="Processing files", unit="file"):
        file_path = os.path.join(directory, filename)
        print(f"Processing file: {filename}")
        data = load_json(file_path)
        process_records(data, max_workers=max_workers)

# Main function
def main():
    directory = input("Enter the directory path containing JSON files: ")
    process_directory(directory)

if __name__ == "__main__":
    main()
