
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry

class VehicleMaintenance:
    def __init__(self, parent):
        self.parent = parent
        
        # Create widgets
        self.create_widgets()
        self.load_maintenance_records()
    
    def create_widgets(self):
        # Create frames
        form_frame = ttk.LabelFrame(self.parent, text="Maintenance Details")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        table_frame = ttk.LabelFrame(self.parent, text="Maintenance Records")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Form widgets
        # Row 1
        row1 = ttk.Frame(form_frame)
        row1.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row1, text="Vehicle Plate:").pack(side=tk.LEFT, padx=(0, 5))
        self.plate_entry = ttk.Entry(row1, width=15)
        self.plate_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="Service Date:").pack(side=tk.LEFT, padx=(10, 5))
        self.date_entry = DateEntry(row1, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(side=tk.LEFT, padx=5)
        
        # Row 2
        row2 = ttk.Frame(form_frame)
        row2.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row2, text="Description:").pack(side=tk.LEFT, padx=(0, 5))
        self.description_entry = ttk.Entry(row2, width=40)
        self.description_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Row 3
        row3 = ttk.Frame(form_frame)
        row3.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row3, text="Cost ($):").pack(side=tk.LEFT, padx=(0, 5))
        self.cost_entry = ttk.Entry(row3, width=15)
        self.cost_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_button = ttk.Button(button_frame, text="Add Record", command=self.add_maintenance)
        self.add_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.update_button = ttk.Button(button_frame, text="Update Selected", command=self.update_maintenance, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_maintenance, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Form", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create Treeview
        columns = ("id", "vehicle_plate_number", "service_date", "description", "cost")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Set column headings
        self.tree.heading("id", text="ID")
        self.tree.heading("vehicle_plate_number", text="Vehicle Plate")
        self.tree.heading("service_date", text="Service Date")
        self.tree.heading("description", text="Description")
        self.tree.heading("cost", text="Cost ($)")
        
        # Set column widths
        self.tree.column("id", width=40)
        self.tree.column("vehicle_plate_number", width=100)
        self.tree.column("service_date", width=100)
        self.tree.column("description", width=300)
        self.tree.column("cost", width=100)
        
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
    
    def load_maintenance_records(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Connect to the database
        conn = sqlite3.connect('easylogipro.db')
        cursor = conn.cursor()
        
        # Get all records ordered by date
        cursor.execute("SELECT * FROM maintenance ORDER BY service_date DESC")
        records = cursor.fetchall()
        
        # Add records to treeview
        for record in records:
            record_id, plate, date, description, cost = record
            cost_formatted = f"{float(cost):.2f}"
            
            self.tree.insert("", tk.END, values=(record_id, plate, date, description, cost_formatted))
        
        conn.close()
    
    def clear_form(self):
        self.plate_entry.delete(0, tk.END)
        self.date_entry.set_date(None)
        self.description_entry.delete(0, tk.END)
        self.cost_entry.delete(0, tk.END)
        self.update_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.add_button.config(state=tk.NORMAL)
        self.tree.selection_remove(self.tree.selection())
    
    def validate_form(self):
        try:
            # Check if fields are empty
            if not self.plate_entry.get() or not self.date_entry.get() or not self.description_entry.get() or not self.cost_entry.get():
                messagebox.showerror("Validation Error", "All fields are required!")
                return False
            
            # Check if cost is a valid number
            try:
                float(self.cost_entry.get())
            except ValueError:
                messagebox.showerror("Validation Error", "Cost must be a valid number!")
                return False
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Validation error: {str(e)}")
            return False
    
    def add_maintenance(self):
        if not self.validate_form():
            return
        
        try:
            # Get values from form
            plate = self.plate_entry.get()
            date = self.date_entry.get()
            description = self.description_entry.get()
            cost = float(self.cost_entry.get())
            
            # Connect to database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Insert new record
            cursor.execute('''
            INSERT INTO maintenance (vehicle_plate_number, service_date, description, cost)
            VALUES (?, ?, ?, ?)
            ''', (plate, date, description, cost))
            
            conn.commit()
            conn.close()
            
            # Refresh records and clear form
            self.load_maintenance_records()
            self.clear_form()
            messagebox.showinfo("Success", "Maintenance record added successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add maintenance record: {str(e)}")
    
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
            self.plate_entry.insert(0, values[1])  # Plate
            self.date_entry.set_date(values[2])  # Date
            self.description_entry.insert(0, values[3])  # Description
            self.cost_entry.insert(0, values[4])  # Cost
            
            # Enable update and delete buttons, disable add button
            self.update_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
            self.add_button.config(state=tk.DISABLED)
            
        except IndexError:
            pass  # No selection
    
    def update_maintenance(self):
        if not self.validate_form():
            return
        
        try:
            # Get selected item
            selected_item = self.tree.selection()[0]
            record_id = self.tree.item(selected_item, "values")[0]
            
            # Get updated values
            plate = self.plate_entry.get()
            date = self.date_entry.get()
            description = self.description_entry.get()
            cost = float(self.cost_entry.get())
            
            # Confirm update
            confirm = messagebox.askyesno("Confirm Update", "Are you sure you want to update this maintenance record?")
            if not confirm:
                return
            
            # Connect to database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Update record
            cursor.execute('''
            UPDATE maintenance
            SET vehicle_plate_number=?, service_date=?, description=?, cost=?
            WHERE id=?
            ''', (plate, date, description, cost, record_id))
            
            conn.commit()
            conn.close()
            
            # Refresh records and clear form
            self.load_maintenance_records()
            self.clear_form()
            messagebox.showinfo("Success", "Maintenance record updated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update maintenance record: {str(e)}")
    
    def delete_maintenance(self):
        try:
            # Get selected item
            selected_item = self.tree.selection()[0]
            record_id = self.tree.item(selected_item, "values")[0]
            
            # Confirm deletion
            confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this maintenance record?")
            if not confirm:
                return
            
            # Connect to database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Delete record
            cursor.execute("DELETE FROM maintenance WHERE id=?", (record_id,))
            
            conn.commit()
            conn.close()
            
            # Refresh records and clear form
            self.load_maintenance_records()
            self.clear_form()
            messagebox.showinfo("Success", "Maintenance record deleted successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete maintenance record: {str(e)}")
