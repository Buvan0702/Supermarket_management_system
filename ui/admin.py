import customtkinter as ctk
from tkinter import ttk, messagebox

# ---------------- Initialize Application ----------------
ctk.set_appearance_mode("light")  # Options: "dark", "light", "system"
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Inventory Management System")
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
header_label = ctk.CTkLabel(main_frame, text="Inventory Management", font=("Arial", 18, "bold"), text_color="#2563eb")
header_label.pack(anchor="w", pady=5)

# ---------------- Add New Item Section ----------------
add_item_frame = ctk.CTkFrame(main_frame, fg_color="white", border_width=1, corner_radius=5)
add_item_frame.pack(fill="x", pady=10, padx=5, ipadx=5, ipady=10)

ctk.CTkLabel(add_item_frame, text="Add New Item", font=("Arial", 13, "bold"), text_color="black").pack(anchor="w", padx=10)

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
placeholders = ["Item Name", "Price ($)", "Stock Quantity"]
entries = []

for placeholder in placeholders:
    entry = ctk.CTkEntry(add_item_frame, width=300)
    entry.insert(0, placeholder)
    entry.configure(text_color="gray")
    entry.bind("<FocusIn>", lambda e, ent=entry, ph=placeholder: on_entry_click(ent, ph))
    entry.bind("<FocusOut>", lambda e, ent=entry, ph=placeholder: on_focus_out(ent, ph))
    entry.pack(fill="x", padx=10, pady=5, ipady=3)
    entries.append(entry)

# Function to add item
def add_item():
    item_name, price, stock = [entry.get() for entry in entries]
    if item_name in placeholders or price in placeholders or stock in placeholders:
        messagebox.showwarning("Input Error", "Please fill out all fields.")
        return
    
    tree.insert("", "end", values=(item_name, f"${price}", stock, "Edit | Delete"))
    messagebox.showinfo("Success", "Item added successfully!")

# Add Item Button
add_item_btn = ctk.CTkButton(add_item_frame, text="Add Item", font=("Arial", 12, "bold"), fg_color="#16a34a",
                             hover_color="#15803d", command=add_item)
add_item_btn.pack(pady=10, padx=10, ipadx=10)

# ---------------- Existing Inventory Section ----------------
inventory_frame = ctk.CTkFrame(main_frame, fg_color="white")
inventory_frame.pack(fill="x", pady=10)

ctk.CTkLabel(inventory_frame, text="Existing Inventory", font=("Arial", 13, "bold"), text_color="black").pack(anchor="w", padx=10)

# Inventory Table
table_frame = ctk.CTkFrame(inventory_frame, fg_color="white", border_width=1, corner_radius=5)
table_frame.pack(fill="both", pady=5, padx=5, expand=True)

columns = ("Item Name", "Price", "Stock", "Actions")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=3)

# Define column headings
tree.heading("Item Name", text="Item Name")
tree.heading("Price", text="Price ($)")
tree.heading("Stock", text="Stock Quantity")
tree.heading("Actions", text="Actions")

# Define column widths
tree.column("Item Name", width=200, anchor="w")
tree.column("Price", width=100, anchor="center")
tree.column("Stock", width=100, anchor="center")
tree.column("Actions", width=200, anchor="center")

# Insert dummy data
data = [
    ("Fresh Apples", "$2.00", "50", "Edit | Delete"),
    ("Organic Bananas", "$1.50", "30", "Edit | Delete")
]

for item in data:
    tree.insert("", "end", values=item)

# Scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

tree.pack(fill="x")

# ---------------- Run Application ----------------
app.mainloop()
