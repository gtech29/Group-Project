COMP440 Team Project Phase 3

Project Title
Online Rental Apartments Database System

Overview
This project is a Python Tkinter and MySQL application for managing online rental apartments. Registered users can sign up, log in, post rental units, search rentals by feature, write reviews, and run the required Phase 3 report queries through the graphical user interface.

Group Member Contributions
Replace the names below with the final group member names before submission.

Member 1: Jacob Arce
- Implemented user registration, login validation, password hashing, and database connection setup.
- Helped design the MySQL schema for users, rental units, rental features, and reviews.

Member 2: Gloria 
- Implemented rental unit posting, feature storage, feature search, and review submission.
- Added validation for daily rental limits, daily review limits, no self-review, and one review per rental unit.

Member 3: Juan C Rodriguez
- Implemented the Phase 3 report interface and SQL queries.
- Tested demo data and verified that the required reports return results through the GUI.

Technologies Used
- Python
- Tkinter
- MySQL
- mysql-connector-python
- python-dotenv

Required Files
- main.py: Main application source code.
- database.sql: SQL script that creates the project database and tables.
- requirements.txt: Python dependency list.
- .env: Local database configuration file. This file may need to be created or updated on the demo machine.

Database Setup
1. Install and start MySQL Server.
2. Create the database and tables by running database.sql in MySQL Workbench or another MySQL client.
3. Make sure the database name is login_system unless you update DB_NAME in the .env file.

Environment Setup
Create a .env file in the project folder with these values:

DB_USERNAME=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_NAME=login_system

Python Setup
1. Open a terminal in the project folder.
2. Optional but recommended: create and activate a virtual environment.

Windows:
python -m venv venv
venv\Scripts\activate

Mac/Linux:
python3 -m venv venv
source venv/bin/activate

3. Install dependencies:

pip install -r requirements.txt

Run Instructions
Run the application with:

python main.py

If using the included Windows virtual environment, run:

venv\Scripts\python.exe main.py

Demo Notes
- All project functionality should be performed through the GUI.
- Direct SQL execution should only be used for setup or debugging, not during the demo.
- The database should be populated before the demo so each Phase 3 report returns meaningful results.

Suggested Demo Inputs
- Phase 3 Report 2: Feature X = Kitchen, Feature Y = Wi-Fi
- Phase 3 Report 3: Username X = juantest
- Phase 3 Report 4: Date = 2026-04-27

Phase 3 Functionality
The Phase 3 Reports screen implements the following required reports:
1. List the most expensive rental units for each feature.
2. List users who posted two different rental units on the same day, where one rental has feature X and the other has feature Y.
3. List rental units posted by user X where all reviews are Excellent or Good, and the rentals have at least one review.
4. List users who posted the most rental units on a specific date, including ties.
5. Display users who posted reviews and every review they posted is Poor.
6. Display users whose posted rental units never received Poor reviews, including rentals with no reviews.

