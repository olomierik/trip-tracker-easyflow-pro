
import { useState, useEffect } from 'react';
import Layout from '@/components/layout/Layout';
import DataTable from '@/components/common/DataTable';
import ExportButtons from '@/components/common/ExportButtons';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogFooter,
  DialogDescription
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';
import databaseService, { InventoryItem } from '@/services/DatabaseService';
import { generateExcelReport, generatePDFReport } from '@/utils/reportUtils';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

const LOW_STOCK_THRESHOLD = 5; // Set threshold for low stock alert

const Inventory = () => {
  const { toast } = useToast();
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentItem, setCurrentItem] = useState<InventoryItem | null>(null);
  const [lowStockItems, setLowStockItems] = useState<InventoryItem[]>([]);
  
  // Form state
  const [itemName, setItemName] = useState('');
  const [quantity, setQuantity] = useState('');
  const [purchasePrice, setPurchasePrice] = useState('');
  const [salePrice, setSalePrice] = useState('');
  
  // Fetch inventory items
  useEffect(() => {
    const fetchInventory = async () => {
      try {
        const data = await databaseService.getInventory();
        setItems(data);
        
        // Check for low stock items
        const lowStock = data.filter(item => item.quantity <= LOW_STOCK_THRESHOLD);
        setLowStockItems(lowStock);
        
        // Show toast notification for low stock items if any
        if (lowStock.length > 0) {
          toast({
            title: "Low Stock Alert",
            description: `${lowStock.length} item(s) are running low on stock.`,
            variant: "warning",
          });
        }
      } catch (error) {
        console.error('Failed to fetch inventory:', error);
        toast({
          title: 'Error',
          description: 'Failed to fetch inventory items.',
          variant: 'destructive',
        });
      }
    };
    
    fetchInventory();
  }, [toast]);
  
  // Handle export to Excel
  const handleExportExcel = () => {
    try {
      const headers = ['Item Name', 'Quantity', 'Purchase Price (TSh)', 'Sale Price (TSh)', 'Profit Margin (%)'];
      const rows = items.map(item => [
        item.itemName,
        item.quantity,
        item.purchasePrice.toFixed(2),
        item.salePrice.toFixed(2),
        calculateMargin(item.purchasePrice, item.salePrice)
      ]);

      generateExcelReport({
        headers,
        rows,
        title: 'Inventory Report',
        fileName: `inventory-${new Date().toISOString().split('T')[0]}`
      });

      toast({
        title: 'Success',
        description: 'Inventory exported to Excel successfully.',
      });
    } catch (error) {
      console.error('Failed to export to Excel:', error);
      toast({
        title: 'Error',
        description: 'Failed to export inventory.',
        variant: 'destructive',
      });
    }
  };

  // Handle export to PDF
  const handleExportPDF = () => {
    try {
      const headers = ['Item Name', 'Quantity', 'Purchase Price (TSh)', 'Sale Price (TSh)', 'Profit Margin'];
      const rows = items.map(item => [
        item.itemName,
        item.quantity,
        item.purchasePrice.toFixed(2),
        item.salePrice.toFixed(2),
        calculateMargin(item.purchasePrice, item.salePrice)
      ]);

      generatePDFReport({
        headers,
        rows,
        title: 'Inventory Report',
        fileName: `inventory-${new Date().toISOString().split('T')[0]}`
      });

      toast({
        title: 'Success',
        description: 'Inventory exported to PDF successfully.',
      });
    } catch (error) {
      console.error('Failed to export to PDF:', error);
      toast({
        title: 'Error',
        description: 'Failed to export inventory.',
        variant: 'destructive',
      });
    }
  };
  
  // Handle edit
  const handleEdit = (item: InventoryItem) => {
    setCurrentItem(item);
    setItemName(item.itemName);
    setQuantity(item.quantity.toString());
    setPurchasePrice(item.purchasePrice.toString());
    setSalePrice(item.salePrice.toString());
    setIsModalOpen(true);
  };
  
  // Handle delete
  const handleDelete = async (item: InventoryItem) => {
    if (!item.id) return;
    
    try {
      await databaseService.deleteInventoryItem(item.id);
      setItems(items.filter(i => i.id !== item.id));
      toast({
        title: 'Success',
        description: 'Inventory item deleted successfully.',
      });
    } catch (error) {
      console.error('Failed to delete inventory item:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete inventory item.',
        variant: 'destructive',
      });
    }
  };
  
  // Reset form
  const resetForm = () => {
    setCurrentItem(null);
    setItemName('');
    setQuantity('');
    setPurchasePrice('');
    setSalePrice('');
  };
  
  // Open modal for new item
  const openNewItemModal = () => {
    resetForm();
    setIsModalOpen(true);
  };
  
  // Submit form
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!itemName || !quantity || !purchasePrice || !salePrice) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields.',
        variant: 'destructive',
      });
      return;
    }
    
    setIsLoading(true);
    
    try {
      const itemData: InventoryItem = {
        id: currentItem?.id,
        itemName,
        quantity: parseInt(quantity),
        purchasePrice: parseFloat(purchasePrice),
        salePrice: parseFloat(salePrice),
      };
      
      let updatedItem;
      
      if (currentItem?.id) {
        updatedItem = await databaseService.updateInventoryItem(itemData);
        setItems(items.map(i => i.id === updatedItem.id ? updatedItem : i));
        toast({
          title: 'Success',
          description: 'Inventory item updated successfully.',
        });
      } else {
        updatedItem = await databaseService.addInventoryItem(itemData);
        setItems([...items, updatedItem]);
        toast({
          title: 'Success',
          description: 'Inventory item added successfully.',
        });
      }
      
      setIsModalOpen(false);
      resetForm();
    } catch (error) {
      console.error('Failed to save inventory item:', error);
      toast({
        title: 'Error',
        description: 'Failed to save inventory item.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Calculate profit margin
  const calculateMargin = (purchase: number, sale: number) => {
    const margin = ((sale - purchase) / purchase) * 100;
    return `${margin.toFixed(1)}%`;
  };
  
  // Table columns
  const columns = [
    { 
      header: 'Item Name', 
      accessor: 'itemName' as keyof InventoryItem
    },
    { 
      header: 'Quantity', 
      accessor: 'quantity' as keyof InventoryItem,
      className: 'text-center'
    },
    { 
      header: 'Purchase Price', 
      accessor: (item: InventoryItem) => `TSh ${item.purchasePrice.toFixed(2)}`,
      className: 'text-right'
    },
    { 
      header: 'Sale Price', 
      accessor: (item: InventoryItem) => `TSh ${item.salePrice.toFixed(2)}`,
      className: 'text-right'
    },
    { 
      header: 'Profit Margin', 
      accessor: (item: InventoryItem) => calculateMargin(item.purchasePrice, item.salePrice),
      className: 'text-right'
    }
  ];
  
  return (
    <Layout title="Inventory Management">
      <div className="space-y-4">
        {lowStockItems.length > 0 && (
          <Alert variant="warning" className="bg-yellow-50 border-yellow-200">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Low Stock Alert</AlertTitle>
            <AlertDescription>
              {lowStockItems.length} item(s) are running low on stock (below {LOW_STOCK_THRESHOLD} units):
              {' '}
              {lowStockItems.map(item => item.itemName).join(', ')}
            </AlertDescription>
          </Alert>
        )}
      
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-medium">Inventory Items</h2>
          <div className="flex space-x-2">
            <ExportButtons 
              onExportExcel={handleExportExcel} 
              onExportPDF={handleExportPDF} 
            />
            <Button onClick={openNewItemModal}>
              <Plus className="h-4 w-4 mr-2" /> Add Item
            </Button>
          </div>
        </div>
        
        <DataTable
          data={items}
          columns={columns}
          keyExtractor={(item) => item.id || 0}
          onEdit={handleEdit}
          onDelete={handleDelete}
          className="border rounded-md"
        />
      </div>
      
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>
              {currentItem ? 'Edit Inventory Item' : 'Add Inventory Item'}
            </DialogTitle>
            <DialogDescription>
              Enter the inventory item details below.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="itemName">Item Name</Label>
                <Input
                  id="itemName"
                  value={itemName}
                  onChange={(e) => setItemName(e.target.value)}
                  placeholder="Item name..."
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="quantity">Quantity</Label>
                <Input
                  id="quantity"
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  placeholder="0"
                  min="0"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="purchasePrice">Purchase Price (TSh)</Label>
                  <Input
                    id="purchasePrice"
                    type="number"
                    value={purchasePrice}
                    onChange={(e) => setPurchasePrice(e.target.value)}
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="salePrice">Sale Price (TSh)</Label>
                  <Input
                    id="salePrice"
                    type="number"
                    value={salePrice}
                    onChange={(e) => setSalePrice(e.target.value)}
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                  />
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setIsModalOpen(false)}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Saving...' : currentItem ? 'Update' : 'Add'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </Layout>
  );
};

export default Inventory;
