import customtkinter as ctk
from tkinter import messagebox

# ---------------- Initialize Application ----------------
ctk.set_appearance_mode("light")  # Can be "dark", "light", or "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

app = ctk.CTk()
app.title("SuperMarket - Checkout")
app.geometry("900x500")
app.resizable(False, False)

# ---------------- Sidebar (Navigation Menu) ----------------
sidebar = ctk.CTkFrame(app, width=180, height=500, corner_radius=0, fg_color="#2563eb")
sidebar.pack(side="left", fill="y")

# Sidebar Title
title_label = ctk.CTkLabel(sidebar, text="SuperMarket", font=("Arial", 18, "bold"), text_color="white")
title_label.pack(pady=20)

# Sidebar Buttons
menu_items = ["Home", "Cart", "Previous Orders", "Logout"]

def menu_click(item):
    messagebox.showinfo("Navigation", f"You clicked: {item}")

for item in menu_items:
    btn = ctk.CTkButton(sidebar, text=item, fg_color="transparent", text_color="white",
                        corner_radius=5, hover_color="#1d4ed8",
                        command=lambda i=item: menu_click(i))
    btn.pack(fill="x", pady=5, padx=10)

# ---------------- Main Content ----------------
main_frame = ctk.CTkFrame(app, fg_color="white")
main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

# Header
header_frame = ctk.CTkFrame(main_frame, fg_color="white")
header_frame.pack(fill="x")

header_label = ctk.CTkLabel(header_frame, text="Checkout", font=("Arial", 18, "bold"), text_color="#2563eb")
header_label.pack(side="left", pady=10)

# Search Bar with Refresh Icon
search_frame = ctk.CTkFrame(header_frame, fg_color="white")
search_frame.pack(side="right")

refresh_icon = ctk.CTkButton(search_frame, text="🔄", font=("Arial", 12), fg_color="#e0e0e0",
                             corner_radius=5, width=30, hover_color="#d4d4d4")
refresh_icon.pack(side="left", padx=5)

search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search...", width=150)
search_entry.pack(side="left", padx=5)

# ---------------- Cart Items Section ----------------
cart_section = ctk.CTkFrame(main_frame, fg_color="white")
cart_section.pack(fill="x", pady=10)

cart_label = ctk.CTkLabel(cart_section, text="Your Cart Items", font=("Arial", 14, "bold"), text_color="black")
cart_label.pack(anchor="w", pady=5)

cart_frame = ctk.CTkFrame(cart_section, fg_color="white", border_width=1, corner_radius=5)
cart_frame.pack(fill="x", pady=5)

cart_items = [
    {"name": "Fresh Apples", "price": "$2.00"},
    {"name": "Organic Bananas", "price": "$1.50"},
    {"name": "Fresh Broccoli", "price": "$1.80"}
]

# Display Cart Items
for item in cart_items:
    item_row = ctk.CTkFrame(cart_frame, fg_color="white")
    item_row.pack(fill="x", padx=10, pady=3)

    ctk.CTkLabel(item_row, text=item["name"], font=("Arial", 12), text_color="black").pack(side="left")
    ctk.CTkLabel(item_row, text=item["price"], font=("Arial", 12), text_color="black").pack(side="right")

# Total Row
total_row = ctk.CTkFrame(cart_frame, fg_color="white")
total_row.pack(fill="x", padx=10, pady=8)

ctk.CTkLabel(total_row, text="Total:", font=("Arial", 12, "bold"), text_color="black").pack(side="left")
ctk.CTkLabel(total_row, text="$5.30", font=("Arial", 12, "bold"), text_color="black").pack(side="right")

# ---------------- Buttons (Edit & Delete) ----------------
buttons_section = ctk.CTkFrame(main_frame, fg_color="white")
buttons_section.pack(fill="x", pady=20)

edit_button = ctk.CTkButton(buttons_section, text="Edit", font=("Arial", 12, "bold"), fg_color="#f97316",
                            hover_color="#ea580c", width=100)
edit_button.pack(side="left", padx=20)

delete_button = ctk.CTkButton(buttons_section, text="Delete", font=("Arial", 12, "bold"), fg_color="#dc2626",
                              hover_color="#b91c1c", width=100)
delete_button.pack(side="right", padx=20)

# ---------------- Run Application ----------------
app.mainloop()
