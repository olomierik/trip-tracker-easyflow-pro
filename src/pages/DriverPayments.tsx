
import { useState, useEffect } from 'react';
import Layout from '@/components/layout/Layout';
import DataTable from '@/components/common/DataTable';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import databaseService, { DriverPayment } from '@/services/DatabaseService';

const DriverPayments = () => {
  const { toast } = useToast();
  const [driverPayments, setDriverPayments] = useState<DriverPayment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [totalDrivers, setTotalDrivers] = useState(0);
  const [totalTrips, setTotalTrips] = useState(0);
  const [totalPayments, setTotalPayments] = useState(0);
  
  // Fetch driver payments
  useEffect(() => {
    const fetchDriverPayments = async () => {
      try {
        setIsLoading(true);
        const data = await databaseService.getDriverPayments();
        setDriverPayments(data);
        
        // Calculate totals
        setTotalDrivers(data.length);
        setTotalTrips(data.reduce((sum, driver) => sum + driver.tripCount, 0));
        setTotalPayments(data.reduce((sum, driver) => sum + driver.netPayment, 0));
      } catch (error) {
        console.error('Failed to fetch driver payments:', error);
        toast({
          title: 'Error',
          description: 'Failed to fetch driver payment data.',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDriverPayments();
  }, [toast]);
  
  // Table columns
  const columns = [
    { 
      header: 'Driver Name', 
      accessor: 'driverName' 
    },
    { 
      header: 'Trips', 
      accessor: 'tripCount',
      className: 'text-center'
    },
    { 
      header: 'Total Income', 
      accessor: (driver: DriverPayment) => `$${driver.totalIncome.toFixed(2)}`,
      className: 'text-right'
    },
    { 
      header: 'Total Expenses', 
      accessor: (driver: DriverPayment) => `$${driver.totalExpenses.toFixed(2)}`,
      className: 'text-right'
    },
    { 
      header: 'Net Payment', 
      accessor: (driver: DriverPayment) => `$${driver.netPayment.toFixed(2)}`,
      className: 'text-right font-medium'
    }
  ];
  
  return (
    <Layout title="Driver Payments">
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Drivers</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalDrivers}</div>
              <p className="text-xs text-muted-foreground">
                Active drivers in the system
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Trips</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalTrips}</div>
              <p className="text-xs text-muted-foreground">
                Completed trips by all drivers
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Net Payments</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${totalPayments.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground">
                Combined driver payments
              </p>
            </CardContent>
          </Card>
        </div>
        
        <div className="space-y-4">
          <h2 className="text-lg font-medium">Driver Payment Summary</h2>
          <Card>
            <CardContent className="p-4">
              <DataTable
                data={driverPayments}
                columns={columns}
                keyExtractor={(driver) => driver.driverName}
                className="border-0"
              />
            </CardContent>
          </Card>
          
          <p className="text-sm text-muted-foreground">
            Note: Net Payment is calculated as Trip Income minus Fuel Expenses.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default DriverPayments;
