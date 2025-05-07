
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry

class TripManagement:
    def __init__(self, parent):
        self.parent = parent
        
        # Create frames
        self.create_widgets()
        self.load_trips()
    
    def create_widgets(self):
        # Create frames
        form_frame = ttk.LabelFrame(self.parent, text="Trip Details")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        table_frame = ttk.LabelFrame(self.parent, text="Trip Records")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Form widgets
        # Row 1
        row1 = ttk.Frame(form_frame)
        row1.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row1, text="Date:").pack(side=tk.LEFT, padx=(0, 5))
        self.date_entry = DateEntry(row1, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Client Name:").pack(side=tk.LEFT, padx=(10, 5))
        self.client_entry = ttk.Entry(row1, width=20)
        self.client_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Driver Name:").pack(side=tk.LEFT, padx=(10, 5))
        self.driver_entry = ttk.Entry(row1, width=20)
        self.driver_entry.pack(side=tk.LEFT, padx=5)
        
        # Row 2
        row2 = ttk.Frame(form_frame)
        row2.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row2, text="Cargo Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.cargo_entry = ttk.Entry(row2, width=15)
        self.cargo_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="Route:").pack(side=tk.LEFT, padx=(10, 5))
        self.route_entry = ttk.Entry(row2, width=25)
        self.route_entry.pack(side=tk.LEFT, padx=5)
        
        # Row 3
        row3 = ttk.Frame(form_frame)
        row3.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row3, text="Trip Income ($):").pack(side=tk.LEFT, padx=(0, 5))
        self.income_entry = ttk.Entry(row3, width=10)
        self.income_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row3, text="Fuel Expenses ($):").pack(side=tk.LEFT, padx=(10, 5))
        self.expenses_entry = ttk.Entry(row3, width=10)
        self.expenses_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_button = ttk.Button(button_frame, text="Add Trip", command=self.add_trip)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.update_button = ttk.Button(button_frame, text="Update Selected", command=self.update_trip, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_trip, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Form", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create Treeview
        columns = ("id", "date", "client_name", "cargo_type", "route", "trip_income", "fuel_expenses", "driver_name")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Set column headings
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("client_name", text="Client Name")
        self.tree.heading("cargo_type", text="Cargo Type")
        self.tree.heading("route", text="Route")
        self.tree.heading("trip_income", text="Income ($)")
        self.tree.heading("fuel_expenses", text="Expenses ($)")
        self.tree.heading("driver_name", text="Driver")
        
        # Set column widths
        self.tree.column("id", width=40)
        self.tree.column("date", width=100)
        self.tree.column("client_name", width=150)
        self.tree.column("cargo_type", width=100)
        self.tree.column("route", width=150)
        self.tree.column("trip_income", width=100)
        self.tree.column("fuel_expenses", width=100)
        self.tree.column("driver_name", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind select event
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Add some padding
        for child in form_frame.winfo_children():
            child.pack_configure(pady=3)
    
    def load_trips(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Connect to the database
        conn = sqlite3.connect('easylogipro.db')
        cursor = conn.cursor()
        
        # Get all trips ordered by date (most recent first)
        cursor.execute("SELECT * FROM trips ORDER BY date DESC")
        trips = cursor.fetchall()
        
        # Add trips to treeview
        for trip in trips:
            trip_id, date, client_name, cargo_type, route, trip_income, fuel_expenses, driver_name = trip
            income_formatted = f"{float(trip_income):.2f}"
            expenses_formatted = f"{float(fuel_expenses):.2f}"
            
            self.tree.insert("", tk.END, values=(trip_id, date, client_name, cargo_type, route, 
                                                income_formatted, expenses_formatted, driver_name))
        
        conn.close()
    
    def clear_form(self):
        self.date_entry.set_date(None)
        self.client_entry.delete(0, tk.END)
        self.cargo_entry.delete(0, tk.END)
        self.route_entry.delete(0, tk.END)
        self.income_entry.delete(0, tk.END)
        self.expenses_entry.delete(0, tk.END)
        self.driver_entry.delete(0, tk.END)
        self.update_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.add_button.config(state=tk.NORMAL)
        self.tree.selection_remove(self.tree.selection())
    
    def validate_form(self):
        try:
            # Check if fields are empty
            if not self.date_entry.get() or not self.client_entry.get() or not self.cargo_entry.get() or \
               not self.route_entry.get() or not self.income_entry.get() or \
               not self.expenses_entry.get() or not self.driver_entry.get():
                messagebox.showerror("Validation Error", "All fields are required!")
                return False
            
            # Check if income and expenses are valid numbers
            try:
                float(self.income_entry.get())
                float(self.expenses_entry.get())
            except ValueError:
                messagebox.showerror("Validation Error", "Income and expenses must be valid numbers!")
                return False
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Validation error: {str(e)}")
            return False
    
    def add_trip(self):
        if not self.validate_form():
            return
        
        try:
            # Get values from form
            date = self.date_entry.get()
            client_name = self.client_entry.get()
            cargo_type = self.cargo_entry.get()
            route = self.route_entry.get()
            trip_income = float(self.income_entry.get())
            fuel_expenses = float(self.expenses_entry.get())
            driver_name = self.driver_entry.get()
            
            # Connect to database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Insert new trip
            cursor.execute('''
            INSERT INTO trips (date, client_name, cargo_type, route, trip_income, fuel_expenses, driver_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (date, client_name, cargo_type, route, trip_income, fuel_expenses, driver_name))
            
            conn.commit()
            conn.close()
            
            # Refresh trips list and clear form
            self.load_trips()
            self.clear_form()
            messagebox.showinfo("Success", "Trip added successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add trip: {str(e)}")
    
    def on_select(self, event):
        try:
            # Get selected item
            selected_item = self.tree.selection()[0]
            values = self.tree.item(selected_item, "values")
            
            if not values:
                return
            
            # Clear form first
            self.clear_form()
            
            # Set values in form
            self.date_entry.set_date(values[1])  # Date
            self.client_entry.insert(0, values[2])  # Client
            self.cargo_entry.insert(0, values[3])  # Cargo
            self.route_entry.insert(0, values[4])  # Route
            self.income_entry.insert(0, values[5])  # Income
            self.expenses_entry.insert(0, values[6])  # Expenses
            self.driver_entry.insert(0, values[7])  # Driver
            
            # Enable update and delete buttons, disable add button
            self.update_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
            self.add_button.config(state=tk.DISABLED)
            
        except IndexError:
            pass  # No selection
    
    def update_trip(self):
        if not self.validate_form():
            return
        
        try:
            # Get selected item
            selected_item = self.tree.selection()[0]
            trip_id = self.tree.item(selected_item, "values")[0]
            
            # Get updated values
            date = self.date_entry.get()
            client_name = self.client_entry.get()
            cargo_type = self.cargo_entry.get()
            route = self.route_entry.get()
            trip_income = float(self.income_entry.get())
            fuel_expenses = float(self.expenses_entry.get())
            driver_name = self.driver_entry.get()
            
            # Confirm update
            confirm = messagebox.askyesno("Confirm Update", "Are you sure you want to update this trip?")
            if not confirm:
                return
            
            # Connect to database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Update trip
            cursor.execute('''
            UPDATE trips
            SET date=?, client_name=?, cargo_type=?, route=?, trip_income=?, fuel_expenses=?, driver_name=?
            WHERE id=?
            ''', (date, client_name, cargo_type, route, trip_income, fuel_expenses, driver_name, trip_id))
            
            conn.commit()
            conn.close()
            
            # Refresh trips list and clear form
            self.load_trips()
            self.clear_form()
            messagebox.showinfo("Success", "Trip updated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update trip: {str(e)}")
    
    def delete_trip(self):
        try:
            # Get selected item
            selected_item = self.tree.selection()[0]
            trip_id = self.tree.item(selected_item, "values")[0]
            
            # Confirm deletion
            confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this trip?")
            if not confirm:
                return
            
            # Connect to database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Delete trip
            cursor.execute("DELETE FROM trips WHERE id=?", (trip_id,))
            
            conn.commit()
            conn.close()
            
            # Refresh trips list and clear form
            self.load_trips()
            self.clear_form()
            messagebox.showinfo("Success", "Trip deleted successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete trip: {str(e)}")
