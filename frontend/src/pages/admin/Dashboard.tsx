import React from 'react';
import { LayoutDashboard } from 'lucide-react';

const AdminDashboard: React.FC = () => {
    return (
        <div className="p-8 text-white">
            <div className="flex items-center gap-3 mb-8">
                <LayoutDashboard className="text-netflix-red" />
                <h1 className="text-2xl font-bold">Dashboard Super-Admin</h1>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900 p-6 rounded-xl border border-slate-800">
                    <p className="text-slate-400 text-sm">Total de Clientes</p>
                    <h2 className="text-3xl font-bold mt-2">0</h2>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
