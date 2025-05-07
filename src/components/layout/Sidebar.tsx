
import { cn } from "@/lib/utils";
import { Link, useLocation } from "react-router-dom";
import { 
  Truck, 
  Wrench, 
  UserCheck, 
  Package, 
  Users, 
  BarChart3 
} from "lucide-react";

const Sidebar = () => {
  const location = useLocation();
  
  const menuItems = [
    { 
      name: "Trip Management", 
      icon: <Truck className="h-5 w-5" />, 
      path: "/" 
    },
    { 
      name: "Vehicle Maintenance", 
      icon: <Wrench className="h-5 w-5" />, 
      path: "/maintenance" 
    },
    { 
      name: "Driver Payments", 
      icon: <UserCheck className="h-5 w-5" />, 
      path: "/drivers" 
    },
    { 
      name: "Inventory", 
      icon: <Package className="h-5 w-5" />, 
      path: "/inventory" 
    },
    { 
      name: "Customer Ledger", 
      icon: <Users className="h-5 w-5" />, 
      path: "/customers" 
    },
    { 
      name: "Dashboard", 
      icon: <BarChart3 className="h-5 w-5" />, 
      path: "/dashboard" 
    }
  ];

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen w-64 bg-easylogipro-50 border-r border-easylogipro-100">
      <div className="p-4 border-b border-easylogipro-100">
        <h1 className="text-xl font-bold text-easylogipro-900">EasyLogiPro</h1>
        <p className="text-sm text-easylogipro-700">Logistics Management</p>
      </div>
      <nav className="p-2">
        <ul className="space-y-1">
          {menuItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors hover:bg-easylogipro-100",
                  isActive(item.path) 
                    ? "bg-easylogipro-500 text-white hover:bg-easylogipro-600" 
                    : "text-easylogipro-900"
                )}
              >
                {item.icon}
                {item.name}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;
