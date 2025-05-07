
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class DriverPayment:
    def __init__(self, parent):
        self.parent = parent
        
        # Create widgets
        self.create_widgets()
        self.load_driver_payments()
    
    def create_widgets(self):
        # Create frames
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        table_frame = ttk.LabelFrame(self.parent, text="Driver Payment Summary")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control widgets
        self.refresh_btn = ttk.Button(control_frame, text="Refresh Data", command=self.load_driver_payments)
        self.refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create Treeview
        columns = ("driver_name", "trip_count", "total_income", "total_expenses", "net_payment")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Set column headings
        self.tree.heading("driver_name", text="Driver Name")
        self.tree.heading("trip_count", text="Number of Trips")
        self.tree.heading("total_income", text="Total Income ($)")
        self.tree.heading("total_expenses", text="Total Expenses ($)")
        self.tree.heading("net_payment", text="Net Payment ($)")
        
        # Set column widths
        self.tree.column("driver_name", width=150)
        self.tree.column("trip_count", width=100)
        self.tree.column("total_income", width=120)
        self.tree.column("total_expenses", width=120)
        self.tree.column("net_payment", width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def load_driver_payments(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Connect to the database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Query to calculate driver payments from trip data
            cursor.execute('''
            SELECT 
                driver_name,
                COUNT(*) as trip_count,
                SUM(trip_income) as total_income,
                SUM(fuel_expenses) as total_expenses,
                (SUM(trip_income) - SUM(fuel_expenses)) as net_payment
            FROM trips
            GROUP BY driver_name
            ORDER BY net_payment DESC
            ''')
            
            payments = cursor.fetchall()
            
            # Add payments to treeview
            for payment in payments:
                driver_name, trip_count, total_income, total_expenses, net_payment = payment
                
                income_formatted = f"{float(total_income):.2f}"
                expenses_formatted = f"{float(total_expenses):.2f}"
                net_formatted = f"{float(net_payment):.2f}"
                
                self.tree.insert("", tk.END, values=(driver_name, trip_count, income_formatted, 
                                                   expenses_formatted, net_formatted))
            
            conn.close()
            
            # Calculate total
            self.calculate_totals()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load driver payments: {str(e)}")
    
    def calculate_totals(self):
        # Add a total row
        total_trips = 0
        total_income = 0.0
        total_expenses = 0.0
        total_net = 0.0
        
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, "values")
            total_trips += int(values[1])
            total_income += float(values[2])
            total_expenses += float(values[3])
            total_net += float(values[4])
        
        # Insert total row at the end
        self.tree.insert("", tk.END, values=(
            "TOTAL", 
            total_trips, 
            f"{total_income:.2f}", 
            f"{total_expenses:.2f}", 
            f"{total_net:.2f}"
        ), tags=('total',))
        
        # Configure tag for total row
        self.tree.tag_configure('total', background='#f0f0f0', font=('TkDefaultFont', 10, 'bold'))
