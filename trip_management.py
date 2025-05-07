
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from tkcalendar import DateEntry
from datetime import datetime
import csv
import os

class TripManagement:
    def __init__(self, parent):
        self.parent = parent
        
        # Create the widgets
        self.create_widgets()
        
        # Load existing trips
        self.load_trips()
    
    def create_widgets(self):
        # Create frames
        form_frame = ttk.LabelFrame(self.parent, text="Trip Details")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        table_frame = ttk.LabelFrame(self.parent, text="Trip Records")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Form widgets - Row 1
        row1 = ttk.Frame(form_frame)
        row1.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row1, text="Date:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.date_entry = DateEntry(row1, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(row1, text="Client Name:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.client_entry = ttk.Entry(row1, width=20)
        self.client_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(row1, text="Driver Name:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.driver_entry = ttk.Entry(row1, width=20)
        self.driver_entry.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        # Form widgets - Row 2
        row2 = ttk.Frame(form_frame)
        row2.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row2, text="Cargo Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.cargo_entry = ttk.Entry(row2, width=15)
        self.cargo_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(row2, text="Route:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.route_entry = ttk.Entry(row2, width=25)
        self.route_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Form widgets - Row 3
        row3 = ttk.Frame(form_frame)
        row3.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row3, text="Trip Income (TZS):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.income_entry = ttk.Entry(row3, width=15)
        self.income_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(row3, text="Fuel Expenses (TZS):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.expense_entry = ttk.Entry(row3, width=15)
        self.expense_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Form buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_button = ttk.Button(button_frame, text="Add Trip", command=self.add_trip)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.update_button = ttk.Button(button_frame, text="Update Selected", command=self.update_trip, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(button_frame, text="Delete Selected", command=self.delete_trip, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Form", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Control widgets
        ttk.Label(control_frame, text="Filter by Driver:").pack(side=tk.LEFT, padx=5, pady=5)
        self.driver_filter = ttk.Combobox(control_frame, width=20)
        self.driver_filter.pack(side=tk.LEFT, padx=5, pady=5)
        self.driver_filter.bind("<<ComboboxSelected>>", self.filter_trips)
        
        ttk.Button(control_frame, text="Reset Filter", command=self.load_trips).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Export to CSV", command=self.export_to_csv).pack(side=tk.RIGHT, padx=5, pady=5)
        ttk.Button(control_frame, text="Export to PDF", command=self.export_to_pdf).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Create treeview for trips
        columns = ("id", "date", "client", "cargo", "route", "income", "expenses", "driver")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Set column headings
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("client", text="Client")
        self.tree.heading("cargo", text="Cargo")
        self.tree.heading("route", text="Route")
        self.tree.heading("income", text="Income (TZS)")
        self.tree.heading("expenses", text="Expenses (TZS)")
        self.tree.heading("driver", text="Driver")
        
        # Set column widths
        self.tree.column("id", width=40)
        self.tree.column("date", width=100)
        self.tree.column("client", width=120)
        self.tree.column("cargo", width=120)
        self.tree.column("route", width=150)
        self.tree.column("income", width=100)
        self.tree.column("expenses", width=100)
        self.tree.column("driver", width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind select event
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def load_trips(self):
        """Load all trips from the database"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # Connect to the database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Get all trips
            cursor.execute("SELECT * FROM trips ORDER BY date DESC")
            trips = cursor.fetchall()
            
            # Add trips to treeview
            for trip in trips:
                trip_id, date, client, cargo, route, income, expenses, driver = trip
                
                income_formatted = f"{float(income):.2f}"
                expenses_formatted = f"{float(expenses):.2f}"
                
                self.tree.insert("", tk.END, values=(trip_id, date, client, cargo, route, 
                                                   income_formatted, expenses_formatted, driver))
            
            # Load drivers for filter
            cursor.execute("SELECT DISTINCT driver_name FROM trips ORDER BY driver_name")
            drivers = [row[0] for row in cursor.fetchall()]
            self.driver_filter['values'] = drivers
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load trips: {str(e)}")
    
    def filter_trips(self, event=None):
        """Filter trips by driver"""
        selected_driver = self.driver_filter.get()
        
        if not selected_driver:
            self.load_trips()
            return
        
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Connect to the database
            conn = sqlite3.connect('easylogipro.db')
            cursor = conn.cursor()
            
            # Get filtered trips
            cursor.execute("SELECT * FROM trips WHERE driver_name=? ORDER BY date DESC", (selected_driver,))
            trips = cursor.fetchall()
            
            # Add trips to treeview
            for trip in trips:
                trip_id, date, client, cargo, route, income, expenses, driver = trip
                
                income_formatted = f"{float(income):.2f}"
                expenses_formatted = f"{float(expenses):.2f}"
                
                self.tree.insert("", tk.END, values=(trip_id, date, client, cargo, route, 
                                                   income_formatted, expenses_formatted, driver))
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter trips: {str(e)}")
    
    # Export to CSV
    def export_to_csv(self):
        """Export trip data to CSV file"""
        try:
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save Trip Report"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Get data from treeview
            trip_data = []
            
            headers = ["ID", "Date", "Client", "Cargo Type", "Route", "Income (TZS)", "Expenses (TZS)", "Driver"]
            trip_data.append(headers)
            
            for item_id in self.tree.get_children():
                trip_data.append(self.tree.item(item_id, "values"))
            
            # Write to CSV
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(trip_data)
                
            messagebox.showinfo("Export Successful", f"Trip data exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    # Export to PDF
    def export_to_pdf(self):
        """Export trip data to PDF file"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import landscape, letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Trip Report"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=landscape(letter))
            elements = []
            
            # Add title
            styles = getSampleStyleSheet()
            title = Paragraph("Trip Report", styles['Title'])
            date_text = Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
            elements.append(title)
            elements.append(date_text)
            elements.append(Spacer(1, 20))
            
            # Prepare data
            data = [["Date", "Client", "Cargo Type", "Route", "Income (TZS)", "Expenses (TZS)", "Driver"]]
            
            for item_id in self.tree.get_children():
                values = self.tree.item(item_id, "values")
                data.append(values[1:])  # Skip ID column
            
            # Create table
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('ALIGN', (4, 1), (5, -1), 'RIGHT'),  # Align income and expenses columns right
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            messagebox.showinfo("Export Successful", f"Trip data exported to {file_path}")
            
        except ImportError:
            messagebox.showerror("Missing Library", "ReportLab is required for PDF export. Please install it with 'pip install reportlab'")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    # ... keep existing code (clear_form, add_trip, update_trip, delete_trip, and on_select methods)
