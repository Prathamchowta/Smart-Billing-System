import customtkinter as ctk
import json
import os
import time
import sqlite3
import pandas as pd
from tkinter import messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageTk
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import numpy as np
from sklearn.linear_model import LinearRegression

MENU = {
    "Coffee": 50,
    "Tea": 30,
    "Sandwich": 70,
    "Burger": 90,
    "Fries": 60,
    "Pizza": 120
}

TAX_RATE = 0.05
SERVICE_CHARGE = 20

DB_FILE = "bills/bills.db"
EXCEL_FILE = "bills/all_bills.xlsx"

class CafeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SMART BILLING SYSTEM")
        self.root.geometry("1400x900")  # Even wider for better layout
        self.entries = {}
        self.bill_pdf_path = None
        self.menu = MENU.copy()  # Use a copy so we can modify

        # --- Main layout: left (content) and right (analytics) ---
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.grid_columnconfigure(0, weight=7)  # Left 70%
        self.main_frame.grid_columnconfigure(1, weight=3)  # Right 30%
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Left: scrollable content
        self.content_container = ctk.CTkFrame(self.main_frame)
        self.content_container.grid(row=0, column=0, sticky="nsew")
        self.build_ui(parent=self.content_container)

        # Right: analytics panel
        self.analytics_panel = ctk.CTkFrame(self.main_frame, fg_color="#f5f6fa", corner_radius=18)
        self.analytics_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(self.analytics_panel, text="Order Analytics", font=("Arial", 20, "bold"), text_color="#222").pack(pady=10)
        self.analytics_controls_frame = ctk.CTkFrame(self.analytics_panel, fg_color=None)
        self.analytics_controls_frame.pack(pady=10)
        self.analytics_charts_frame = ctk.CTkFrame(self.analytics_panel, fg_color=None)
        self.analytics_charts_frame.pack(fill="both", expand=True)
        self.setup_analytics_controls()

        self.predict_profit_btn = ctk.CTkButton(self.analytics_panel, text="Predict Future Profit", command=self.display_analytics_profit_prediction, fg_color="#e67e22", text_color="#fff")
        self.predict_profit_btn.pack(pady=15, side="bottom")

        self.init_db()
        self.update_totals_labels()

        # Always-visible back arrow at top left (place last so it's on top)
        self.back_arrow_btn = ctk.CTkButton(self.root, text="←", width=32, height=32, font=("Arial", 18, "bold"), fg_color="transparent", text_color="#000", border_width=2, border_color="#000", corner_radius=16, command=self.go_back)
        self.back_arrow_btn.place(x=10, y=10)

        # Set initial pane sizes
        self.root.after(100, self.set_initial_pane_sizes)

    def set_initial_pane_sizes(self):
        # Set left:right ratio to about 2:1
        total = self.paned.winfo_width()
        if total > 0:
            self.paned.sash_place(0, int(total * 0.66), 0)

    def reset_pane_layout(self):
        self.set_initial_pane_sizes()

    def build_ui(self, parent=None):
        if parent is None:
            parent = self.root
        # Attractive color palette
        accent_color = "#1abc9c"  # teal
        heading_color = "#000000"  # black for headings
        label_color = "#eaf6fb"
        frame_bg = "#0e2233"
        entry_bg = "#eaf6fb"
        total_color = "#000000"  # black for total
        highlight_color = "#ffb347"  # bright orange for visibility

        # --- Scrollable Frame Setup ---
        self.main_canvas = ctk.CTkCanvas(parent, bg=None, highlightthickness=0)
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar = ctk.CTkScrollbar(parent, orientation="vertical", command=self.main_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = ctk.CTkFrame(self.main_canvas, fg_color=None)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

        # Main heading
        ctk.CTkLabel(self.scrollable_frame, text="SMART BILLING SYSTEM", font=("Arial", 28, "bold"), text_color=heading_color).pack(pady=10)

        # --- Today's Total Section ---
        self.todays_total_section = ctk.CTkFrame(self.scrollable_frame, fg_color=highlight_color, corner_radius=18)
        self.todays_total_section.pack(pady=(0, 15), padx=20, fill="x")
        ctk.CTkLabel(self.todays_total_section, text="Today's Total Amount", font=("Arial", 18, "bold"), text_color="#000").pack(pady=(8, 0))
        self.todays_total_big_label = ctk.CTkLabel(self.todays_total_section, text="₹0.00", font=("Arial", 24, "bold"), text_color="#222")
        self.todays_total_big_label.pack(pady=(0, 8))

        # Customer name
        ctk.CTkLabel(self.scrollable_frame, text="Customer Name:", font=("Arial", 15, "bold"), text_color=heading_color).pack()
        self.customer_name = ctk.CTkEntry(self.scrollable_frame, width=350, fg_color=entry_bg, text_color="#222", border_color=accent_color, border_width=2)
        self.customer_name.pack(pady=5)

        # Frame for menu items input
        self.menu_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=frame_bg, corner_radius=18)
        self.menu_frame.pack(pady=10, fill="x", padx=20)

        self.render_menu_entries()

        # Frame for add/delete menu items
        self.menu_manage_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=frame_bg, corner_radius=18)
        self.menu_manage_frame.pack(pady=15, fill="x", padx=20)

        self.build_menu_manage_ui()

        # Buttons
        btn_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=None)
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Total & Print", command=self.calculate_and_save, width=140, fg_color=accent_color, hover_color="#16a085", text_color="#fff").grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="Export All to Excel", command=self.export_to_excel, width=160, fg_color=accent_color, hover_color="#16a085", text_color="#fff").grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="Reset", command=self.reset, width=100, fg_color="#2980b9", hover_color="#2471a3", text_color="#fff").grid(row=1, column=0, padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="Exit", command=self.root.quit, width=100, fg_color="#e74c3c", hover_color="#c0392b", text_color="#fff").grid(row=1, column=1, padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="Add Test Data", command=self.add_sample_data_for_testing, width=120, fg_color="#9b59b6", hover_color="#8e44ad", text_color="#fff").grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        self.total_label = ctk.CTkLabel(self.scrollable_frame, text="Total: ₹0", font=("Arial", 18, "bold"), text_color=total_color)
        self.total_label.pack(pady=15)

        # New labels for all time total and today's total
        self.all_time_total_label = ctk.CTkLabel(self.scrollable_frame, text="All-Time Total Amount: ₹0", font=("Arial", 15, "bold"), text_color="#000")
        self.all_time_total_label.pack(pady=5)

        self.today_total_label = ctk.CTkLabel(self.scrollable_frame, text="Today's Total Amount: ₹0", font=("Arial", 15, "bold"), text_color="#000")
        self.today_total_label.pack(pady=5)

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def render_menu_entries(self):
        accent_color = "#1abc9c"
        label_color = "#eaf6fb"
        entry_bg = "#eaf6fb"
        heading_color = "#fff"
        # Clear current widgets in menu_frame
        for widget in self.menu_frame.winfo_children():
            widget.destroy()
        self.entries.clear()

        ctk.CTkLabel(self.menu_frame, text="Menu Item", font=("Arial", 14, "bold"), text_color=heading_color).grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkLabel(self.menu_frame, text="Price (₹)", font=("Arial", 14, "bold"), text_color=heading_color).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.menu_frame, text="Quantity", font=("Arial", 14, "bold"), text_color=heading_color).grid(row=0, column=2, padx=10, pady=5)

        for idx, (item, price) in enumerate(self.menu.items(), start=1):
            ctk.CTkLabel(self.menu_frame, text=item, font=("Arial", 13, "bold"), text_color="#fff").grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.menu_frame, text=str(price), font=("Arial", 13, "bold"), text_color="#fff").grid(row=idx, column=1, padx=10, pady=5)
            entry = ctk.CTkEntry(self.menu_frame, width=60, placeholder_text="0", fg_color=entry_bg, text_color="#222", border_color=accent_color, border_width=2)
            entry.grid(row=idx, column=2, padx=10, pady=5)
            self.entries[item] = entry

    def build_menu_manage_ui(self):
        accent_color = "#1abc9c"
        label_color = "#eaf6fb"
        entry_bg = "#eaf6fb"
        heading_color = "#fff"
        # Add new menu item
        add_label = ctk.CTkLabel(self.menu_manage_frame, text="Add New Item", font=("Arial", 14, "bold"), text_color=heading_color)
        add_label.grid(row=0, column=0, columnspan=3, pady=(0,10))

        ctk.CTkLabel(self.menu_manage_frame, text="Item Name:", text_color=label_color, font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="e", padx=5)
        self.new_item_name = ctk.CTkEntry(self.menu_manage_frame, width=180, fg_color=entry_bg, text_color="#222", border_color=accent_color, border_width=2)
        self.new_item_name.grid(row=1, column=1, padx=5)

        ctk.CTkLabel(self.menu_manage_frame, text="Price (₹):", text_color=label_color, font=("Arial", 12, "bold")).grid(row=1, column=2, sticky="e", padx=5)
        self.new_item_price = ctk.CTkEntry(self.menu_manage_frame, width=80, fg_color=entry_bg, text_color="#222", border_color=accent_color, border_width=2)
        self.new_item_price.grid(row=1, column=3, padx=5)

        add_btn = ctk.CTkButton(self.menu_manage_frame, text="Add", command=self.add_menu_item, fg_color=accent_color, hover_color="#16a085", text_color="#fff", width=70, height=28)
        add_btn.grid(row=1, column=4, padx=10)

        # Separator
        sep = ctk.CTkLabel(self.menu_manage_frame, text="-"*60, text_color=label_color)
        sep.grid(row=2, column=0, columnspan=5, pady=10)

        # Delete existing menu item
        del_label = ctk.CTkLabel(self.menu_manage_frame, text="Delete Item", font=("Arial", 14, "bold"), text_color=heading_color)
        del_label.grid(row=3, column=0, columnspan=5, pady=(0,10))

        ctk.CTkLabel(self.menu_manage_frame, text="Select Item:", text_color=label_color, font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="e", padx=5)
        self.delete_item_dropdown = ctk.CTkComboBox(self.menu_manage_frame, values=list(self.menu.keys()), width=200, fg_color=entry_bg, text_color="#222", border_color=accent_color, border_width=2, button_color=accent_color)
        self.delete_item_dropdown.grid(row=4, column=1, columnspan=2, padx=5)

        del_btn = ctk.CTkButton(self.menu_manage_frame, text="Delete Item", fg_color="#e74c3c", hover_color="#c0392b", text_color="#fff", command=self.delete_menu_item)
        del_btn.grid(row=4, column=3, padx=10)

    def add_menu_item(self):
        item = self.new_item_name.get().strip()
        price_text = self.new_item_price.get().strip()

        if not item:
            messagebox.showerror("Input Error", "Item name cannot be empty.")
            return

        if item in self.menu:
            messagebox.showerror("Input Error", "This item already exists in the menu.")
            return

        try:
            price = float(price_text)
            if price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Enter a valid positive number for price.")
            return

        # Add to menu and refresh UI
        self.menu[item] = price
        self.render_menu_entries()

        # Update delete dropdown options
        self.delete_item_dropdown.configure(values=list(self.menu.keys()))

        # Clear input fields
        self.new_item_name.delete(0, "end")
        self.new_item_price.delete(0, "end")

        messagebox.showinfo("Success", f"'{item}' added to menu with price ₹{price:.2f}")

    def delete_menu_item(self):
        item = self.delete_item_dropdown.get()
        if not item:
            messagebox.showerror("Selection Error", "Select an item to delete.")
            return

        if item not in self.menu:
            messagebox.showerror("Selection Error", "Selected item not found in menu.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item}' from the menu?")
        if not confirm:
            return

        del self.menu[item]
        self.render_menu_entries()
        self.delete_item_dropdown.configure(values=list(self.menu.keys()))
        self.delete_item_dropdown.set("")

        messagebox.showinfo("Success", f"'{item}' has been removed from the menu.")

    def init_db(self):
        if not os.path.exists("bills"):
            os.makedirs("bills")
        self.conn = sqlite3.connect(DB_FILE)
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS bills (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer TEXT,
                        datetime TEXT,
                        items TEXT,
                        subtotal REAL,
                        tax REAL,
                        service_charge REAL,
                        total REAL,
                        pdf_path TEXT
                    )''')
        self.conn.commit()

    def calculate_and_save(self):
        name = self.customer_name.get().strip()
        if not name:
            messagebox.showerror("Input Error", "Customer name is required.")
            return

        subtotal = 0
        order_items = {}

        for item, entry in self.entries.items():
            try:
                qty = int(entry.get() or 0)
                if qty < 0:
                    raise ValueError
                price = qty * self.menu[item]
                if qty > 0:
                    order_items[item] = (qty, price)
                    subtotal += price
            except ValueError:
                messagebox.showerror("Invalid input", f"Enter a valid quantity for {item}.")
                return

        if not order_items:
            messagebox.showerror("Order Error", "Add at least one item.")
            return

        tax = subtotal * TAX_RATE
        total = subtotal + tax + SERVICE_CHARGE

        self.total_label.configure(
            text=f"Subtotal: ₹{subtotal:.2f}\nTax: ₹{tax:.2f}\nService: ₹{SERVICE_CHARGE}\nTotal: ₹{total:.2f}",
            text_color="#000"
        )

        datetime_str = time.strftime("%Y-%m-%d %H:%M:%S")
        pdf_path = self.generate_pdf_bill(order_items, name, total, datetime_str)
        self.bill_pdf_path = pdf_path

        # Save to DB
        c = self.conn.cursor()
        items_str = json.dumps(order_items)  # Save order items as JSON string
        c.execute('''INSERT INTO bills (customer, datetime, items, subtotal, tax, service_charge, total, pdf_path)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (name, datetime_str, items_str, subtotal, tax, SERVICE_CHARGE, total, pdf_path))
        self.conn.commit()

        messagebox.showinfo("Success", f"Bill saved and recorded successfully.\nPDF: {pdf_path}")

        # Update totals labels after saving
        self.update_totals_labels()

    def generate_pdf_bill(self, order_items, customer_name, total_amount, datetime_str):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"Bill_{customer_name}_{timestamp}.pdf"
        filepath = os.path.join("bills", filename)

        c = canvas.Canvas(filepath, pagesize=letter)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(160, 750, "SMART BILLING SYSTEM - Customer Bill")
        c.setFont("Helvetica", 12)

        y = 700
        c.drawString(50, y, f"Customer: {customer_name}")
        y -= 30
        c.drawString(50, y, f"Date/Time: {datetime_str}")
        y -= 30
        for item, (qty, price) in order_items.items():
            c.drawString(50, y, f"{item} x {qty} = ₹{price}")
            y -= 20

        y -= 10
        c.drawString(50, y, f"Total Amount: ₹{total_amount:.2f}")
        c.drawString(50, y - 30, f"Thank you for your visit!")
        c.save()

        return filepath

    def export_to_excel(self):
        c = self.conn.cursor()
        c.execute("SELECT customer, datetime, items, subtotal, tax, service_charge, total FROM bills")
        rows = c.fetchall()
        if not rows:
            messagebox.showinfo("Export", "No bills found to export.")
            return

        data = []
        for r in rows:
            customer, datetime_str, items_json, subtotal, tax, service_charge, total = r
            items = json.loads(items_json)
            # Flatten items to string for excel
            items_str = ", ".join([f"{k}x{v[0]}" for k, v in items.items()])
            data.append({
                "Customer": customer,
                "DateTime": datetime_str,
                "Items": items_str,
                "Subtotal": subtotal,
                "Tax": tax,
                "Service Charge": service_charge,
                "Total": total
            })

        df = pd.DataFrame(data)
        df.to_excel(EXCEL_FILE, index=False)

        messagebox.showinfo("Export", f"All bills exported to Excel file:\n{EXCEL_FILE}")

    def reset(self):
        self.customer_name.delete(0, 'end')
        for entry in self.entries.values():
            entry.delete(0, 'end')
        self.total_label.configure(text="Total: ₹0")
        self.bill_pdf_path = None

    def update_totals_labels(self):
        c = self.conn.cursor()

        # Calculate all-time total
        c.execute("SELECT SUM(total) FROM bills")
        all_time_total = c.fetchone()[0] or 0

        # Calculate today's total
        today_date = time.strftime("%Y-%m-%d")
        c.execute("SELECT SUM(total) FROM bills WHERE datetime LIKE ?", (f"{today_date}%",))
        today_total = c.fetchone()[0] or 0

        self.all_time_total_label.configure(text=f"All-Time Total Amount: ₹{all_time_total:.2f}")
        self.today_total_label.configure(text=f"Today's Total Amount: ₹{today_total:.2f}")
        # Update the new big label as well
        self.todays_total_big_label.configure(text=f"₹{today_total:.2f}")

    def setup_analytics_controls(self):
        # Dropdown for chart selection
        self.chart_options = [
            "Most Popular Items (Bar)",
            "Revenue per Item (Bar)",
            "Revenue Share (Pie)",
            "Order Counts per Day (Line)",
            "Quantity Histogram",
            "Future Profit Prediction"
        ]
        self.analytics_dropdown = ctk.CTkComboBox(self.analytics_controls_frame, values=self.chart_options, width=260)
        self.analytics_dropdown.set("Most Popular Items (Bar)")
        self.analytics_dropdown.grid(row=0, column=0, padx=5)
        self.analytics_show_btn = ctk.CTkButton(self.analytics_controls_frame, text="Display", command=self.display_selected_analytics, fg_color="#1abc9c", text_color="#fff")
        self.analytics_show_btn.grid(row=0, column=1, padx=5)

    def display_selected_analytics(self):
        selected = self.analytics_dropdown.get()
        if selected == "Most Popular Items (Bar)":
            self.display_analytics_most_popular_bar()
        elif selected == "Revenue per Item (Bar)":
            self.display_analytics_revenue_per_item_bar()
        elif selected == "Revenue Share (Pie)":
            self.display_analytics_revenue_share_pie()
        elif selected == "Order Counts per Day (Line)":
            self.display_analytics_order_counts_line()
        elif selected == "Quantity Histogram":
            self.display_analytics_quantity_histogram()
        elif selected == "Future Profit Prediction":
            self.display_analytics_profit_prediction()

    def display_analytics_most_popular_bar(self):
        self._clear_analytics_charts()
        c = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT items FROM bills", c)
        c.close()
        if df.empty:
            ctk.CTkLabel(self.analytics_charts_frame, text="No data yet.", text_color="#888").pack(pady=20)
            return
        item_counts = {}
        for items_json in df['items']:
            items = json.loads(items_json)
            for k, v in items.items():
                item_counts[k] = item_counts.get(k, 0) + v[0]
        if not item_counts:
            ctk.CTkLabel(self.analytics_charts_frame, text="No item data.", text_color="#888").pack(pady=20)
            return
        fig, ax = plt.subplots(figsize=(7,5), dpi=100)
        items = list(item_counts.keys())
        counts = list(item_counts.values())
        ax.bar(items, counts, color="#1abc9c")
        ax.set_title("Most Popular Items")
        ax.set_ylabel("Quantity Sold")
        ax.set_xlabel("Menu Item")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        fig.tight_layout()
        chart = FigureCanvasTkAgg(fig, master=self.analytics_charts_frame)
        chart.get_tk_widget().pack(pady=10)
        plt.close(fig)

    def display_analytics_revenue_per_item_bar(self):
        self._clear_analytics_charts()
        c = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT items FROM bills", c)
        c.close()
        if df.empty:
            ctk.CTkLabel(self.analytics_charts_frame, text="No data yet.", text_color="#888").pack(pady=20)
            return
        item_revenue = {}
        for items_json in df['items']:
            items = json.loads(items_json)
            for k, v in items.items():
                item_revenue[k] = item_revenue.get(k, 0) + v[1]
        if not item_revenue:
            ctk.CTkLabel(self.analytics_charts_frame, text="No item data.", text_color="#888").pack(pady=20)
            return
        fig, ax = plt.subplots(figsize=(7,5), dpi=100)
        items = list(item_revenue.keys())
        revenue = list(item_revenue.values())
        ax.bar(items, revenue, color="#2980b9")
        ax.set_title("Revenue per Item")
        ax.set_ylabel("Revenue (₹)")
        ax.set_xlabel("Menu Item")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        fig.tight_layout()
        chart = FigureCanvasTkAgg(fig, master=self.analytics_charts_frame)
        chart.get_tk_widget().pack(pady=10)
        plt.close(fig)

    def display_analytics_revenue_share_pie(self):
        self._clear_analytics_charts()
        c = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT items FROM bills", c)
        c.close()
        if df.empty:
            ctk.CTkLabel(self.analytics_charts_frame, text="No data yet.", text_color="#888").pack(pady=20)
            return
        item_revenue = {}
        for items_json in df['items']:
            items = json.loads(items_json)
            for k, v in items.items():
                item_revenue[k] = item_revenue.get(k, 0) + v[1]
        if not item_revenue:
            ctk.CTkLabel(self.analytics_charts_frame, text="No item data.", text_color="#888").pack(pady=20)
            return
        fig, ax = plt.subplots(figsize=(7,5), dpi=100)
        items = list(item_revenue.keys())
        revenue = list(item_revenue.values())
        ax.pie(revenue, labels=items, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
        ax.set_title("Revenue Share by Item")
        fig.tight_layout()
        chart = FigureCanvasTkAgg(fig, master=self.analytics_charts_frame)
        chart.get_tk_widget().pack(pady=10)
        plt.close(fig)

    def display_analytics_order_counts_line(self):
        self._clear_analytics_charts()
        c = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT datetime FROM bills", c)
        c.close()
        if df.empty:
            ctk.CTkLabel(self.analytics_charts_frame, text="No data yet.", text_color="#888").pack(pady=20)
            return
        df['date'] = df['datetime'].str[:10]
        date_counts = df['date'].value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(7,5), dpi=100)
        ax.plot(date_counts.index, date_counts.values, marker='o', color="#e67e22")
        ax.set_title("Order Counts per Day")
        ax.set_ylabel("Orders")
        ax.set_xlabel("Date")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        fig.tight_layout()
        chart = FigureCanvasTkAgg(fig, master=self.analytics_charts_frame)
        chart.get_tk_widget().pack(pady=10)
        plt.close(fig)

    def display_analytics_quantity_histogram(self):
        self._clear_analytics_charts()
        c = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT items FROM bills", c)
        c.close()
        if df.empty:
            ctk.CTkLabel(self.analytics_charts_frame, text="No data yet.", text_color="#888").pack(pady=20)
            return
        quantities = []
        for items_json in df['items']:
            items = json.loads(items_json)
            for v in items.values():
                quantities.append(v[0])
        if not quantities:
            ctk.CTkLabel(self.analytics_charts_frame, text="No quantity data.", text_color="#888").pack(pady=20)
            return
        fig, ax = plt.subplots(figsize=(7,5), dpi=100)
        ax.hist(quantities, bins=range(1, max(quantities)+2), color="#8e44ad", edgecolor='black', align='left')
        ax.set_title("Quantity Histogram")
        ax.set_xlabel("Quantity per Order Item")
        ax.set_ylabel("Frequency")
        fig.tight_layout()
        chart = FigureCanvasTkAgg(fig, master=self.analytics_charts_frame)
        chart.get_tk_widget().pack(pady=10)
        plt.close(fig)

    def display_analytics_profit_prediction(self):
        self._clear_analytics_charts()
        c = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT datetime, items FROM bills", c)
        c.close()
        if df.empty:
            ctk.CTkLabel(self.analytics_charts_frame, text="No data yet.", text_color="#888").pack(pady=20)
            return
        
        # Add debugging info
        debug_info = f"Total bills in database: {len(df)}"
        ctk.CTkLabel(self.analytics_charts_frame, text=debug_info, text_color="#666", font=("Arial", 10)).pack(pady=5)
        
        df['date'] = df['datetime'].str[:10]
        # Build a dict: {item: [daily sales list]}
        all_dates = sorted(df['date'].unique())
        item_sales = {item: [0]*len(all_dates) for item in self.menu.keys()}
        date_index = {d: i for i, d in enumerate(all_dates)}
        
        # Debug: Show available dates
        dates_info = f"Available dates: {', '.join(all_dates)}"
        ctk.CTkLabel(self.analytics_charts_frame, text=dates_info, text_color="#666", font=("Arial", 10)).pack(pady=5)
        
        for _, row in df.iterrows():
            items = json.loads(row['items'])
            for k, v in items.items():
                if k in item_sales:
                    item_sales[k][date_index[row['date']]] += v[0]
        
        # Debug: Show item sales data
        sales_debug = "Item sales data:"
        for item, sales in item_sales.items():
            non_zero_count = np.count_nonzero(sales)
            total_sales = sum(sales)
            sales_debug += f"\n{item}: {non_zero_count} non-zero days, total sales: {total_sales}"
        
        ctk.CTkLabel(self.analytics_charts_frame, text=sales_debug, text_color="#666", font=("Arial", 10), justify="left").pack(pady=5)
        
        # Predict next 7 days for each item
        future_days = 7
        future_dates = pd.date_range(all_dates[-1], periods=future_days+1, freq='D')[1:]
        table_frame = ctk.CTkFrame(self.analytics_charts_frame)
        table_frame.pack(pady=10)
        # Header
        ctk.CTkLabel(table_frame, text="Item", font=("Arial", 13, "bold"), width=120).grid(row=0, column=0, padx=2, pady=2)
        for j, d in enumerate(future_dates):
            ctk.CTkLabel(table_frame, text=d.strftime('%Y-%m-%d'), font=("Arial", 12, "bold"), width=90).grid(row=0, column=j+1, padx=2, pady=2)
        # Rows: each item
        for i, (item, sales) in enumerate(item_sales.items()):
            ctk.CTkLabel(table_frame, text=item, font=("Arial", 12), width=120).grid(row=i+1, column=0, padx=2, pady=2)
            sales_arr = np.array(sales)
            if np.count_nonzero(sales_arr) < 2:
                preds = ["N/A"]*future_days
            else:
                X = np.arange(len(sales_arr)).reshape(-1, 1)
                y = sales_arr
                model = LinearRegression()
                model.fit(X, y)
                X_future = np.arange(len(sales_arr), len(sales_arr)+future_days).reshape(-1, 1)
                preds = np.maximum(0, np.round(model.predict(X_future))).astype(int)
            for j, val in enumerate(preds):
                ctk.CTkLabel(table_frame, text=str(val), font=("Arial", 12), width=90).grid(row=i+1, column=j+1, padx=2, pady=2)
        # Explanation below the table
        # Line chart: predicted sales per item for the next 7 days
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        fig, ax = plt.subplots(figsize=(5,3), dpi=100)
        for item, sales in item_sales.items():
            sales_arr = np.array(sales)
            if np.count_nonzero(sales_arr) < 2:
                continue
            X = np.arange(len(sales_arr)).reshape(-1, 1)
            y = sales_arr
            model = LinearRegression()
            model.fit(X, y)
            X_future = np.arange(len(sales_arr), len(sales_arr)+future_days).reshape(-1, 1)
            preds = np.maximum(0, np.round(model.predict(X_future))).astype(int)
            ax.plot([d.strftime('%Y-%m-%d') for d in future_dates], preds, marker='o', label=item)
        ax.set_title("Predicted Sales per Item (Next 7 Days)")
        ax.set_ylabel("Predicted Sales")
        ax.set_xlabel("Date")
        ax.legend(fontsize=8)
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        fig.tight_layout()
        chart = FigureCanvasTkAgg(fig, master=self.analytics_charts_frame)
        chart.get_tk_widget().pack(pady=10, fill="x", expand=False)
        plt.close(fig)

        explanation = (
            "This table shows the predicted sales for each menu item for the next 7 days, "
            "based on previous sales data and linear regression. Predictions are rounded to the nearest integer. "
            "'N/A' means not enough data for prediction (need at least 2 days with sales)."
        )
        self.prediction_explanation_label = ctk.CTkLabel(self.analytics_charts_frame, text=explanation, wraplength=500, font=("Arial", 13), text_color="#222", justify="left")
        self.prediction_explanation_label.pack(pady=(5, 10))
        # Back button
        self.back_btn = ctk.CTkButton(self.analytics_charts_frame, text="Back", command=self._back_to_analytics_controls, fg_color="#2980b9", text_color="#fff")
        self.back_btn.pack(pady=(0, 10))

    def _back_to_analytics_controls(self):
        self._clear_analytics_charts()

    def _clear_analytics_charts(self):
        for widget in self.analytics_charts_frame.winfo_children():
            widget.destroy()

    def go_back(self):
        # Universal back: clear analytics chart area and show main analytics controls
        self._clear_analytics_charts()
        # Future: add logic here to handle main content navigation if needed

    def add_sample_data_for_testing(self):
        """Add sample data to test predictions - for development only"""
        import random
        from datetime import datetime, timedelta
        
        # Generate sample data for the last 10 days
        base_date = datetime.now() - timedelta(days=10)
        
        for day in range(10):
            current_date = base_date + timedelta(days=day)
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Generate 1-3 bills per day
            num_bills = random.randint(1, 3)
            for bill in range(num_bills):
                time_str = current_date.strftime("%H:%M:%S")
                datetime_str = f"{date_str} {time_str}"
                
                # Generate random order
                order_items = {}
                for item in self.menu.keys():
                    if random.random() < 0.6:  # 60% chance to order each item
                        qty = random.randint(1, 5)
                        price = qty * self.menu[item]
                        order_items[item] = (qty, price)
                
                if order_items:
                    subtotal = sum(price for _, price in order_items.values())
                    tax = subtotal * TAX_RATE
                    total = subtotal + tax + SERVICE_CHARGE
                    
                    # Save to DB
                    c = self.conn.cursor()
                    items_str = json.dumps(order_items)
                    c.execute('''INSERT INTO bills (customer, datetime, items, subtotal, tax, service_charge, total, pdf_path)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                              (f"Test Customer {day}-{bill}", datetime_str, items_str, subtotal, tax, SERVICE_CHARGE, total, f"test_bill_{day}_{bill}.pdf"))
                    self.conn.commit()
        
        messagebox.showinfo("Test Data", "Sample data added for testing predictions!")

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = ctk.CTk()
    CafeApp(app)
    app.mainloop()
