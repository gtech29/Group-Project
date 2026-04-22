import tkinter as tk
from tkinter import messagebox
import hashlib
import mysql.connector
import os
from dotenv import load_dotenv
from mysql.connector import errorcode

# load the .env file
load_dotenv()

# retrieve username and password
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")

# track current user
current_user = None


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


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


# Signup
def handle_signup():
    username = su_username_entry.get().strip()
    password = su_password_entry.get().strip()
    confirm = su_confirm_entry.get().strip()
    firstName = su_firstname_entry.get().strip()
    lastName = su_lastname_entry.get().strip()
    email = su_email_entry.get().strip()
    phone = su_phone_entry.get().strip()

    if not all([username, password, confirm, firstName, lastName, email, phone]):
        messagebox.showerror("Signup Error", "All fields are required")
        return

    if password != confirm:
        messagebox.showerror("Signup Error", "Passwords do not match")
        return

    cnx = get_db_connection()
    if not cnx:
        return

    cursor = cnx.cursor()

    # Check for duplicates
    cursor.execute(
        "SELECT * FROM user WHERE username=%s OR email=%s OR phone=%s",
        (username, email, phone),
    )
    if cursor.fetchone():
        messagebox.showerror("Signup Error", "Username, email, or phone already exists")
        cursor.close()
        cnx.close()
        return

    # Add new user with hashed password
    hashed_pw = hash_password(password)
    cursor.execute(
        """
        INSERT INTO user (username, password, firstName, lastName, email, phone)
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
        (username, hashed_pw, firstName, lastName, email, phone),
    )
    cnx.commit()
    cursor.close()
    cnx.close()
    messagebox.showinfo("Signup", "Account created successfully!")
    signup_win.destroy()  # close signup window
    open_login_window()


def open_signup_window():
    global signup_win
    global su_username_entry, su_password_entry, su_confirm_entry
    global su_firstname_entry, su_lastname_entry, su_email_entry, su_phone_entry

    signup_win = tk.Toplevel(root)
    signup_win.title("Signup")
    signup_win.geometry("400x400")
    signup_win.resizable(False, False)

    tk.Label(signup_win, text="Signup Page", font=("Arial", 18, "bold")).pack(pady=10)

    tk.Label(signup_win, text="Username:").pack()
    su_username_entry = tk.Entry(signup_win, width=30)
    su_username_entry.pack()

    tk.Label(signup_win, text="Password:").pack()
    su_password_entry = tk.Entry(signup_win, width=30, show="*")
    su_password_entry.pack()

    tk.Label(signup_win, text="Confirm Password:").pack()
    su_confirm_entry = tk.Entry(signup_win, width=30, show="*")
    su_confirm_entry.pack()

    tk.Label(signup_win, text="First Name:").pack()
    su_firstname_entry = tk.Entry(signup_win, width=30)
    su_firstname_entry.pack()

    tk.Label(signup_win, text="Last Name:").pack()
    su_lastname_entry = tk.Entry(signup_win, width=30)
    su_lastname_entry.pack()

    tk.Label(signup_win, text="Email:").pack()
    su_email_entry = tk.Entry(signup_win, width=30)
    su_email_entry.pack()

    tk.Label(signup_win, text="Phone:").pack()
    su_phone_entry = tk.Entry(signup_win, width=30)
    su_phone_entry.pack()

    tk.Button(signup_win, text="Signup", width=18, command=handle_signup).pack(pady=20)

    link = tk.Label(signup_win, text="Already have an account? Login",
                fg="blue", cursor="hand2")
os.link.pack()

link.bind("<Button-1>", lambda e: [signup_win.destroy(), open_login_window()])


# Login
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
    query = "SELECT password FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    if result:
        stored_hash = result[0]
        entered_hash = hash_password(password)
        if entered_hash == stored_hash:
            current_user = username  # Set the current user
            messagebox.showinfo("Login", f"Welcome {username}!")
            open_dashboard_window()
        else:
            messagebox.showerror("Login Error", "Incorrect password")
    else:
        messagebox.showerror("Login Error", "User not found")


def open_login_window():
    global username_entry, password_entry
    root.deiconify()
    root.title("Login")
    root.geometry("400x250")
    root.resizable(False, False)

    tk.Label(root, text="Login Page", font=("Arial", 18, "bold")).pack(pady=20)

    tk.Label(root, text="Username:").pack(pady=(5, 0))
    username_entry = tk.Entry(root, width=30)
    username_entry.pack(pady=5)

    tk.Label(root, text="Password:").pack(pady=(5, 0))
    password_entry = tk.Entry(root, width=30, show="*")
    password_entry.pack(pady=5)

    tk.Button(root, text="Login", width=18, command=handle_login).pack(pady=20)

    tk.Button(root, text="Don't have an account? Sign up",
          command=lambda: [root.withdraw(), open_signup_window()]
).pack()

def handle_insert_rental():
        global current_user

        title = rental_title.get().strip()
        description = rental_description.get().strip()
        feature = rental_feature.get().strip()
        price = rental_price.get().strip()

        # Validate inputs
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
                INSERT INTO rental_unit (title, description, feature, price, username)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (title, description, feature, price, current_user),
            )
            cnx.commit()
            messagebox.showinfo("Success", "Rental added successfully!")

            # Clear fields after insert
            rental_title.delete(0, tk.END)
            rental_description.delete(0, tk.END)
            rental_feature.delete(0, tk.END)
            rental_price.delete(0, tk.END)

        except mysql.connector.Error as err:
            messagebox.showerror("DB Error", str(err))

        finally:
            cursor.close()
            cnx.close()

def open_dashboard_window():
    global rental_title, rental_description, rental_feature, rental_price

    # Create a brand new window on top of the root
    dashboard_win = tk.Toplevel(root)
    dashboard_win.title("Rental Dashboard")
    dashboard_win.geometry("300x350")

    tk.Label(dashboard_win, text="Enter Rental Info", font=("Arial", 18, "bold")).pack(pady=20)
    
    tk.Label(dashboard_win, text="Title").pack()
    rental_title = tk.Entry(dashboard_win, width=30)
    rental_title.pack(pady=5)

    tk.Label(dashboard_win, text="Description").pack()
    rental_description = tk.Entry(dashboard_win, width=30)
    rental_description.pack(pady=5)

    tk.Label(dashboard_win, text="Feature").pack()
    rental_feature = tk.Entry(dashboard_win, width=30)
    rental_feature.pack(pady=5)

    tk.Label(dashboard_win, text="Price").pack()
    rental_price = tk.Entry(dashboard_win, width=30)
    rental_price.pack(pady=5)
    
    tk.Button(dashboard_win, text="Submit", command=handle_insert_rental).pack(pady=20)


root = tk.Tk()
root.withdraw()

open_signup_window()  # Signup opens first


root.mainloop()


