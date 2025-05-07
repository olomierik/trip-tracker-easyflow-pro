
import React from 'react';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu, 
  DropdownMenuTrigger, 
  DropdownMenuContent, 
  DropdownMenuItem 
} from '@/components/ui/dropdown-menu';
import { FileSpreadsheet, FileText, Download } from 'lucide-react';

interface ExportButtonsProps {
  onExportExcel: () => void;
  onExportPDF: () => void;
  className?: string;
}

const ExportButtons: React.FC<ExportButtonsProps> = ({ 
  onExportExcel, 
  onExportPDF,
  className 
}) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className={className}>
          <Download className="h-4 w-4 mr-2" />
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={onExportExcel}>
          <FileSpreadsheet className="h-4 w-4 mr-2" />
          Export to Excel
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onExportPDF}>
          <FileText className="h-4 w-4 mr-2" />
          Export to PDF
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default ExportButtons;
