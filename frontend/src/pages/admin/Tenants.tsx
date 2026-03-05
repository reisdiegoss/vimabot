import React, { useEffect, useState } from 'react';
import {
    Users,
    Plus,
    Search,
    MoreVertical,
    ShieldCheck,
    UserX,
    Clock,
    ExternalLink,
    ChevronRight
} from 'lucide-react';
import api from '../../api/client';
import { Tenant } from '../../types/auth';

/**
 * Página de Gestão de Tenants (Clientes) - Exclusiva Super-Admin.
 * Lista todos os inquilinos registrados na plataforma SaaS.
 * Integração com GET /api/v1/tenants.
 */
const AdminTenants: React.FC = () => {
    const [tenants, setTenants] = useState<Tenant[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        async function loadTenants() {
            try {
                const response = await api.get<Tenant[]>('/api/v1/tenants');
                setTenants(response.data);
            } catch (error) {
                console.error('Erro ao carregar tenants:', error);
            } finally {
                setLoading(false);
            }
        }

        loadTenants();
    }, []);

    // Filtro de busca local
    const filteredTenants = tenants.filter(t =>
        t.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        t.owner_email.toLowerCase().includes(searchTerm.toLowerCase())
    );

    /**
     * Renderiza a Badge de status com cores semânticas.
     */
    const StatusBadge = ({ status }: { status: Tenant['status'] }) => {
        const styles = {
            active: 'bg-green-500/10 text-green-500 border-green-500/20',
            inactive: 'bg-slate-500/10 text-slate-500 border-slate-500/20',
            suspended: 'bg-red-500/10 text-red-500 border-red-500/20',
        };

        const labels = {
            active: 'Ativo',
            inactive: 'Inativo',
            suspended: 'Suspenso',
        };

        return (
            <span className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase border ${styles[status]}`}>
                {labels[status]}
            </span>
        );
    };

    return (
        <div className="space-y-8">
            {/* Cabeçalho de Ações */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white">Gestão de Clientes</h1>
                    <p className="text-slate-400 text-sm mt-1">Gerencie os inquilinos e assinaturas do SaaS.</p>
                </div>

                <div className="flex items-center gap-3">
                    <div className="relative group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-netflix-red transition-colors" size={18} />
                        <input
                            type="text"
                            placeholder="Buscar cliente..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-netflix-red/50 w-full md:w-64 transition-all"
                        />
                    </div>
                    <button className="flex items-center gap-2 bg-netflix-red hover:bg-red-700 text-white px-5 py-2.5 rounded-xl font-bold text-sm transition-all shadow-lg shadow-netflix-red/20 active:scale-95">
                        <Plus size={18} />
                        <span className="hidden sm:inline">NOVO CLIENTE</span>
                    </button>
                </div>
            </div>

            {/* Tabela de Dados */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-sm shadow-xl">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-slate-950/50 border-b border-white/5">
                                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-widest leading-none">Empresa / ID</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-widest leading-none">Proprietário</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-widest leading-none text-center">Plano</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-widest leading-none text-center">Status</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-widest leading-none text-right">Ações</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {loading ? (
                                <tr>
                                    <td colSpan={5} className="px-6 py-12 text-center text-slate-600 animate-pulse">Carregando dados dos inquilinos...</td>
                                </tr>
                            ) : filteredTenants.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="px-6 py-12 text-center text-slate-600 italic">Nenhum cliente encontrado.</td>
                                </tr>
                            ) : (
                                filteredTenants.map((tenant) => (
                                    <tr key={tenant.id} className="hover:bg-white/[0.02] transition-colors group">
                                        <td className="px-6 py-4">
                                            <div className="flex flex-col">
                                                <span className="text-sm font-bold text-white group-hover:text-netflix-red transition-colors">{tenant.company_name}</span>
                                                <span className="text-[10px] text-slate-500 font-mono mt-1">{tenant.id}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex flex-col">
                                                <span className="text-sm text-slate-300 font-medium">{tenant.owner_email}</span>
                                                <span className="text-[11px] text-slate-500 flex items-center gap-1 mt-0.5">
                                                    <Clock size={10} />
                                                    {new Date(tenant.created_at).toLocaleDateString('pt-BR')}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-center">
                                            <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded text-[10px] font-black uppercase">
                                                {tenant.plan_type}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-center">
                                            <StatusBadge status={tenant.status} />
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex items-center justify-end gap-2">
                                                <button className="p-2 text-slate-500 hover:text-white hover:bg-slate-800 rounded-lg transition-all" title="Gerenciar Bots">
                                                    <ShieldCheck size={18} />
                                                </button>
                                                <button className="p-2 text-slate-500 hover:text-netflix-red hover:bg-red-500/10 rounded-lg transition-all" title="Editar / Logs">
                                                    <ChevronRight size={18} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Grid de Stats Rápidos */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex items-center gap-4 shadow-lg active:scale-95 cursor-pointer hover:border-slate-700 transition-all">
                    <div className="h-12 w-12 rounded-xl bg-netflix-red/10 flex items-center justify-center text-netflix-red">
                        <Users size={24} />
                    </div>
                    <div>
                        <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Total Clientes</p>
                        <h3 className="text-2xl font-black text-white leading-none mt-1">{tenants.length}</h3>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminTenants;
