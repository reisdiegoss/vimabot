import React from 'react';
import { Settings } from 'lucide-react';

const TenantBotConfig: React.FC = () => {
    return (
        <div className="p-8 text-white">
            <div className="flex items-center gap-3 mb-8">
                <Settings className="text-netflix-red" />
                <h1 className="text-2xl font-bold">Configuração do Bot</h1>
            </div>
            <div className="bg-slate-900 p-8 rounded-xl border border-slate-800 max-w-2xl">
                <p className="text-slate-400 mb-6">Insira as credenciais do seu BOT para conectá-lo à plataforma.</p>
                <button className="bg-green-600 px-6 py-2 rounded-lg font-semibold hover:bg-green-700 transition-colors">
                    Salvar Configurações
                </button>
            </div>
        </div>
    );
};

export default TenantBotConfig;
