
import { useToast } from "@/components/ui/use-toast";

// Types for our data models
export interface Trip {
  id?: number;
  date: string;
  clientName: string;
  cargoType: string;
  route: string;
  tripIncome: number;
  fuelExpenses: number;
  driverName: string;
}

export interface Maintenance {
  id?: number;
  vehiclePlateNumber: string;
  serviceDate: string;
  description: string;
  cost: number;
}

export interface DriverPayment {
  driverName: string;
  tripCount: number;
  totalIncome: number;
  totalExpenses: number;
  netPayment: number;
}

export interface InventoryItem {
  id?: number;
  itemName: string;
  quantity: number;
  purchasePrice: number;
  salePrice: number;
}

export interface CustomerTransaction {
  id?: number;
  customerName: string;
  date: string;
  amountOwed: number;
  amountPaid: number;
}

// Mock database service for frontend demo
class DatabaseService {
  // Trip Management
  private trips: Trip[] = [
    {
      id: 1,
      date: '2024-05-05',
      clientName: 'ABC Shipping',
      cargoType: 'Electronics',
      route: 'New York to Boston',
      tripIncome: 1200,
      fuelExpenses: 250,
      driverName: 'John Smith'
    },
    {
      id: 2,
      date: '2024-05-04',
      clientName: 'XYZ Logistics',
      cargoType: 'Furniture',
      route: 'Chicago to Detroit',
      tripIncome: 950,
      fuelExpenses: 200,
      driverName: 'Sarah Johnson'
    },
    {
      id: 3,
      date: '2024-05-03',
      clientName: 'Global Transports',
      cargoType: 'Food products',
      route: 'Miami to Atlanta',
      tripIncome: 1500,
      fuelExpenses: 320,
      driverName: 'John Smith'
    }
  ];

  // Vehicle Maintenance
  private maintenance: Maintenance[] = [
    {
      id: 1,
      vehiclePlateNumber: 'ABC-1234',
      serviceDate: '2024-04-15',
      description: 'Oil Change',
      cost: 120
    },
    {
      id: 2,
      vehiclePlateNumber: 'XYZ-5678',
      serviceDate: '2024-04-20',
      description: 'Brake Repair',
      cost: 350
    }
  ];

  // Inventory Items
  private inventory: InventoryItem[] = [
    {
      id: 1,
      itemName: 'Engine Oil',
      quantity: 24,
      purchasePrice: 15,
      salePrice: 22
    },
    {
      id: 2,
      itemName: 'Air Filter',
      quantity: 12,
      purchasePrice: 10,
      salePrice: 18
    }
  ];

  // Customer Transactions
  private customerTransactions: CustomerTransaction[] = [
    {
      id: 1,
      customerName: 'ABC Shipping',
      date: '2024-05-01',
      amountOwed: 2500,
      amountPaid: 1500
    },
    {
      id: 2,
      customerName: 'XYZ Logistics',
      date: '2024-05-02',
      amountOwed: 1800,
      amountPaid: 1800
    }
  ];

  // Trip Management Methods
  async getTrips(): Promise<Trip[]> {
    return [...this.trips];
  }

  async addTrip(trip: Trip): Promise<Trip> {
    const newId = this.trips.length > 0 ? Math.max(...this.trips.map(t => t.id || 0)) + 1 : 1;
    const newTrip = { ...trip, id: newId };
    this.trips.push(newTrip);
    return newTrip;
  }

  async updateTrip(trip: Trip): Promise<Trip> {
    const index = this.trips.findIndex(t => t.id === trip.id);
    if (index !== -1) {
      this.trips[index] = trip;
      return trip;
    }
    throw new Error("Trip not found");
  }

  async deleteTrip(id: number): Promise<void> {
    const index = this.trips.findIndex(t => t.id === id);
    if (index !== -1) {
      this.trips.splice(index, 1);
      return;
    }
    throw new Error("Trip not found");
  }

  // Maintenance Methods
  async getMaintenance(): Promise<Maintenance[]> {
    return [...this.maintenance];
  }

  async addMaintenance(record: Maintenance): Promise<Maintenance> {
    const newId = this.maintenance.length > 0 ? 
      Math.max(...this.maintenance.map(m => m.id || 0)) + 1 : 1;
    const newRecord = { ...record, id: newId };
    this.maintenance.push(newRecord);
    return newRecord;
  }

