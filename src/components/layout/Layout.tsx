
import React from 'react';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
  title: string;
}

const Layout: React.FC<LayoutProps> = ({ children, title }) => {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <header className="bg-white shadow-sm border-b">
          <div className="px-6 py-4">
            <h1 className="text-2xl font-semibold text-easylogipro-900">{title}</h1>
          </div>
        </header>
        <main className="flex-1 p-6">
          {children}
        </main>
        <footer className="bg-white border-t py-4 px-6 text-center text-sm text-gray-500">
          EasyLogiPro &copy; {new Date().getFullYear()} - Logistics Management Software
        </footer>
      </div>
    </div>
  );
};

export default Layout;
