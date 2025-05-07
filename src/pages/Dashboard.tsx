
import { useState, useEffect } from 'react';
import Layout from '@/components/layout/Layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { useToast } from '@/components/ui/use-toast';
import databaseService, { Trip, DriverPayment, Maintenance } from '@/services/DatabaseService';

const Dashboard = () => {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [totalTrips, setTotalTrips] = useState(0);
  const [totalIncome, setTotalIncome] = useState(0);
  const [totalExpenses, setTotalExpenses] = useState(0);
  const [netProfit, setNetProfit] = useState(0);
  const [maintenanceCost, setMaintenanceCost] = useState(0);
  const [driverPayments, setDriverPayments] = useState<DriverPayment[]>([]);
  const [trips, setTrips] = useState<Trip[]>([]);
  const [maintenance, setMaintenance] = useState<Maintenance[]>([]);
  
  // Color constants
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];
  
  // Fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        
        // Fetch trips data
        const tripsData = await databaseService.getTrips();
        setTrips(tripsData);
        setTotalTrips(tripsData.length);
        
        // Calculate income and expenses
        const income = tripsData.reduce((sum, trip) => sum + trip.tripIncome, 0);
        const expenses = tripsData.reduce((sum, trip) => sum + trip.fuelExpenses, 0);
        
        setTotalIncome(income);
        setTotalExpenses(expenses);
        
        // Fetch maintenance data
        const maintenanceData = await databaseService.getMaintenance();
        setMaintenance(maintenanceData);
        const maintCost = maintenanceData.reduce((sum, record) => sum + record.cost, 0);
        setMaintenanceCost(maintCost);
        
        // Calculate net profit
        setNetProfit(income - expenses - maintCost);
        
        // Fetch driver payments
        const driversData = await databaseService.getDriverPayments();
        setDriverPayments(driversData);
        
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load dashboard data.',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, [toast]);
  
  // Prepare data for driver trips chart
  const driverTripsData = driverPayments.map(driver => ({
    name: driver.driverName,
    trips: driver.tripCount
  }));
  
  // Prepare data for income/expense chart
  const incomeExpenseData = [
    { name: 'Income', value: totalIncome },
    { name: 'Fuel', value: totalExpenses },
    { name: 'Maintenance', value: maintenanceCost }
  ];
  
  // Prepare data for maintenance cost chart
  const maintenanceChartData = maintenance.map(record => ({
    name: record.description,
    cost: record.cost
  }));
  
  return (
    <Layout title="Dashboard">
      <div className="space-y-6">
        {/* Summary cards */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Trips</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalTrips}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Income</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${totalIncome.toFixed(2)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Expenses</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${(totalExpenses + maintenanceCost).toFixed(2)}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Net Profit</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${netProfit.toFixed(2)}</div>
            </CardContent>
          </Card>
        </div>
        
        {/* Charts */}
        <div className="grid gap-4 md:grid-cols-2">
          {/* Driver Trips Chart */}
          <Card className="col-span-1">
            <CardHeader>
              <CardTitle>Trips by Driver</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={driverTripsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="trips" fill="#0c99ea" name="Trips" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          
          {/* Income vs Expense Chart */}
          <Card className="col-span-1">
            <CardHeader>
              <CardTitle>Income vs Expenses</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={incomeExpenseData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {incomeExpenseData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `$${Number(value).toFixed(2)}`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          
          {/* Maintenance Cost Chart */}
          <Card className="col-span-2">
            <CardHeader>
              <CardTitle>Maintenance Costs</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={maintenanceChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => `$${Number(value).toFixed(2)}`} />
                  <Legend />
                  <Bar dataKey="cost" fill="#82ca9d" name="Cost" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
