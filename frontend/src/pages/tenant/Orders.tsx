import React from 'react';
import { Kanban } from 'lucide-react';

const TenantOrders: React.FC = () => {
    return (
        <div className="p-8 text-white h-full flex flex-col">
            <div className="flex items-center gap-3 mb-8">
                <Kanban className="text-netflix-red" />
                <h1 className="text-2xl font-bold">Kanban de Vendas</h1>
            </div>

            <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-6 overflow-x-auto pb-4">
                {/* Colunas Mock */}
                {['Aguardando Pagamento', 'Validação', 'Processando', 'Finalizados'].map((col) => (
                    <div key={col} className="bg-slate-900/50 rounded-xl border border-slate-800 p-4 min-w-[280px]">
                        <h2 className="text-sm font-semibold text-slate-400 mb-4 uppercase tracking-wider">{col}</h2>
                        <div className="space-y-3">
                            <p className="text-center text-xs text-slate-600 py-8">Vazio</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TenantOrders;
