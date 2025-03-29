import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import messagebox

# ---------------- Initialize Application ----------------
ctk.set_appearance_mode("light")  # Can be "dark", "light", or "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

app = ctk.CTk()
app.title("SuperMarket Dashboard")
app.geometry("900x600")
app.resizable(False, False)

# ---------------- Sidebar (Navigation Menu) ----------------
sidebar = ctk.CTkFrame(app, width=180, height=600, corner_radius=0, fg_color="#2563eb")
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
header_label = ctk.CTkLabel(main_frame, text="Welcome to the SuperMarket",
                            font=("Arial", 18, "bold"), text_color="black")
header_label.pack(anchor="w", pady=10)

# ---------------- Available Items Section ----------------
items_section = ctk.CTkFrame(main_frame, fg_color="white")
items_section.pack(fill="x", pady=10)

items_label = ctk.CTkLabel(items_section, text="Available Items", font=("Arial", 14, "bold"), text_color="black")
items_label.pack(anchor="w", pady=5)

items_frame = ctk.CTkFrame(items_section, fg_color="white")
items_frame.pack(fill="x", pady=10)

# Product Details
products = [
    {"name": "Fresh Apples", "price": "$2.00", "image": "apple.png"},
    {"name": "Organic Bananas", "price": "$1.50", "image": "banana.png"},
    {"name": "Fresh Broccoli", "price": "$1.80", "image": "broccoli.png"}
]

# Displaying Items
for product in products:
    item_card = ctk.CTkFrame(items_frame, fg_color="white", border_width=1, corner_radius=10)
    item_card.pack(side="left", padx=10, pady=5)

    try:
        img = Image.open(product["image"])
        img = img.resize((100, 100), Image.Resampling.LANCZOS)
        product_img = ImageTk.PhotoImage(img)
        img_label = ctk.CTkLabel(item_card, image=product_img, text="")
        img_label.image = product_img  # Keep reference
        img_label.pack(pady=5)
    except:
        ctk.CTkLabel(item_card, text="[No Image]", font=("Arial", 12)).pack(pady=5)

    ctk.CTkLabel(item_card, text=product["name"], font=("Arial", 12, "bold"), text_color="black").pack()
    ctk.CTkLabel(item_card, text=product["price"], font=("Arial", 12), text_color="gray").pack()

    add_cart_btn = ctk.CTkButton(item_card, text="Add to Cart", fg_color="#2563eb",
                                 hover_color="#1d4ed8", width=100)
    add_cart_btn.pack(pady=10)

# ---------------- Checkout Section ----------------
checkout_section = ctk.CTkFrame(main_frame, fg_color="white")
checkout_section.pack(fill="x", pady=10)

checkout_label = ctk.CTkLabel(checkout_section, text="Checkout", font=("Arial", 14, "bold"), text_color="black")
checkout_label.pack(anchor="w", pady=5)

checkout_btn = ctk.CTkButton(checkout_section, text="Proceed to Checkout", fg_color="#16a34a",
                             hover_color="#15803d", width=200)
checkout_btn.pack(pady=10)

# ---------------- Previous Orders Section ----------------
orders_section = ctk.CTkFrame(main_frame, fg_color="white")
orders_section.pack(fill="x", pady=10)

orders_label = ctk.CTkLabel(orders_section, text="Previous Orders", font=("Arial", 14, "bold"), text_color="black")
orders_label.pack(anchor="w", pady=5)

orders_frame = ctk.CTkFrame(orders_section, fg_color="white")
orders_frame.pack(fill="x", pady=5)

orders = [
    {"name": "Order #1", "price": "$15.00"},
    {"name": "Order #2", "price": "$20.00"},
    {"name": "Order #3", "price": "$10.00"}
]

for order in orders:
    order_row = ctk.CTkFrame(orders_frame, fg_color="white")
    order_row.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(order_row, text=order["name"], font=("Arial", 12), text_color="black").pack(side="left")
    ctk.CTkLabel(order_row, text=order["price"], font=("Arial", 12, "bold"), text_color="black").pack(side="right")

# ---------------- Run Application ----------------
app.mainloop()
