# Python

## Task 0 - Python Generators - Task 0: Getting Started

### Objective
Create a Python script to set up a MySQL database and insert data using a CSV file.

### Features
- Connects to MySQL server
- Creates database `ALX_prodev` if it doesn't exist
- Creates table `user_data` with fields:
  - `user_id` (UUID, Primary Key)
  - `name`, `email`, `age`
- Inserts data from `user_data.csv`
- Prints first 5 rows to verify insert

## Task 1 - Stream rows from SQL with a generator

This task implements a generator `stream_users()` in the file `0-stream_users.py` that connects to a MySQL database `ALX_prodev`, fetches users from the `user_data` table and yields each row one by one as a dictionary.

## Task 2 - Batch processing large data

This task uses a generator to fetch user data from a SQL database in batches using `fetchmany`.

### Files:
- `1-batch_processing.py`: Contains:
  - `stream_users_in_batches(batch_size)` – yields batches from the database.
  - `batch_processing(batch_size)` – filters users older than 25 and prints them.

## Requirements
- Python 3.x
- mysql-connector-python
- MySQL running (via Laragon or local install)

## How to Run
```bash
pip freeze > requirements.txt
python 0-main.py
python3 1-main.py