  async updateMaintenance(record: Maintenance): Promise<Maintenance> {
    const index = this.maintenance.findIndex(m => m.id === record.id);
    if (index !== -1) {
      this.maintenance[index] = record;
      return record;
    }
    throw new Error("Maintenance record not found");
  }

  async deleteMaintenance(id: number): Promise<void> {
    const index = this.maintenance.findIndex(m => m.id === id);
    if (index !== -1) {
      this.maintenance.splice(index, 1);
      return;
    }
    throw new Error("Maintenance record not found");
  }

  // Driver Payment Methods
  async getDriverPayments(): Promise<DriverPayment[]> {
    // Group trips by driver and calculate payments
    const driverMap = new Map<string, DriverPayment>();
    
    for (const trip of this.trips) {
      const { driverName, tripIncome, fuelExpenses } = trip;
      
      if (!driverMap.has(driverName)) {
        driverMap.set(driverName, {
          driverName,
          tripCount: 0,
          totalIncome: 0,
          totalExpenses: 0,
          netPayment: 0
        });
      }
      
      const driverData = driverMap.get(driverName)!;
      driverData.tripCount += 1;
      driverData.totalIncome += tripIncome;
      driverData.totalExpenses += fuelExpenses;
      driverData.netPayment = driverData.totalIncome - driverData.totalExpenses;
    }
    
    return Array.from(driverMap.values());
  }

  // Inventory Methods
  async getInventory(): Promise<InventoryItem[]> {
    return [...this.inventory];
  }

  async addInventoryItem(item: InventoryItem): Promise<InventoryItem> {
    const newId = this.inventory.length > 0 ? 
      Math.max(...this.inventory.map(i => i.id || 0)) + 1 : 1;
    const newItem = { ...item, id: newId };
    this.inventory.push(newItem);
    return newItem;
  }

  async updateInventoryItem(item: InventoryItem): Promise<InventoryItem> {
    const index = this.inventory.findIndex(i => i.id === item.id);
    if (index !== -1) {
      this.inventory[index] = item;
      return item;
    }
    throw new Error("Inventory item not found");
  }

  async deleteInventoryItem(id: number): Promise<void> {
    const index = this.inventory.findIndex(i => i.id === id);
    if (index !== -1) {
      this.inventory.splice(index, 1);
      return;
    }
    throw new Error("Inventory item not found");
  }

  // Customer Ledger Methods
  async getCustomerTransactions(): Promise<CustomerTransaction[]> {
    return [...this.customerTransactions];
  }

  async addCustomerTransaction(transaction: CustomerTransaction): Promise<CustomerTransaction> {
    const newId = this.customerTransactions.length > 0 ? 
      Math.max(...this.customerTransactions.map(t => t.id || 0)) + 1 : 1;
    const newTransaction = { ...transaction, id: newId };
    this.customerTransactions.push(newTransaction);
    return newTransaction;
  }

  async updateCustomerTransaction(transaction: CustomerTransaction): Promise<CustomerTransaction> {
    const index = this.customerTransactions.findIndex(t => t.id === transaction.id);
    if (index !== -1) {
      this.customerTransactions[index] = transaction;
      return transaction;
    }
    throw new Error("Customer transaction not found");
  }

  async deleteCustomerTransaction(id: number): Promise<void> {
    const index = this.customerTransactions.findIndex(t => t.id === id);
    if (index !== -1) {
      this.customerTransactions.splice(index, 1);
      return;
    }
    throw new Error("Customer transaction not found");
  }

  // Calculate customer balances
  async getCustomerBalances(): Promise<{ customerName: string, balance: number }[]> {
    const customerMap = new Map<string, number>();
    
    for (const transaction of this.customerTransactions) {
      const { customerName, amountOwed, amountPaid } = transaction;
      
      if (!customerMap.has(customerName)) {
        customerMap.set(customerName, 0);
      }
      
      const currentBalance = customerMap.get(customerName)!;
      customerMap.set(customerName, currentBalance + (amountOwed - amountPaid));
    }
    
    return Array.from(customerMap.entries()).map(([customerName, balance]) => ({
      customerName,
      balance
    }));
  }
}

// Singleton instance
const dbService = new DatabaseService();
export default dbService;
