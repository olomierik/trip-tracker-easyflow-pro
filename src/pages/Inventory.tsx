import { useState, useEffect } from 'react';
import Layout from '@/components/layout/Layout';
import DataTable from '@/components/common/DataTable';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogFooter 
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';
import databaseService, { InventoryItem } from '@/services/DatabaseService';

const Inventory = () => {
  const { toast } = useToast();
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentItem, setCurrentItem] = useState<InventoryItem | null>(null);
  
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
  
  // Table columns - fixed to match Column<InventoryItem> type
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
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-medium">Inventory Items</h2>
          <Button onClick={openNewItemModal}>
            <Plus className="h-4 w-4 mr-2" /> Add Item
          </Button>
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
