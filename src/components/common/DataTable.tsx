
import React, { useState } from 'react';
import { 
  Table, 
  TableHeader, 
  TableRow, 
  TableHead, 
  TableBody, 
  TableCell 
} from '@/components/ui/table';
import { Edit, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';

interface Column<T> {
  header: string;
  accessor: keyof T | ((item: T) => React.ReactNode);
  className?: string;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  keyExtractor: (item: T) => string | number;
  onEdit?: (item: T) => void;
  onDelete?: (item: T) => void;
  className?: string;
}

function DataTable<T>({ 
  data, 
  columns, 
  keyExtractor,
  onEdit,
  onDelete,
  className 
}: DataTableProps<T>) {
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<T | null>(null);

  const handleDeleteClick = (item: T) => {
    setItemToDelete(item);
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = () => {
    if (itemToDelete && onDelete) {
      onDelete(itemToDelete);
    }
    setDeleteConfirmOpen(false);
    setItemToDelete(null);
  };

  const renderCell = (item: T, column: Column<T>) => {
    if (typeof column.accessor === 'function') {
      return column.accessor(item);
    } else {
      return item[column.accessor as keyof T];
    }
  };

  return (
    <>
      <div className={`w-full overflow-auto ${className}`}>
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((column, index) => (
                <TableHead key={index} className={column.className}>
                  {column.header}
                </TableHead>
              ))}
              {(onEdit || onDelete) && <TableHead className="w-24">Actions</TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((item) => (
              <TableRow key={keyExtractor(item)}>
                {columns.map((column, index) => (
                  <TableCell key={index} className={column.className}>
                    {renderCell(item, column)}
                  </TableCell>
                ))}
                {(onEdit || onDelete) && (
                  <TableCell className="flex items-center gap-2">
                    {onEdit && (
                      <Button 
                        size="sm" 
                        variant="ghost" 
                        onClick={() => onEdit(item)}
                        className="h-8 w-8 p-0"
                      >
                        <Edit className="h-4 w-4" />
                        <span className="sr-only">Edit</span>
                      </Button>
                    )}
                    {onDelete && (
                      <Button 
                        size="sm" 
                        variant="ghost" 
                        onClick={() => handleDeleteClick(item)} 
                        className="h-8 w-8 p-0 text-destructive hover:bg-destructive/10"
                      >
                        <Trash2 className="h-4 w-4" />
                        <span className="sr-only">Delete</span>
                      </Button>
                    )}
                  </TableCell>
                )}
              </TableRow>
            ))}
            {data.length === 0 && (
              <TableRow>
                <TableCell 
                  colSpan={columns.length + (onEdit || onDelete ? 1 : 0)} 
                  className="h-24 text-center"
                >
                  No records found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Deletion</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this record? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirmOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={confirmDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

export default DataTable;
