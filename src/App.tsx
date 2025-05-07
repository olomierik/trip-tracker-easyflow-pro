
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import TripManagement from "./pages/TripManagement";
import VehicleMaintenance from "./pages/VehicleMaintenance";
import DriverPayments from "./pages/DriverPayments";
import Inventory from "./pages/Inventory";
import CustomerLedger from "./pages/CustomerLedger";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<TripManagement />} />
          <Route path="/maintenance" element={<VehicleMaintenance />} />
          <Route path="/drivers" element={<DriverPayments />} />
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/customers" element={<CustomerLedger />} />
          <Route path="/dashboard" element={<Dashboard />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
