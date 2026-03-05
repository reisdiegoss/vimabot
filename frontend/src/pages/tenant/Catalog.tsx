import React from 'react';
import { Package } from 'lucide-react';

const TenantCatalog: React.FC = () => {
    return (
        <div className="p-8 text-white">
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                    <Package className="text-netflix-red" />
                    <h1 className="text-2xl font-bold">Catálogo de Produtos</h1>
                </div>
                <button className="bg-netflix-red px-6 py-2 rounded-lg font-semibold hover:bg-red-700 transition-colors">
                    Novo Produto
                </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
                <p className="col-span-full text-center text-slate-500 py-12 border-2 border-dashed border-slate-800 rounded-xl">
                    Nenhum produto cadastrado no catálogo.
                </p>
            </div>
        </div>
    );
};

export default TenantCatalog;
