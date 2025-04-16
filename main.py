import customtkinter as ctk
import subprocess
import sys
from tkinter import messagebox
import os

from config import APP_TITLE, APP_VERSION
from utils import initialize_system, read_login_file

# ------------------- Main Application ----------------
class SuperMarketApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Configure appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text=APP_TITLE, 
                                 font=("Arial", 24, "bold"))
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(main_frame, text="Choose an option to proceed:", 
                                    font=("Arial", 14))
        subtitle_label.pack(pady=10)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        # Login button
        login_btn = ctk.CTkButton(buttons_frame, text="Login", width=200, height=40,
                                fg_color="#2563eb", hover_color="#1d4ed8",
                                command=self.open_login)
        login_btn.pack(pady=10)
        
        # Sign Up button
        signup_btn = ctk.CTkButton(buttons_frame, text="Sign Up", width=200, height=40,
                                 fg_color="#10b981", hover_color="#059669",
                                 command=self.open_signup)
        signup_btn.pack(pady=10)
        
        # Admin button
        admin_btn = ctk.CTkButton(buttons_frame, text="Admin Panel", width=200, height=40,
                                fg_color="#6366f1", hover_color="#4f46e5",
                                command=self.open_admin_login)
        admin_btn.pack(pady=10)
        
        # Exit button
        exit_btn = ctk.CTkButton(buttons_frame, text="Exit", width=200, height=40,
                               fg_color="#ef4444", hover_color="#dc2626",
                               command=self.root.destroy)
        exit_btn.pack(pady=10)
        
        # Version label
        version_label = ctk.CTkLabel(main_frame, text=f"Version {APP_VERSION}", 
                                   font=("Arial", 10), text_color="gray")
        version_label.pack(side="bottom", pady=10)
    
    def open_login(self):
        self.root.withdraw()  # Hide main window
        try:
            result = subprocess.run(["python", "custom/login.py"], check=True)
            # Wait for a moment to see if login was successful
            if os.path.exists("current_user.txt"):
                username, role = read_login_file()
                if username and role:
                    if role == "admin":
                        self.open_admin(username)
                    else:
                        self.open_home(username)
                    return
        except Exception as e:
            print(f"Error opening login window: {e}")
        
        # If we get here, login was not successful or window was closed
        # self.root.deiconify()  # Show main window again
    
    def open_signup(self):
        self.root.withdraw()  # Hide main window
        try:
            result = subprocess.run(["python", "custom/signup.py"], check=True)
        except Exception as e:
            print(f"Error opening signup window: {e}")
        
        # self.root.deiconify()  # Show main window again
    
    def open_admin_login(self):
        """Open admin login window instead of directly opening admin panel"""
        self.root.withdraw()  # Hide main window
        try:
            result = subprocess.run(["python", "custom/admin_login.py"], check=True)
        except Exception as e:
            print(f"Error opening admin login window: {e}")
        
        # self.root.deiconify()  # Show main window again
    
    def open_admin(self, username=None):
        """This is only called after successful admin login"""
        self.root.withdraw()  # Hide main window
        
        result = subprocess.run(["python", "custom/admin.py", username], check=True)
           
        
        # self.root.deiconify()  # Show main window again
    
    def open_home(self, username):
        self.root.withdraw()  # Hide main window
        try:
            result = subprocess.run(["python", "custom/home.py", username], check=True)
        except Exception as e:
            print(f"Error opening home window: {e}")
        
        # self.root.deiconify()  # Show main window again

# ------------------- Main Function ----------------
def main():
    # Initialize the system
    if not initialize_system():
        sys.exit(1)
    
    # Start the main application
    print("Starting SuperMarket Management System...")
    root = ctk.CTk()
    app = SuperMarketApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()