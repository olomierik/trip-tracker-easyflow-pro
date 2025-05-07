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
import databaseService, { Trip } from '@/services/DatabaseService';
import { format } from 'date-fns';
import { generateExcelReport, generatePDFReport } from '@/utils/reportUtils';

const TripManagement = () => {
  const { toast } = useToast();
  const [trips, setTrips] = useState<Trip[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentTrip, setCurrentTrip] = useState<Trip | null>(null);
  
  // Form state
  const [date, setDate] = useState('');
  const [clientName, setClientName] = useState('');
  const [cargoType, setCargoType] = useState('');
  const [route, setRoute] = useState('');
  const [tripIncome, setTripIncome] = useState('');
  const [fuelExpenses, setFuelExpenses] = useState('');
  const [driverName, setDriverName] = useState('');
  
  // Fetch trips
  useEffect(() => {
    const fetchTrips = async () => {
      try {
        const data = await databaseService.getTrips();
        setTrips(data);
      } catch (error) {
        console.error('Failed to fetch trips:', error);
        toast({
          title: 'Error',
          description: 'Failed to fetch trip records.',
          variant: 'destructive',
        });
      }
    };
    
    fetchTrips();
  }, [toast]);
  
  // Handle export to Excel
  const handleExportExcel = () => {
    try {
      const headers = ['Date', 'Client Name', 'Cargo Type', 'Route', 'Income (TSh)', 'Fuel Expenses (TSh)', 'Driver'];
      const rows = trips.map(trip => [
        trip.date,
        trip.clientName,
        trip.cargoType,
        trip.route,
        trip.tripIncome.toFixed(2),
        trip.fuelExpenses.toFixed(2),
        trip.driverName
      ]);

      generateExcelReport({
        headers,
        rows,
        title: 'Trip Records Report',
        fileName: `trip-records-${new Date().toISOString().split('T')[0]}`
      });

      toast({
        title: 'Success',
        description: 'Trip records exported to Excel successfully.',
      });
    } catch (error) {
      console.error('Failed to export to Excel:', error);
      toast({
        title: 'Error',
        description: 'Failed to export trip records.',
        variant: 'destructive',
      });
    }
  };

  // Handle export to PDF
  const handleExportPDF = () => {
    try {
      const headers = ['Date', 'Client', 'Cargo', 'Route', 'Income (TSh)', 'Expenses (TSh)', 'Driver'];
      const rows = trips.map(trip => [
        trip.date,
        trip.clientName,
        trip.cargoType,
        trip.route,
        trip.tripIncome.toFixed(2),
        trip.fuelExpenses.toFixed(2),
        trip.driverName
      ]);

      generatePDFReport({
        headers,
        rows,
        title: 'Trip Records Report',
        fileName: `trip-records-${new Date().toISOString().split('T')[0]}`
      });

      toast({
        title: 'Success',
        description: 'Trip records exported to PDF successfully.',
      });
    } catch (error) {
      console.error('Failed to export to PDF:', error);
      toast({
        title: 'Error',
        description: 'Failed to export trip records.',
        variant: 'destructive',
      });
    }
  };
  
  // Handle edit
  const handleEdit = (trip: Trip) => {
    setCurrentTrip(trip);
    setDate(trip.date);
    setClientName(trip.clientName);
    setCargoType(trip.cargoType);
    setRoute(trip.route);
    setTripIncome(trip.tripIncome.toString());
    setFuelExpenses(trip.fuelExpenses.toString());
    setDriverName(trip.driverName);
    setIsModalOpen(true);
  };
  
  // Handle delete
  const handleDelete = async (trip: Trip) => {
    if (!trip.id) return;
    
    try {
      await databaseService.deleteTrip(trip.id);
      setTrips(trips.filter(t => t.id !== trip.id));
      toast({
        title: 'Success',
        description: 'Trip record deleted successfully.',
      });
    } catch (error) {
      console.error('Failed to delete trip:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete trip record.',
        variant: 'destructive',
      });
    }
  };
  
  // Reset form
  const resetForm = () => {
    setCurrentTrip(null);
    setDate('');
    setClientName('');
    setCargoType('');
    setRoute('');
    setTripIncome('');
    setFuelExpenses('');
    setDriverName('');
  };
  
  // Open modal for new trip
  const openNewTripModal = () => {
    resetForm();
    setDate(format(new Date(), 'yyyy-MM-dd'));
    setIsModalOpen(true);
  };
  
  // Submit form
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!date || !clientName || !cargoType || !route || !tripIncome || !fuelExpenses || !driverName) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields.',
        variant: 'destructive',
      });
      return;
    }
    
    setIsLoading(true);
    
    try {
      const tripData: Trip = {
        id: currentTrip?.id,
        date,
        clientName,
        cargoType,
        route,
        tripIncome: parseFloat(tripIncome),
        fuelExpenses: parseFloat(fuelExpenses),
        driverName,
      };
      
      let updatedTrip;
      
      if (currentTrip?.id) {
        updatedTrip = await databaseService.updateTrip(tripData);
        setTrips(trips.map(t => t.id === updatedTrip.id ? updatedTrip : t));
        toast({
          title: 'Success',
          description: 'Trip record updated successfully.',
        });
      } else {
        updatedTrip = await databaseService.addTrip(tripData);
        setTrips([...trips, updatedTrip]);
        toast({
          title: 'Success',
          description: 'Trip record added successfully.',
        });
      }
      
      setIsModalOpen(false);
      resetForm();
    } catch (error) {
      console.error('Failed to save trip:', error);
      toast({
        title: 'Error',
        description: 'Failed to save trip record.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Table columns - fixed to match Column<Trip> type
  const columns = [
    { 
      header: 'Date', 
      accessor: 'date' as keyof Trip
    },
    { 
      header: 'Client Name', 
      accessor: 'clientName' as keyof Trip
    },
    { 
      header: 'Cargo Type', 
      accessor: 'cargoType' as keyof Trip
    },
    { 
      header: 'Route', 
      accessor: 'route' as keyof Trip
    },
    { 
      header: 'Income', 
      accessor: (trip: Trip) => `TSh ${trip.tripIncome.toFixed(2)}`,
      className: 'text-right'
    },
    { 
      header: 'Fuel Expenses', 
      accessor: (trip: Trip) => `TSh ${trip.fuelExpenses.toFixed(2)}`,
      className: 'text-right'
    },
    { 
      header: 'Driver', 
      accessor: 'driverName' as keyof Trip
    }
  ];
  
  return (
    <Layout title="Trip Management">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-medium">Trip Records</h2>
          <div className="flex space-x-2">
            <ExportButtons 
              onExportExcel={handleExportExcel} 
              onExportPDF={handleExportPDF} 
            />
            <Button onClick={openNewTripModal}>
              <Plus className="h-4 w-4 mr-2" /> Add Trip
            </Button>
          </div>
        </div>
        
        <DataTable
          data={trips}
          columns={columns}
          keyExtractor={(trip) => trip.id || 0}
          onEdit={handleEdit}
          onDelete={handleDelete}
          className="border rounded-md"
        />
      </div>
      
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[550px]">
          <DialogHeader>
            <DialogTitle>
              {currentTrip ? 'Edit Trip Record' : 'Add Trip Record'}
            </DialogTitle>
            <DialogDescription>
              Enter the trip details below.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="date">Date</Label>
                  <Input
                    id="date"
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="clientName">Client Name</Label>
                  <Input
                    id="clientName"
                    value={clientName}
                    onChange={(e) => setClientName(e.target.value)}
                    placeholder="Client name..."
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="cargoType">Cargo Type</Label>
                <Input
                  id="cargoType"
                  value={cargoType}
                  onChange={(e) => setCargoType(e.target.value)}
                  placeholder="Type of cargo..."
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="route">Route</Label>
                <Input
                  id="route"
                  value={route}
                  onChange={(e) => setRoute(e.target.value)}
                  placeholder="Origin to destination..."
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="tripIncome">Trip Income (TSh)</Label>
                  <Input
                    id="tripIncome"
                    type="number"
                    value={tripIncome}
                    onChange={(e) => setTripIncome(e.target.value)}
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="fuelExpenses">Fuel Expenses (TSh)</Label>
                  <Input
                    id="fuelExpenses"
                    type="number"
                    value={fuelExpenses}
                    onChange={(e) => setFuelExpenses(e.target.value)}
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="driverName">Driver Name</Label>
                <Input
                  id="driverName"
                  value={driverName}
                  onChange={(e) => setDriverName(e.target.value)}
                  placeholder="Driver name..."
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
                {isLoading ? 'Saving...' : currentTrip ? 'Update' : 'Add'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </Layout>
  );
};

export default TripManagement;
