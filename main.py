import tkinter as tk
from tkinter import messagebox
import hashlib
import mysql.connector
import os
import re
from dotenv import load_dotenv
from mysql.connector import errorcode, IntegrityError

# load the .env file
load_dotenv()

# retrieve database username and password
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")

# track current user
current_user = None


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def is_valid_email(email):
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(com|edu)$'
    return re.fullmatch(pattern, email) is not None


def is_valid_phone(phone):
    pattern = r'^\d{10}$'
    return re.fullmatch(pattern, phone) is not None


def get_db_connection():
    try:
        cnx = mysql.connector.connect(
            user=db_username,
            password=db_password,
            host="localhost",
            database="login_system",
        )
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            messagebox.showerror("DB Error", "Wrong username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            messagebox.showerror("DB Error", "Database does not exist")
        else:
            messagebox.showerror("DB Error", str(err))
        return None


# -------------------------
# Signup
# -------------------------
def open_signup_window():
    signup_window = tk.Toplevel(root)
    signup_window.title("Sign Up")
    signup_window.geometry("460x560")
    signup_window.resizable(False, False)

    tk.Label(
        signup_window,
        text="Create Account",
        font=("Arial", 20)
    ).pack(pady=18)

    tk.Label(signup_window, text="Username:", font=("Arial", 11)).pack()
    signup_username = tk.Entry(signup_window, width=34, font=("Arial", 11))
    signup_username.pack(pady=6)

    tk.Label(signup_window, text="Password:", font=("Arial", 11)).pack()
    signup_password = tk.Entry(signup_window, width=34, font=("Arial", 11), show="*")
    signup_password.pack(pady=6)

    tk.Label(signup_window, text="Confirm Password:", font=("Arial", 11)).pack()
    signup_confirm_password = tk.Entry(signup_window, width=34, font=("Arial", 11), show="*")
    signup_confirm_password.pack(pady=6)

    tk.Label(signup_window, text="First Name:", font=("Arial", 11)).pack()
    signup_firstname = tk.Entry(signup_window, width=34, font=("Arial", 11))
    signup_firstname.pack(pady=6)

    tk.Label(signup_window, text="Last Name:", font=("Arial", 11)).pack()
    signup_lastname = tk.Entry(signup_window, width=34, font=("Arial", 11))
    signup_lastname.pack(pady=6)

    tk.Label(signup_window, text="Email:", font=("Arial", 11)).pack()
    signup_email = tk.Entry(signup_window, width=34, font=("Arial", 11))
    signup_email.pack(pady=6)

    tk.Label(signup_window, text="Phone:", font=("Arial", 11)).pack()
    signup_phone = tk.Entry(signup_window, width=34, font=("Arial", 11))
    signup_phone.pack(pady=6)

    def handle_signup():
        username = signup_username.get().strip()
        password = signup_password.get().strip()
        confirm_password = signup_confirm_password.get().strip()
        first_name = signup_firstname.get().strip()
        last_name = signup_lastname.get().strip()
        email = signup_email.get().strip()
        phone = signup_phone.get().strip()

        if not all([username, password, confirm_password, first_name, last_name, email, phone]):
            messagebox.showerror("Signup Error", "Please fill in all fields.")
            return

        if password != confirm_password:
            messagebox.showerror("Signup Error", "Passwords do not match.")
            return

        if not is_valid_email(email):
            messagebox.showerror("Signup Error", "Email must be valid and end with .com or .edu.")
            return

        if not is_valid_phone(phone):
            messagebox.showerror("Signup Error", "Phone number must be exactly 10 digits.")
            return

        cnx = get_db_connection()
        if not cnx:
            return

        cursor = cnx.cursor()
        hashed_pw = hash_password(password)

        try:
            insert_query = """
                INSERT INTO user (username, password, firstName, lastName, email, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                insert_query,
                (username, hashed_pw, first_name, last_name, email, phone)
            )
            cnx.commit()
            messagebox.showinfo("Signup Success", "Account created successfully.")
            signup_window.destroy()

        except IntegrityError as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                messagebox.showerror("Signup Error", "Username, email, or phone already exists.")
            else:
                messagebox.showerror("Signup Error", str(err))
        except mysql.connector.Error as err:
            messagebox.showerror("Signup Error", str(err))
        finally:
            cursor.close()
            cnx.close()

    signup_window.bind("<Return>", lambda event: handle_signup())

    tk.Button(
        signup_window,
        text="Create Account",
        width=22,
        height=2,
        font=("Arial", 12),
        command=handle_signup
    ).pack(pady=24)


# -------------------------
# Login
# -------------------------
def handle_login():
    global current_user

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showerror("Login Error", "Please fill in both fields.")
        return

    cnx = get_db_connection()
    if not cnx:
        return

    cursor = cnx.cursor()
    hashed_pw = hash_password(password)

    query = "SELECT username FROM user WHERE username = %s AND password = %s"
    cursor.execute(query, (username, hashed_pw))
    result = cursor.fetchone()

    cursor.close()
    cnx.close()

    if result:
        current_user = username
        messagebox.showinfo("Login Success", f"Welcome, {username}!")
        open_dashboard_window()
    else:
        messagebox.showerror("Login Error", "Invalid username or password.")


def open_login_window():
    global username_entry, password_entry

    root.deiconify()
    root.title("Login")
    root.geometry("400x320")
    root.resizable(False, False)

    tk.Label(root, text="Login Page", font=("Arial", 20)).pack(pady=22)

    tk.Label(root, text="Username:", font=("Arial", 11)).pack(pady=(5, 0))
    username_entry = tk.Entry(root, width=34, font=("Arial", 11))
    username_entry.pack(pady=6)

    tk.Label(root, text="Password:", font=("Arial", 11)).pack(pady=(5, 0))
    password_entry = tk.Entry(root, width=34, font=("Arial", 11), show="*")
    password_entry.pack(pady=6)

    tk.Button(
        root, text="Login", width=18, height=2, font=("Arial", 11), command=handle_login
    ).pack(pady=(18, 10))

    tk.Button(
        root, text="Sign Up", width=18, height=2, font=("Arial", 11), command=open_signup_window
    ).pack()

    root.bind("<Return>", lambda event: handle_login())


# -------------------------
# Rental insert
# -------------------------
def handle_insert_rental():
    global current_user

    title = rental_title.get().strip()
    description = rental_description.get().strip()
    feature = rental_feature.get().strip()
    price = rental_price.get().strip()

    if not all([title, description, feature, price]):
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        price = float(price)
    except ValueError:
        messagebox.showerror("Error", "Price must be a number")
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
            AND created_at >= CURDATE()
            """,
            (current_user,),
        )

        count = cursor.fetchone()[0]

        if count >= 2:
            messagebox.showerror(
                "Limit reached",
                "You can only post 2 rentals per day."
            )
            return

        cursor.execute(
            """
            INSERT INTO rental_unit (title, description, feature, price, username)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (title, description, feature, price, current_user),
        )
        cnx.commit()
        messagebox.showinfo("Success", "Rental added successfully!")

        rental_title.delete(0, tk.END)
        rental_description.delete(0, tk.END)
        rental_feature.delete(0, tk.END)
        rental_price.delete(0, tk.END)

    except mysql.connector.Error as err:
        messagebox.showerror("DB Error", str(err))

    finally:
        cursor.close()
        cnx.close()


# -------------------------
# Search rentals
# -------------------------
def handle_search_rentals():
    global rental_results_data

    search_term = search_feature_entry.get().strip()

    if not search_term:
        messagebox.showerror("Search Error", "Please enter a feature to search.")
        return

    cnx = get_db_connection()
    if not cnx:
        return

    cursor = cnx.cursor()

    try:
        query = """
            SELECT rental_id, title, description, feature, price, username
            FROM rental_unit
            WHERE feature LIKE %s
        """
        cursor.execute(query, ("%" + search_term + "%",))
        results = cursor.fetchall()

        rental_results_data = results
        search_results_listbox.delete(0, tk.END)

        if not results:
            search_results_listbox.insert(tk.END, "No rentals found.")
            return

        for rental in results:
            rental_id, title, description, feature, price, username = rental
            display_text = (
                f"ID: {rental_id} | {title} | {description} | "
                f"Feature: {feature} | Price: ${price} | Posted by: {username}"
            )
            search_results_listbox.insert(tk.END, display_text)

    except mysql.connector.Error as err:
        messagebox.showerror("DB Error", str(err))

    finally:
        cursor.close()
        cnx.close()


def get_selected_rental():
    selected_index = search_results_listbox.curselection()

    if not selected_index:
        messagebox.showerror("Selection Error", "Please select a rental from the search results.")
        return None

    if not rental_results_data:
        messagebox.showerror("Selection Error", "No valid rental data found.")
        return None

    return rental_results_data[selected_index[0]]


# -------------------------
# Check reviews + leave review
# -------------------------
def handle_check_reviews():
    selected_rental = get_selected_rental()
    if not selected_rental:
        return

    rental_id, title, description, feature, price, rental_owner = selected_rental

    cnx = get_db_connection()
    if not cnx:
        return

    cursor = cnx.cursor()

    try:
        cursor.execute(
            """
            SELECT username, score, remark, created_at
            FROM review
            WHERE rental_id = %s
            ORDER BY created_at DESC
            """,
            (rental_id,),
        )
        reviews = cursor.fetchall()

        reviews_win = tk.Toplevel(root)
        reviews_win.title(f"Rental Details - {title}")
        reviews_win.geometry("800x650")

        tk.Label(
            reviews_win,
            text="Rental Details",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        tk.Label(reviews_win, text=f"Title: {title}", font=("Arial", 11)).pack(anchor="w", padx=20)
        tk.Label(reviews_win, text=f"Description: {description}", font=("Arial", 11)).pack(anchor="w", padx=20)
        tk.Label(reviews_win, text=f"Feature: {feature}", font=("Arial", 11)).pack(anchor="w", padx=20)
        tk.Label(reviews_win, text=f"Price: ${price}", font=("Arial", 11)).pack(anchor="w", padx=20)
        tk.Label(reviews_win, text=f"Posted by: {rental_owner}", font=("Arial", 11)).pack(anchor="w", padx=20, pady=(0, 10))

        tk.Label(
            reviews_win,
            text="Current Reviews",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        reviews_listbox = tk.Listbox(reviews_win, width=110, height=12)
        reviews_listbox.pack(pady=10)

        if not reviews:
            reviews_listbox.insert(tk.END, "No reviews yet for this rental.")
        else:
            for review in reviews:
                username, score, remark, created_at = review
                reviews_listbox.insert(
                    tk.END,
                    f"User: {username} | Score: {score} | Remark: {remark} | Date: {created_at}"
                )

        tk.Label(
            reviews_win,
            text="Leave a Review",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        if current_user == rental_owner:
            tk.Label(
                reviews_win,
                text="You cannot review your own rental.",
                fg="red",
                font=("Arial", 11)
            ).pack(pady=5)
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
            tk.Label(
                reviews_win,
                text="You have already reviewed this rental.",
                fg="red",
                font=("Arial", 11)
            ).pack(pady=5)
            return

        tk.Label(reviews_win, text="Score").pack()
        score_var = tk.StringVar(reviews_win)
        score_var.set("Excellent")
        tk.OptionMenu(reviews_win, score_var, "Excellent", "Good", "Fair", "Poor").pack(pady=5)

        tk.Label(reviews_win, text="Remark").pack()
        remark_entry = tk.Entry(reviews_win, width=50)
        remark_entry.pack(pady=5)

        def submit_review():
            score = score_var.get().strip()
            remark = remark_entry.get().strip()

            if not remark:
                messagebox.showerror("Review Error", "Please enter a remark.")
                return

            review_cnx = get_db_connection()
            if not review_cnx:
                return

            review_cursor = review_cnx.cursor()

            try:
                review_cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM review
                    WHERE username = %s
                    AND created_at >= CURDATE()
                    """,
                    (current_user,),
                )
                daily_count = review_cursor.fetchone()[0]

                if daily_count >= 3:
                    messagebox.showerror("Review Error", "You can only post 3 reviews per day.")
                    return

                review_cursor.execute(
                    """
                    INSERT INTO review (rental_id, username, score, remark)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (rental_id, current_user, score, remark),
                )
                review_cnx.commit()

                messagebox.showinfo("Success", "Review added successfully!")
                reviews_win.destroy()

            except mysql.connector.Error as err:
                messagebox.showerror("DB Error", str(err))

            finally:
                review_cursor.close()
                review_cnx.close()

        tk.Button(
            reviews_win,
            text="Submit Review",
            command=submit_review
        ).pack(pady=10)

    except mysql.connector.Error as err:
        messagebox.showerror("DB Error", str(err))

    finally:
        cursor.close()
        cnx.close()


# -------------------------
# Dashboard
# -------------------------
def open_dashboard_window():
    global rental_title, rental_description, rental_feature, rental_price
    global search_feature_entry, search_results_listbox, rental_results_data

    rental_results_data = []

    dashboard_win = tk.Toplevel(root)
    dashboard_win.title("Rental Dashboard")
    dashboard_win.geometry("800x700")

    tk.Label(
        dashboard_win, text="Enter Rental Info", font=("Arial", 18, "bold")
    ).pack(pady=10)

    tk.Label(dashboard_win, text="Title").pack()
    rental_title = tk.Entry(dashboard_win, width=40)
    rental_title.pack(pady=5)

    tk.Label(dashboard_win, text="Description").pack()
    rental_description = tk.Entry(dashboard_win, width=40)
    rental_description.pack(pady=5)

    tk.Label(dashboard_win, text="Feature").pack()
    rental_feature = tk.Entry(dashboard_win, width=40)
    rental_feature.pack(pady=5)

    tk.Label(dashboard_win, text="Price").pack()
    rental_price = tk.Entry(dashboard_win, width=40)
    rental_price.pack(pady=5)

    tk.Button(
        dashboard_win, text="Submit Rental", command=handle_insert_rental
    ).pack(pady=10)

    tk.Label(
        dashboard_win, text="Search Rentals by Feature", font=("Arial", 16, "bold")
    ).pack(pady=15)

    tk.Label(dashboard_win, text="Enter Feature").pack()
    search_feature_entry = tk.Entry(dashboard_win, width=40)
    search_feature_entry.pack(pady=5)

    tk.Button(
        dashboard_win, text="Search", command=handle_search_rentals
    ).pack(pady=10)

    search_results_listbox = tk.Listbox(dashboard_win, width=110, height=12)
    search_results_listbox.pack(pady=10)

    tk.Button(
        dashboard_win, text="Check Reviews", command=handle_check_reviews
    ).pack(pady=5)


root = tk.Tk()
root.withdraw()

open_login_window()

root.mainloop()