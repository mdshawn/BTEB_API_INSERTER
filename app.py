import requests
import json

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
    for record in data:
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

        # Debug: Print the new record
        print(f"Final record to be processed: {json.dumps(new_record, indent=4)}")

        # Check if record exists
        if record_exists(roll_number, semester):
            print(f"Updating record with roll number {roll_number} and semester {semester}.")
            update_record(new_record)
        else:
            print(f"Inserting new record with roll number {roll_number} and semester {semester}.")
            insert_record(new_record)

# Main function
def main():
    json_filename = 'Result_6th_2016_Regulation.json'  # Update this with the path to your JSON file
    data = load_json(json_filename)
    process_records(data)

if __name__ == "__main__":
    main()
