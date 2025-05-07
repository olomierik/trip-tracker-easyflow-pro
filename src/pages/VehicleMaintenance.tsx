
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
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/use-toast';
import databaseService, { Maintenance } from '@/services/DatabaseService';
import { format } from 'date-fns';

const VehicleMaintenance = () => {
  const { toast } = useToast();
  const [records, setRecords] = useState<Maintenance[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentRecord, setCurrentRecord] = useState<Maintenance | null>(null);
  
  // Form state
  const [vehiclePlateNumber, setVehiclePlateNumber] = useState('');
  const [serviceDate, setServiceDate] = useState('');
  const [description, setDescription] = useState('');
  const [cost, setCost] = useState('');
  
  // Fetch maintenance records
  useEffect(() => {
    const fetchMaintenance = async () => {
      try {
        const data = await databaseService.getMaintenance();
        setRecords(data);
      } catch (error) {
        console.error('Failed to fetch maintenance records:', error);
        toast({
          title: 'Error',
          description: 'Failed to fetch maintenance records.',
          variant: 'destructive',
        });
      }
    };
    
    fetchMaintenance();
  }, [toast]);
  
  // Handle edit
  const handleEdit = (record: Maintenance) => {
    setCurrentRecord(record);
    setVehiclePlateNumber(record.vehiclePlateNumber);
    setServiceDate(record.serviceDate);
    setDescription(record.description);
    setCost(record.cost.toString());
    setIsModalOpen(true);
  };
  
  // Handle delete
  const handleDelete = async (record: Maintenance) => {
    if (!record.id) return;
    
    try {
      await databaseService.deleteMaintenance(record.id);
      setRecords(records.filter(r => r.id !== record.id));
      toast({
        title: 'Success',
        description: 'Maintenance record deleted successfully.',
      });
    } catch (error) {
      console.error('Failed to delete maintenance record:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete maintenance record.',
        variant: 'destructive',
      });
    }
  };
  
  // Reset form
  const resetForm = () => {
    setCurrentRecord(null);
    setVehiclePlateNumber('');
    setServiceDate('');
    setDescription('');
    setCost('');
  };
  
  // Open modal for new maintenance record
  const openNewMaintenanceModal = () => {
    resetForm();
    setServiceDate(format(new Date(), 'yyyy-MM-dd'));
    setIsModalOpen(true);
  };
  
  // Submit form
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!vehiclePlateNumber || !serviceDate || !description || !cost) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields.',
        variant: 'destructive',
      });
      return;
    }
    
    setIsLoading(true);
    
    try {
      const recordData: Maintenance = {
        id: currentRecord?.id,
        vehiclePlateNumber,
        serviceDate,
        description,
        cost: parseFloat(cost),
      };
      
      let updatedRecord;
      
      if (currentRecord?.id) {
        updatedRecord = await databaseService.updateMaintenance(recordData);
        setRecords(records.map(r => r.id === updatedRecord.id ? updatedRecord : r));
        toast({
          title: 'Success',
          description: 'Maintenance record updated successfully.',
        });
      } else {
        updatedRecord = await databaseService.addMaintenance(recordData);
        setRecords([...records, updatedRecord]);
        toast({
          title: 'Success',
          description: 'Maintenance record added successfully.',
        });
      }
      
      setIsModalOpen(false);
      resetForm();
    } catch (error) {
      console.error('Failed to save maintenance record:', error);
      toast({
        title: 'Error',
        description: 'Failed to save maintenance record.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Table columns
  const columns = [
    { 
      header: 'Vehicle Plate', 
      accessor: 'vehiclePlateNumber' 
    },
    { 
      header: 'Service Date', 
      accessor: 'serviceDate' 
    },
    { 
      header: 'Description', 
      accessor: 'description' 
    },
    { 
      header: 'Cost', 
      accessor: (record: Maintenance) => `$${record.cost.toFixed(2)}`,
      className: 'text-right'
    }
  ];
  
  return (
    <Layout title="Vehicle Maintenance">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-medium">Maintenance Records</h2>
          <Button onClick={openNewMaintenanceModal}>
            <Plus className="h-4 w-4 mr-2" /> Add Maintenance
          </Button>
        </div>
        
        <DataTable
          data={records}
          columns={columns}
          keyExtractor={(record) => record.id || 0}
          onEdit={handleEdit}
          onDelete={handleDelete}
          className="border rounded-md"
        />
      </div>
      
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>
              {currentRecord ? 'Edit Maintenance Record' : 'Add Maintenance Record'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="vehiclePlateNumber">Vehicle Plate Number</Label>
                  <Input
                    id="vehiclePlateNumber"
                    value={vehiclePlateNumber}
                    onChange={(e) => setVehiclePlateNumber(e.target.value)}
                    placeholder="ABC-1234"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="serviceDate">Service Date</Label>
                  <Input
                    id="serviceDate"
                    type="date"
                    value={serviceDate}
                    onChange={(e) => setServiceDate(e.target.value)}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Maintenance description..."
                  rows={3}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="cost">Cost ($)</Label>
                <Input
                  id="cost"
                  type="number"
                  value={cost}
                  onChange={(e) => setCost(e.target.value)}
                  placeholder="0.00"
                  step="0.01"
                  min="0"
                />
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
                {isLoading ? 'Saving...' : currentRecord ? 'Update' : 'Add'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </Layout>
  );
};

export default VehicleMaintenance;
