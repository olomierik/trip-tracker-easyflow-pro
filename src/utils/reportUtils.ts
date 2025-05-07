
import { saveAs } from 'file-saver';
import * as XLSX from 'xlsx';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';

type ReportData = {
  headers: string[];
  rows: (string | number)[][];
  title: string;
  fileName: string;
};

export const generateExcelReport = (data: ReportData): void => {
  try {
    // Create worksheet
    const ws = XLSX.utils.aoa_to_sheet([data.headers, ...data.rows]);
    
    // Create workbook
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Report');
    
    // Generate Excel file
    const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
    
    // Save file
    const blob = new Blob([excelBuffer], { type: 'application/octet-stream' });
    saveAs(blob, `${data.fileName}.xlsx`);
  } catch (error) {
    console.error('Failed to generate Excel report:', error);
    throw error;
  }
};

export const generatePDFReport = (data: ReportData): void => {
  try {
    // Create PDF document
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(16);
    doc.text(data.title, 14, 20);
    
    // Add date
    doc.setFontSize(10);
    doc.text(`Generated on: ${new Date().toLocaleString()}`, 14, 30);
    
    // Add table
    (doc as any).autoTable({
      head: [data.headers],
      body: data.rows,
      startY: 35,
      styles: {
        fontSize: 9,
      },
      headStyles: {
        fillColor: [66, 139, 202],
        textColor: 255,
      },
    });
    
    // Save file
    doc.save(`${data.fileName}.pdf`);
  } catch (error) {
    console.error('Failed to generate PDF report:', error);
    throw error;
  }
};
