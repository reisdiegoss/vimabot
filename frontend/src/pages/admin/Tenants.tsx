import React from 'react';
import { Users } from 'lucide-react';

const AdminTenants: React.FC = () => {
    return (
        <div className="p-8 text-white">
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <Users className="text-netflix-red" />
                    <h1 className="text-2xl font-bold">Gestão de Clientes</h1>
                </div>
                <button className="bg-netflix-red px-6 py-2 rounded-lg font-semibold hover:bg-red-700 transition-colors">
                    Novo Cliente
                </button>
            </div>
            <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
                <table className="w-full text-left border-collapse">
                    <thead className="bg-slate-950 border-b border-slate-800">
                        <tr>
                            <th className="px-6 py-4 text-sm font-medium text-slate-400">Empresa</th>
                            <th className="px-6 py-4 text-sm font-medium text-slate-400">E-mail</th>
                            <th className="px-6 py-4 text-sm font-medium text-slate-400">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colSpan={3} className="px-6 py-8 text-center text-slate-500">Nenhum cliente cadastrado.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AdminTenants;
