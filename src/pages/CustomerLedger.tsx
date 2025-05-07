
import { useState, useEffect } from 'react';
import Layout from '@/components/layout/Layout';
import DataTable from '@/components/common/DataTable';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import databaseService, { CustomerTransaction } from '@/services/DatabaseService';
import { format } from 'date-fns';

const CustomerLedger = () => {
  const { toast } = useToast();
  const [transactions, setTransactions] = useState<CustomerTransaction[]>([]);
  const [customerBalances, setCustomerBalances] = useState<{ customerName: string, balance: number }[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentTransaction, setCurrentTransaction] = useState<CustomerTransaction | null>(null);
  
  // Form state
  const [customerName, setCustomerName] = useState('');
  const [date, setDate] = useState('');
  const [amountOwed, setAmountOwed] = useState('');
  const [amountPaid, setAmountPaid] = useState('');
  
  // Fetch customer data
  useEffect(() => {
    const fetchCustomerData = async () => {
      try {
        const transactionsData = await databaseService.getCustomerTransactions();
        setTransactions(transactionsData);
        
        const balancesData = await databaseService.getCustomerBalances();
        setCustomerBalances(balancesData);
      } catch (error) {
        console.error('Failed to fetch customer data:', error);
        toast({
          title: 'Error',
          description: 'Failed to fetch customer data.',
          variant: 'destructive',
        });
      }
    };
    
    fetchCustomerData();
  }, [toast]);
  
  // Handle edit
  const handleEdit = (transaction: CustomerTransaction) => {
    setCurrentTransaction(transaction);
    setCustomerName(transaction.customerName);
    setDate(transaction.date);
    setAmountOwed(transaction.amountOwed.toString());
    setAmountPaid(transaction.amountPaid.toString());
    setIsModalOpen(true);
  };
  
  // Handle delete
  const handleDelete = async (transaction: CustomerTransaction) => {
    if (!transaction.id) return;
    
    try {
      await databaseService.deleteCustomerTransaction(transaction.id);
      setTransactions(transactions.filter(t => t.id !== transaction.id));
      
      // Refresh customer balances
      const balancesData = await databaseService.getCustomerBalances();
      setCustomerBalances(balancesData);
      
      toast({
        title: 'Success',
        description: 'Transaction deleted successfully.',
      });
    } catch (error) {
      console.error('Failed to delete transaction:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete transaction.',
        variant: 'destructive',
      });
    }
  };
  
  // Reset form
  const resetForm = () => {
    setCurrentTransaction(null);
    setCustomerName('');
    setDate('');
    setAmountOwed('');
    setAmountPaid('');
  };
  
  // Open modal for new transaction
  const openNewTransactionModal = () => {
    resetForm();
    setDate(format(new Date(), 'yyyy-MM-dd'));
    setIsModalOpen(true);
  };
  
  // Submit form
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!customerName || !date || (amountOwed === '' && amountPaid === '')) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields.',
        variant: 'destructive',
      });
      return;
    }
    
    setIsLoading(true);
    
    try {
      const transactionData: CustomerTransaction = {
        id: currentTransaction?.id,
        customerName,
        date,
        amountOwed: parseFloat(amountOwed || '0'),
        amountPaid: parseFloat(amountPaid || '0'),
      };
      
      let updatedTransaction;
      
      if (currentTransaction?.id) {
        updatedTransaction = await databaseService.updateCustomerTransaction(transactionData);
        setTransactions(transactions.map(t => 
          t.id === updatedTransaction.id ? updatedTransaction : t
        ));
        toast({
          title: 'Success',
          description: 'Transaction updated successfully.',
        });
      } else {
        updatedTransaction = await databaseService.addCustomerTransaction(transactionData);
        setTransactions([...transactions, updatedTransaction]);
        toast({
          title: 'Success',
          description: 'Transaction added successfully.',
        });
      }
      
      // Refresh customer balances
      const balancesData = await databaseService.getCustomerBalances();
      setCustomerBalances(balancesData);
      
      setIsModalOpen(false);
      resetForm();
    } catch (error) {
      console.error('Failed to save transaction:', error);
      toast({
        title: 'Error',
        description: 'Failed to save transaction.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Table columns for transactions
  const transactionColumns = [
    { 
      header: 'Date', 
      accessor: 'date' 
    },
    { 
      header: 'Customer Name', 
      accessor: 'customerName' 
    },
    { 
      header: 'Amount Owed', 
      accessor: (transaction: CustomerTransaction) => 
        `$${transaction.amountOwed.toFixed(2)}`,
      className: 'text-right'
    },
    { 
      header: 'Amount Paid', 
      accessor: (transaction: CustomerTransaction) => 
        `$${transaction.amountPaid.toFixed(2)}`,
      className: 'text-right'
    },
    { 
      header: 'Balance', 
      accessor: (transaction: CustomerTransaction) => 
        `$${(transaction.amountOwed - transaction.amountPaid).toFixed(2)}`,
      className: 'text-right font-medium'
    }
  ];
  
  // Table columns for balances
  const balanceColumns = [
    { 
      header: 'Customer Name', 
      accessor: 'customerName' 
    },
    { 
      header: 'Balance', 
      accessor: (record: { customerName: string, balance: number }) => 
        `$${record.balance.toFixed(2)}`,
      className: 'text-right font-medium'
    }
  ];
  
  // Calculate totals
  const totalOwed = transactions.reduce((sum, transaction) => sum + transaction.amountOwed, 0);
  const totalPaid = transactions.reduce((sum, transaction) => sum + transaction.amountPaid, 0);
  const totalBalance = totalOwed - totalPaid;
  
  return (
    <Layout title="Customer Ledger">
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Owed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${totalOwed.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground">
                Total amount customers owe
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Paid</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${totalPaid.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground">
                Total amount received from customers
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Outstanding Balance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${totalBalance.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground">
                Total unpaid balance
              </p>
            </CardContent>
          </Card>
        </div>
        
        <Tabs defaultValue="transactions" className="space-y-4">
          <div className="flex justify-between items-center">
            <TabsList>
              <TabsTrigger value="transactions">Transactions</TabsTrigger>
              <TabsTrigger value="balances">Customer Balances</TabsTrigger>
            </TabsList>
            <Button onClick={openNewTransactionModal}>
              <Plus className="h-4 w-4 mr-2" /> Add Transaction
            </Button>
          </div>
          
          <TabsContent value="transactions" className="space-y-4">
            <DataTable
              data={transactions}
              columns={transactionColumns}
              keyExtractor={(transaction) => transaction.id || 0}
              onEdit={handleEdit}
              onDelete={handleDelete}
              className="border rounded-md"
            />
          </TabsContent>
          
          <TabsContent value="balances" className="space-y-4">
            <DataTable
              data={customerBalances}
              columns={balanceColumns}
              keyExtractor={(record) => record.customerName}
              className="border rounded-md"
            />
          </TabsContent>
        </Tabs>
      </div>
      
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>
              {currentTransaction ? 'Edit Transaction' : 'Add Transaction'}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="customerName">Customer Name</Label>
                  <Input
                    id="customerName"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    placeholder="Customer name..."
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="date">Date</Label>
                  <Input
                    id="date"
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="amountOwed">Amount Owed ($)</Label>
                  <Input
                    id="amountOwed"
                    type="number"
                    value={amountOwed}
                    onChange={(e) => setAmountOwed(e.target.value)}
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="amountPaid">Amount Paid ($)</Label>
                  <Input
                    id="amountPaid"
                    type="number"
                    value={amountPaid}
                    onChange={(e) => setAmountPaid(e.target.value)}
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
                {isLoading ? 'Saving...' : currentTransaction ? 'Update' : 'Add'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </Layout>
  );
};

export default CustomerLedger;
