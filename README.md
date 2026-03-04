# **Group Project - COMP 440 Database Design**

## **Overview**

This login and user registration interface is intended to be a secure system that only allows a registered user to login into the system.

---

## **Key Features**

- **User Registration**: New accounts and usernames and passwords should be unique.
- **Secure Login**: Login using a registered username and password.
- **Data Validation**: Checks that authorized users provide correct data when registering and logging in.
- **Password Encryption**: Encrypts passwords using hashed algorithms and then stores them in the database.
- **Interactive GUI**: A clean and well-organised user-friendly graphical user interface (GUI).
- **Error Handling**: Deals with bad input, duplicate applications and system errors gracefully.

---

## **Technologies Used**

- **Python**: Main programming language used for logic and GUI.
- **MySQL**: Relational database used for user data storage.

---

## **Folder Structure**

```text
Group-Project-COMP440  
├── 📄 main.py              # Main Python script with login, registration, and GUI logic  
├── 📄 database.sql         # SQL file to create the necessary tables 
├── 📄 requirements.txt     # Required libraries for the project  
└── 📄 README.md            # Project documentation (this file)  
```

---

## **Screenshots**

> TBD

---

## **Installation and Setup**

To install the repository in your system, do the following.

---

### **Clone the Repository**

```bash
git clone https://github.com/gtech29/Group-Project-COMP440.git
cd Group-Project-COMP440
```

---

### **Create a Virtual Environment (Optional but Recommended)**

```bash
python -m venv venv
source venv/bin/activate  # For Linux/MacOS
venv\Scripts\activate     # For Windows
```

---

### **Install Required Libraries**

Install all the dependencies listed in `requirements.txt` using:

```bash
pip install -r requirements.txt
```

ensure you have the right interpreter (virtual environment)

---

## **License**

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.
