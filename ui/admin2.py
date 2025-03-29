import customtkinter as ctk
from tkinter import ttk, messagebox

# ---------------- Initialize Application ----------------
ctk.set_appearance_mode("light")  # Options: "dark", "light", "system"
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("User Management System")
app.geometry("900x500")
app.resizable(False, False)

# ---------------- Main Container ----------------
container = ctk.CTkFrame(app, fg_color="white", corner_radius=10)
container.place(relx=0.5, rely=0.5, anchor="center")

# ---------------- Sidebar (Blue Admin Panel) ----------------
sidebar = ctk.CTkFrame(container, width=180, height=420, fg_color="#2563eb", corner_radius=0)
sidebar.pack(side="left", fill="y")

# Sidebar Title
title_label = ctk.CTkLabel(sidebar, text="Admin Panel", font=("Arial", 16, "bold"), text_color="white")
title_label.pack(pady=20)

# Sidebar Buttons
menu_items = ["Manage Inventory", "Manage Users", "Generate Report", "Logout"]

def menu_click(item):
    messagebox.showinfo("Navigation", f"You clicked: {item}")

for item in menu_items:
    btn = ctk.CTkButton(sidebar, text=item, fg_color="transparent", text_color="white",
                        corner_radius=5, hover_color="#1d4ed8",
                        command=lambda i=item: menu_click(i))
    btn.pack(fill="x", pady=5, padx=10)

# ---------------- Main Content ----------------
main_frame = ctk.CTkFrame(container, fg_color="white")
main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

# Header
header_label = ctk.CTkLabel(main_frame, text="User Management", font=("Arial", 18, "bold"), text_color="black")
header_label.pack(anchor="w", pady=5)

# ---------------- Add New User Section ----------------
add_user_frame = ctk.CTkFrame(main_frame, fg_color="white", border_width=1, corner_radius=5)
add_user_frame.pack(fill="x", pady=10, padx=5, ipadx=5, ipady=10)

ctk.CTkLabel(add_user_frame, text="Add New User", font=("Arial", 13, "bold"), text_color="black").pack(anchor="w", padx=10)

# Custom placeholder behavior for entries
def on_entry_click(entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, "end")
        entry.configure(text_color="black")

def on_focus_out(entry, placeholder):
    if not entry.get():
        entry.insert(0, placeholder)
        entry.configure(text_color="gray")

# Input Fields
placeholders = ["Full Name", "Email", "User Role"]
entries = []

for placeholder in placeholders:
    entry = ctk.CTkEntry(add_user_frame, width=300)
    entry.insert(0, placeholder)
    entry.configure(text_color="gray")
    entry.bind("<FocusIn>", lambda e, ent=entry, ph=placeholder: on_entry_click(ent, ph))
    entry.bind("<FocusOut>", lambda e, ent=entry, ph=placeholder: on_focus_out(ent, ph))
    entry.pack(fill="x", padx=10, pady=5, ipady=3)
    entries.append(entry)

# Function to add user
def add_user():
    name, email, role = [entry.get() for entry in entries]
    if name in placeholders or email in placeholders or role in placeholders:
        messagebox.showwarning("Input Error", "Please fill out all fields.")
        return
    
    tree.insert("", "end", values=(name, email, role))
    messagebox.showinfo("Success", "User added successfully!")

# Add User Button
add_user_btn = ctk.CTkButton(add_user_frame, text="Add User", font=("Arial", 12, "bold"), fg_color="#16a34a",
                             hover_color="#15803d", command=add_user)
add_user_btn.pack(pady=10, padx=10, ipadx=10)

# ---------------- Existing Users Section ----------------
users_frame = ctk.CTkFrame(main_frame, fg_color="white")
users_frame.pack(fill="x", pady=10)

ctk.CTkLabel(users_frame, text="Existing Users", font=("Arial", 13, "bold"), text_color="black").pack(anchor="w", padx=10)

# Users Table
table_frame = ctk.CTkFrame(users_frame, fg_color="white", border_width=1, corner_radius=5)
table_frame.pack(fill="both", pady=5, padx=5, expand=True)

columns = ("Name", "Email", "Role")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=3)

# Define column headings
tree.heading("Name", text="Name")
tree.heading("Email", text="Email")
tree.heading("Role", text="Role")

# Define column widths
tree.column("Name", width=200, anchor="w")
tree.column("Email", width=200, anchor="w")
tree.column("Role", width=100, anchor="center")

# Insert dummy data
data = [
    ("John Doe", "johndoe@example.com", "Admin"),
    ("Jane Smith", "janesmith@example.com", "Customer")
]

for user in data:
    tree.insert("", "end", values=user)

# Scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

tree.pack(fill="x")

# ---------------- Run Application ----------------
app.mainloop()
