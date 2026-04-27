import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode


load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "login_system")

current_user = None
root = None


# ---------------------------------------------------------
# Database helpers
# ---------------------------------------------------------


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_db_connection():
    try:
        return mysql.connector.connect(
            user=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_NAME,
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            messagebox.showerror("DB Error", "Wrong database username or password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            messagebox.showerror("DB Error", f"Database '{DB_NAME}' does not exist.")
        else:
            messagebox.showerror("DB Error", str(err))
        return None


def initialize_database():
    """
    Creates the required tables if they do not already exist.

    Schema:
    user(username, password, firstName, lastName, email, phone)
    rental_unit(rental_id, title, description, price, username, created_at)
    rental_feature(rental_id, feature)
    review(review_id, rental_id, username, score, remark, created_at)
    """

    cnx = get_db_connection()
    if not cnx:
        return

    cursor = cnx.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                username VARCHAR(50) PRIMARY KEY,
                password VARCHAR(255) NOT NULL,
                firstName VARCHAR(100) NOT NULL,
                lastName VARCHAR(100) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                phone VARCHAR(50) NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rental_unit (
                rental_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                username VARCHAR(50) NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES user(username)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rental_feature (
                rental_id INT NOT NULL,
                feature VARCHAR(100) NOT NULL,
                PRIMARY KEY (rental_id, feature),
                FOREIGN KEY (rental_id) REFERENCES rental_unit(rental_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review (
                review_id INT AUTO_INCREMENT PRIMARY KEY,
                rental_id INT NOT NULL,
                username VARCHAR(50) NOT NULL,
                score ENUM('Excellent', 'Good', 'Fair', 'Poor') NOT NULL,
                remark TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_rental_review (rental_id, username),
                FOREIGN KEY (rental_id) REFERENCES rental_unit(rental_id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                FOREIGN KEY (username) REFERENCES user(username)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            )
        """)

        cnx.commit()

    except mysql.connector.Error as err:
        messagebox.showerror("DB Initialization Error", str(err))
    finally:
        cursor.close()
        cnx.close()


def fetch_all(query, params=None):
    cnx = get_db_connection()
    if not cnx:
        return [], []

    cursor = cnx.cursor()
    try:
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return columns, rows
    except mysql.connector.Error as err:
        messagebox.showerror("DB Error", str(err))
        return [], []
    finally:
        cursor.close()
        cnx.close()


def execute_write(query, params=None):
    cnx = get_db_connection()
    if not cnx:
        return False

    cursor = cnx.cursor()
    try:
        cursor.execute(query, params or ())
        cnx.commit()
        return True
    except mysql.connector.Error as err:
        messagebox.showerror("DB Error", str(err))
        cnx.rollback()
        return False
    finally:
        cursor.close()
        cnx.close()


# ---------------------------------------------------------
# UI helpers
# ---------------------------------------------------------


def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()


def center_window(window, width, height):
    window.geometry(f"{width}x{height}")
    window.resizable(False, False)


def create_results_window(title, columns, rows):
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("1000x500")

    tk.Label(win, text=title, font=("Arial", 16, "bold")).pack(pady=10)

    if not rows:
        tk.Label(win, text="No results found.", font=("Arial", 12)).pack(pady=20)
        return

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(frame, columns=columns, show="headings")

    y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

    tree.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")

    for row in rows:
        tree.insert("", tk.END, values=row)


def parse_features(feature_text):
    features = []
    seen = set()

    for part in feature_text.split(","):
        feature = part.strip()
        if feature and feature.lower() not in seen:
            features.append(feature)
            seen.add(feature.lower())

    return features


# ---------------------------------------------------------
# Signup and login
# ---------------------------------------------------------


def show_login_window():
    clear_window(root)
    root.deiconify()
    root.title("Login")
    center_window(root, 400, 300)

    tk.Label(root, text="Login Page", font=("Arial", 18, "bold")).pack(pady=20)

    tk.Label(root, text="Username:").pack()
    username_entry = tk.Entry(root, width=30)
    username_entry.pack(pady=5)

    tk.Label(root, text="Password:").pack()
    password_entry = tk.Entry(root, width=30, show="*")
    password_entry.pack(pady=5)

    def handle_login():
        global current_user

        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Login Error", "Please enter username and password.")
            return

        cnx = get_db_connection()
        if not cnx:
            return

        cursor = cnx.cursor()
        try:
            cursor.execute("SELECT password FROM user WHERE username = %s", (username,))
            result = cursor.fetchone()
        except mysql.connector.Error as err:
            messagebox.showerror("DB Error", str(err))
            return
        finally:
            cursor.close()
            cnx.close()

        if not result:
            messagebox.showerror("Login Error", "User not found.")
            return

        stored_hash = result[0]
        entered_hash = hash_password(password)

        if entered_hash != stored_hash:
            messagebox.showerror("Login Error", "Incorrect password.")
            return

        current_user = username
        messagebox.showinfo("Login", f"Welcome {username}!")
        show_dashboard()

    tk.Button(root, text="Login", width=18, command=handle_login).pack(pady=10)
    tk.Button(root, text="Create Account", width=18, command=show_signup_window).pack()


def show_signup_window():
    clear_window(root)
    root.title("Signup")
    center_window(root, 450, 520)

    tk.Label(root, text="Signup Page", font=("Arial", 18, "bold")).pack(pady=15)

    entries = {}

    fields = [
        ("Username", "username"),
        ("Password", "password"),
        ("Confirm Password", "confirm"),
        ("First Name", "firstName"),
        ("Last Name", "lastName"),
        ("Email", "email"),
        ("Phone", "phone"),
    ]

    for label_text, key in fields:
        tk.Label(root, text=f"{label_text}:").pack()
        entry = tk.Entry(root, width=35, show="*" if "Password" in label_text else "")
        entry.pack(pady=4)
        entries[key] = entry

    def handle_signup():
        username = entries["username"].get().strip()
        password = entries["password"].get().strip()
        confirm = entries["confirm"].get().strip()
        first_name = entries["firstName"].get().strip()
        last_name = entries["lastName"].get().strip()
        email = entries["email"].get().strip()
        phone = entries["phone"].get().strip()

        if not all([username, password, confirm, first_name, last_name, email, phone]):
            messagebox.showerror("Signup Error", "All fields are required.")
            return

        if password != confirm:
            messagebox.showerror("Signup Error", "Passwords do not match.")
            return

        cnx = get_db_connection()
        if not cnx:
            return

        cursor = cnx.cursor()
        try:
            cursor.execute(
                """
                SELECT username, email, phone
                FROM user
                WHERE username = %s OR email = %s OR phone = %s
                """,
                (username, email, phone),
            )

            if cursor.fetchone():
                messagebox.showerror(
                    "Signup Error", "Username, email, or phone already exists."
                )
                return

            cursor.execute(
                """
                INSERT INTO user (username, password, firstName, lastName, email, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    username,
                    hash_password(password),
                    first_name,
                    last_name,
                    email,
                    phone,
                ),
            )

            cnx.commit()
            messagebox.showinfo("Signup", "Account created successfully!")
            show_login_window()

        except mysql.connector.Error as err:
            cnx.rollback()
            messagebox.showerror("DB Error", str(err))
        finally:
            cursor.close()
            cnx.close()

    tk.Button(root, text="Signup", width=18, command=handle_signup).pack(pady=15)
    tk.Button(root, text="Back to Login", width=18, command=show_login_window).pack()


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------


def show_dashboard():
    clear_window(root)
    root.title("Rental Dashboard")
    center_window(root, 520, 520)

    tk.Label(
        root,
        text=f"Rental Dashboard - Logged in as {current_user}",
        font=("Arial", 16, "bold"),
    ).pack(pady=20)

    tk.Button(
        root, text="Insert Rental Unit", width=35, command=show_insert_rental
    ).pack(pady=6)
    tk.Button(
        root, text="Search Rentals by Feature", width=35, command=show_search_rentals
    ).pack(pady=6)
    tk.Button(root, text="Write Review", width=35, command=show_write_review).pack(
        pady=6
    )
    tk.Button(root, text="Phase 3 Reports", width=35, command=show_phase3_reports).pack(
        pady=6
    )

    tk.Button(root, text="Logout", width=35, command=logout).pack(pady=30)


def logout():
    global current_user
    current_user = None
    show_login_window()


# ---------------------------------------------------------
# Phase 2: Insert rental
# ---------------------------------------------------------


def show_insert_rental():
    clear_window(root)
    root.title("Insert Rental Unit")
    center_window(root, 550, 460)

    tk.Label(root, text="Insert Rental Unit", font=("Arial", 18, "bold")).pack(pady=15)

    tk.Label(root, text="Title, e.g. Los Angeles, California:").pack()
    title_entry = tk.Entry(root, width=55)
    title_entry.pack(pady=5)

    tk.Label(root, text="Description:").pack()
    description_entry = tk.Entry(root, width=55)
    description_entry.pack(pady=5)

    tk.Label(
        root, text="Features separated by commas, e.g. Mountainview, Kitchen, Wi-Fi:"
    ).pack()
    features_entry = tk.Entry(root, width=55)
    features_entry.pack(pady=5)

    tk.Label(root, text="Price per night:").pack()
    price_entry = tk.Entry(root, width=55)
    price_entry.pack(pady=5)

    def handle_insert():
        title = title_entry.get().strip()
        description = description_entry.get().strip()
        feature_text = features_entry.get().strip()
        price_text = price_entry.get().strip()

        features = parse_features(feature_text)

        if not all([title, description, feature_text, price_text]):
            messagebox.showerror("Error", "All fields are required.")
            return

        if not features:
            messagebox.showerror("Error", "Please enter at least one feature.")
            return

        try:
            price = float(price_text)
            if price < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Price must be a positive number.")
            return

        cnx = get_db_connection()
        if not cnx:
            return

        cursor = cnx.cursor()

        try:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM rental_unit
                WHERE username = %s
                  AND DATE(created_at) = CURDATE()
                """,
                (current_user,),
            )

            count = cursor.fetchone()[0]

            if count >= 2:
                messagebox.showerror(
                    "Limit Reached", "You can only post 2 rental units per day."
                )
                return

            cursor.execute(
                """
                INSERT INTO rental_unit (title, description, price, username)
                VALUES (%s, %s, %s, %s)
                """,
                (title, description, price, current_user),
            )

            rental_id = cursor.lastrowid

            for feature in features:
                cursor.execute(
                    """
                    INSERT INTO rental_feature (rental_id, feature)
                    VALUES (%s, %s)
                    """,
                    (rental_id, feature),
                )

            cnx.commit()
            messagebox.showinfo("Success", "Rental unit added successfully.")

            title_entry.delete(0, tk.END)
            description_entry.delete(0, tk.END)
            features_entry.delete(0, tk.END)
            price_entry.delete(0, tk.END)

        except mysql.connector.Error as err:
            cnx.rollback()
            messagebox.showerror("DB Error", str(err))
        finally:
            cursor.close()
            cnx.close()

    tk.Button(root, text="Submit Rental", width=22, command=handle_insert).pack(pady=20)
    tk.Button(root, text="Back to Dashboard", width=22, command=show_dashboard).pack()


# ---------------------------------------------------------
# Phase 2: Search rentals by feature
# ---------------------------------------------------------


def show_search_rentals():
    clear_window(root)
    root.title("Search Rentals")
    center_window(root, 600, 260)

    tk.Label(root, text="Search Rentals by Feature", font=("Arial", 18, "bold")).pack(
        pady=20
    )

    tk.Label(root, text="Feature:").pack()
    feature_entry = tk.Entry(root, width=40)
    feature_entry.pack(pady=8)

    def handle_search():
        feature = feature_entry.get().strip()

        if not feature:
            messagebox.showerror("Error", "Please enter a feature.")
            return

        query = """
            SELECT
                r.rental_id,
                r.title,
                r.description,
                r.price,
                r.username AS posted_by,
                DATE(r.created_at) AS posted_date,
                GROUP_CONCAT(rf2.feature ORDER BY rf2.feature SEPARATOR ', ') AS features
            FROM rental_unit r
            JOIN rental_feature rf ON r.rental_id = rf.rental_id
            JOIN rental_feature rf2 ON r.rental_id = rf2.rental_id
            WHERE rf.feature = %s
            GROUP BY r.rental_id, r.title, r.description, r.price, r.username, DATE(r.created_at)
            ORDER BY r.price DESC
        """

        columns, rows = fetch_all(query, (feature,))
        create_results_window(f"Rentals with Feature: {feature}", columns, rows)

    tk.Button(root, text="Search", width=22, command=handle_search).pack(pady=10)
    tk.Button(root, text="Back to Dashboard", width=22, command=show_dashboard).pack()


# ---------------------------------------------------------
# Phase 2: Write review
# ---------------------------------------------------------


def show_write_review():
    clear_window(root)
    root.title("Write Review")
    center_window(root, 650, 430)

    tk.Label(root, text="Write a Review", font=("Arial", 18, "bold")).pack(pady=15)

    tk.Label(root, text="Rental ID:").pack()
    rental_id_entry = tk.Entry(root, width=40)
    rental_id_entry.pack(pady=5)

    tk.Label(root, text="Score:").pack()
    score_var = tk.StringVar(value="Excellent")
    score_dropdown = ttk.Combobox(
        root,
        textvariable=score_var,
        values=["Excellent", "Good", "Fair", "Poor"],
        state="readonly",
        width=37,
    )
    score_dropdown.pack(pady=5)

    tk.Label(root, text="Remark:").pack()
    remark_entry = tk.Entry(root, width=60)
    remark_entry.pack(pady=5)

    def handle_review():
        rental_id_text = rental_id_entry.get().strip()
        score = score_var.get().strip()
        remark = remark_entry.get().strip()

        if not rental_id_text or not score or not remark:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            rental_id = int(rental_id_text)
        except ValueError:
            messagebox.showerror("Error", "Rental ID must be a number.")
            return

        cnx = get_db_connection()
        if not cnx:
            return

        cursor = cnx.cursor()

        try:
            cursor.execute(
                "SELECT username FROM rental_unit WHERE rental_id = %s",
                (rental_id,),
            )
            rental = cursor.fetchone()

            if not rental:
                messagebox.showerror("Error", "Rental ID does not exist.")
                return

            owner = rental[0]

            if owner == current_user:
                messagebox.showerror("Error", "You cannot review your own rental unit.")
                return

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM review
                WHERE username = %s
                  AND DATE(created_at) = CURDATE()
                """,
                (current_user,),
            )
            review_count_today = cursor.fetchone()[0]

            if review_count_today >= 3:
                messagebox.showerror(
                    "Limit Reached", "You can only post 3 reviews per day."
                )
                return

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM review
                WHERE rental_id = %s AND username = %s
                """,
                (rental_id, current_user),
            )
            existing_review_count = cursor.fetchone()[0]

            if existing_review_count > 0:
                messagebox.showerror("Error", "You already reviewed this rental unit.")
                return

            cursor.execute(
                """
                INSERT INTO review (rental_id, username, score, remark)
                VALUES (%s, %s, %s, %s)
                """,
                (rental_id, current_user, score, remark),
            )

            cnx.commit()
            messagebox.showinfo("Success", "Review submitted successfully.")

            rental_id_entry.delete(0, tk.END)
            remark_entry.delete(0, tk.END)
            score_var.set("Excellent")

        except mysql.connector.Error as err:
            cnx.rollback()
            messagebox.showerror("DB Error", str(err))
        finally:
            cursor.close()
            cnx.close()

    def show_all_rentals():
        query = """
            SELECT
                r.rental_id,
                r.title,
                r.price,
                r.username AS posted_by,
                DATE(r.created_at) AS posted_date,
                GROUP_CONCAT(rf.feature ORDER BY rf.feature SEPARATOR ', ') AS features
            FROM rental_unit r
            LEFT JOIN rental_feature rf ON r.rental_id = rf.rental_id
            GROUP BY r.rental_id, r.title, r.price, r.username, DATE(r.created_at)
            ORDER BY r.rental_id
        """
        columns, rows = fetch_all(query)
        create_results_window("All Rentals", columns, rows)

    tk.Button(root, text="Submit Review", width=22, command=handle_review).pack(pady=12)
    tk.Button(root, text="View Rental IDs", width=22, command=show_all_rentals).pack(
        pady=4
    )
    tk.Button(root, text="Back to Dashboard", width=22, command=show_dashboard).pack(
        pady=4
    )


# ---------------------------------------------------------
# Phase 3 reports
# ---------------------------------------------------------


def show_phase3_reports():
    clear_window(root)
    root.title("Phase 3 Reports")
    center_window(root, 700, 520)

    tk.Label(root, text="Phase 3 Reports", font=("Arial", 18, "bold")).pack(pady=18)

    tk.Button(
        root,
        text="1. Most Expensive Rental Units for Each Feature",
        width=60,
        command=phase3_report_1,
    ).pack(pady=5)

    tk.Button(
        root,
        text="2. Users Who Posted Feature X and Feature Y on Same Day",
        width=60,
        command=show_phase3_report_2_form,
    ).pack(pady=5)

    tk.Button(
        root,
        text="3. Rentals by User X with Only Excellent/Good Reviews",
        width=60,
        command=show_phase3_report_3_form,
    ).pack(pady=5)

    tk.Button(
        root,
        text="4. Users Who Posted the Most Rentals on a Specific Date",
        width=60,
        command=show_phase3_report_4_form,
    ).pack(pady=5)

    tk.Button(
        root,
        text="5. Users Who Posted Reviews, and Every Review Is Poor",
        width=60,
        command=phase3_report_5,
    ).pack(pady=5)

    tk.Button(
        root,
        text="6. Users Whose Rentals Never Received Poor Reviews",
        width=60,
        command=phase3_report_6,
    ).pack(pady=5)

    tk.Button(root, text="Back to Dashboard", width=30, command=show_dashboard).pack(
        pady=25
    )


def phase3_report_1():
    """
    List the most expensive rental units for each feature.
    Includes ties.
    """

    query = """
        SELECT
            rf.feature,
            r.rental_id,
            r.title,
            r.description,
            r.price,
            r.username AS posted_by,
            DATE(r.created_at) AS posted_date
        FROM rental_feature rf
        JOIN rental_unit r ON rf.rental_id = r.rental_id
        WHERE r.price = (
            SELECT MAX(r2.price)
            FROM rental_feature rf2
            JOIN rental_unit r2 ON rf2.rental_id = r2.rental_id
            WHERE rf2.feature = rf.feature
        )
        ORDER BY rf.feature, r.price DESC, r.rental_id
    """

    columns, rows = fetch_all(query)
    create_results_window(
        "Phase 3 Report 1 - Most Expensive Rentals by Feature", columns, rows
    )


def show_phase3_report_2_form():
    win = tk.Toplevel(root)
    win.title("Phase 3 Report 2")
    win.geometry("500x250")
    win.resizable(False, False)

    tk.Label(
        win,
        text="Users Who Posted Two Rentals on Same Day",
        font=("Arial", 14, "bold"),
    ).pack(pady=15)

    tk.Label(win, text="Feature X:").pack()
    feature_x_entry = tk.Entry(win, width=35)
    feature_x_entry.pack(pady=5)

    tk.Label(win, text="Feature Y:").pack()
    feature_y_entry = tk.Entry(win, width=35)
    feature_y_entry.pack(pady=5)

    def run_report():
        feature_x = feature_x_entry.get().strip()
        feature_y = feature_y_entry.get().strip()

        if not feature_x or not feature_y:
            messagebox.showerror("Error", "Please enter both features.")
            return

        query = """
            SELECT DISTINCT
                r1.username,
                DATE(r1.created_at) AS posted_date,
                r1.rental_id AS rental_with_feature_x,
                r2.rental_id AS rental_with_feature_y
            FROM rental_unit r1
            JOIN rental_feature f1 ON r1.rental_id = f1.rental_id
            JOIN rental_unit r2 ON r1.username = r2.username
            JOIN rental_feature f2 ON r2.rental_id = f2.rental_id
            WHERE r1.rental_id <> r2.rental_id
              AND DATE(r1.created_at) = DATE(r2.created_at)
              AND f1.feature = %s
              AND f2.feature = %s
            ORDER BY r1.username, posted_date
        """

        columns, rows = fetch_all(query, (feature_x, feature_y))
        create_results_window(
            f"Phase 3 Report 2 - Users with {feature_x} and {feature_y}",
            columns,
            rows,
        )

    tk.Button(win, text="Run Report", width=20, command=run_report).pack(pady=15)


def show_phase3_report_3_form():
    win = tk.Toplevel(root)
    win.title("Phase 3 Report 3")
    win.geometry("520x220")
    win.resizable(False, False)

    tk.Label(
        win,
        text="Rentals by User with Only Excellent/Good Reviews",
        font=("Arial", 14, "bold"),
    ).pack(pady=15)

    tk.Label(win, text="Username X:").pack()
    username_entry = tk.Entry(win, width=35)
    username_entry.pack(pady=5)

    def run_report():
        username = username_entry.get().strip()

        if not username:
            messagebox.showerror("Error", "Please enter a username.")
            return

        query = """
            SELECT
                r.rental_id,
                r.title,
                r.description,
                r.price,
                r.username AS posted_by,
                DATE(r.created_at) AS posted_date
            FROM rental_unit r
            WHERE r.username = %s
              AND EXISTS (
                  SELECT 1
                  FROM review rev
                  WHERE rev.rental_id = r.rental_id
              )
              AND NOT EXISTS (
                  SELECT 1
                  FROM review rev
                  WHERE rev.rental_id = r.rental_id
                    AND rev.score NOT IN ('Excellent', 'Good')
              )
            ORDER BY r.rental_id
        """

        columns, rows = fetch_all(query, (username,))
        create_results_window(
            f"Phase 3 Report 3 - Excellent/Good Rentals by {username}",
            columns,
            rows,
        )

    tk.Button(win, text="Run Report", width=20, command=run_report).pack(pady=15)


def show_phase3_report_4_form():
    win = tk.Toplevel(root)
    win.title("Phase 3 Report 4")
    win.geometry("520x230")
    win.resizable(False, False)

    tk.Label(
        win,
        text="Users Who Posted the Most Rentals on a Date",
        font=("Arial", 14, "bold"),
    ).pack(pady=15)

    tk.Label(win, text="Date, format YYYY-MM-DD, e.g. 2025-10-15:").pack()
    date_entry = tk.Entry(win, width=35)
    date_entry.pack(pady=5)

    def run_report():
        selected_date = date_entry.get().strip()

        if not selected_date:
            messagebox.showerror("Error", "Please enter a date.")
            return

        query = """
            SELECT
                username,
                COUNT(*) AS rental_count
            FROM rental_unit
            WHERE DATE(created_at) = %s
            GROUP BY username
            HAVING COUNT(*) = (
                SELECT MAX(user_count)
                FROM (
                    SELECT COUNT(*) AS user_count
                    FROM rental_unit
                    WHERE DATE(created_at) = %s
                    GROUP BY username
                ) AS counts
            )
            ORDER BY username
        """

        columns, rows = fetch_all(query, (selected_date, selected_date))
        create_results_window(
            f"Phase 3 Report 4 - Most Rentals on {selected_date}",
            columns,
            rows,
        )

    tk.Button(win, text="Run Report", width=20, command=run_report).pack(pady=15)


def phase3_report_5():
    """
    Display all users who posted some reviews, but each review is Poor.
    """

    query = """
        SELECT
            username,
            COUNT(*) AS poor_review_count
        FROM review
        GROUP BY username
        HAVING COUNT(*) > 0
           AND SUM(CASE WHEN score <> 'Poor' THEN 1 ELSE 0 END) = 0
        ORDER BY username
    """

    columns, rows = fetch_all(query)
    create_results_window(
        "Phase 3 Report 5 - Users Whose Reviews Are All Poor", columns, rows
    )


def phase3_report_6():
    """
    Display users who posted rentals, and none of their rentals has received Poor reviews.
    Rentals with no reviews are allowed.
    """

    query = """
        SELECT
            r.username,
            COUNT(DISTINCT r.rental_id) AS rental_count
        FROM rental_unit r
        WHERE NOT EXISTS (
            SELECT 1
            FROM rental_unit r2
            JOIN review rev ON r2.rental_id = rev.rental_id
            WHERE r2.username = r.username
              AND rev.score = 'Poor'
        )
        GROUP BY r.username
        HAVING COUNT(DISTINCT r.rental_id) > 0
        ORDER BY r.username
    """

    columns, rows = fetch_all(query)
    create_results_window(
        "Phase 3 Report 6 - Users Whose Rentals Never Received Poor Reviews",
        columns,
        rows,
    )


# ---------------------------------------------------------
# App start
# ---------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    initialize_database()
    show_login_window()

    root.mainloop()
