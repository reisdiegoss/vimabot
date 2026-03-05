import React from 'react';
import { Home } from 'lucide-react';

const TenantDashboard: React.FC = () => {
    return (
        <div className="p-8 text-white">
            <div className="flex items-center gap-3 mb-8">
                <Home className="text-netflix-red" />
                <h1 className="text-2xl font-bold">Resumo Geral</h1>
            </div>
            <div className="bg-slate-900 p-8 rounded-xl border border-slate-800 text-center">
                <h2 className="text-xl font-semibold mb-2">Bem-vindo ao VimaBOT</h2>
                <p className="text-slate-400">Configure seu bot e comece a vender produtos digitais.</p>
            </div>
        </div>
    );
};

export default TenantDashboard;
