
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import os
from datetime import datetime

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
        
        # Export buttons
        self.export_csv_btn = ttk.Button(control_frame, text="Export to CSV", command=self.export_to_csv)
        self.export_csv_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.export_pdf_btn = ttk.Button(control_frame, text="Export to PDF", command=self.export_to_pdf)
        self.export_pdf_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create Treeview
        columns = ("driver_name", "trip_count", "total_income", "total_expenses", "net_payment")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Set column headings
        self.tree.heading("driver_name", text="Driver Name")
        self.tree.heading("trip_count", text="Number of Trips")
        self.tree.heading("total_income", text="Total Income (TZS)")
        self.tree.heading("total_expenses", text="Total Expenses (TZS)")
        self.tree.heading("net_payment", text="Net Payment (TZS)")
        
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

    def export_to_csv(self):
        """Export driver payments data to CSV file"""
        try:
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save Driver Payments Report"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Open file for writing
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(['Driver Name', 'Number of Trips', 'Total Income (TZS)', 
                                'Total Expenses (TZS)', 'Net Payment (TZS)'])
                
                # Write data rows
                for item_id in self.tree.get_children():
                    writer.writerow(self.tree.item(item_id, "values"))
            
            messagebox.showinfo("Export Successful", f"Driver payments exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

    def export_to_pdf(self):
        """Export driver payments data to PDF file"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Driver Payments Report"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            
            # Add title
            styles = getSampleStyleSheet()
            title = Paragraph("Driver Payments Report", styles['Title'])
            date_text = Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
            elements.append(title)
            elements.append(date_text)
            elements.append(Spacer(1, 20))
            
            # Prepare data
            data = [['Driver Name', 'Number of Trips', 'Total Income (TZS)', 
                    'Total Expenses (TZS)', 'Net Payment (TZS)']]
                    
            for item_id in self.tree.get_children():
                data.append(self.tree.item(item_id, "values"))
            
            # Create table
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            messagebox.showinfo("Export Successful", f"Driver payments exported to {file_path}")
            
        except ImportError:
            messagebox.showerror("Missing Library", "ReportLab is required for PDF export. Please install it with 'pip install reportlab'")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
