import React, { useEffect, useState } from 'react';
import {
    Kanban as KanbanIcon,
    ExternalLink,
    Eye,
    CheckCircle2,
    Truck,
    Clock,
    CircleDollarSign,
    AlertCircle,
    MoreHorizontal
} from 'lucide-react';
import api from '../../api/client';

interface Order {
    id: string;
    customer_name: string;
    product_name: string;
    amount: number;
    status: 'pending' | 'validation' | 'paid' | 'delivered';
    pix_proof_url?: string;
    created_at: string;
}

const COLUMNS = [
    { id: 'pending', title: 'Aguardando Pagamento', icon: CircleDollarSign, color: 'text-slate-400' },
    { id: 'validation', title: 'Validação', icon: Eye, color: 'text-amber-400' },
    { id: 'paid', title: 'Processando', icon: CheckCircle2, color: 'text-blue-400' },
    { id: 'delivered', title: 'Finalizados', icon: Truck, color: 'text-green-400' },
];

/**
 * Página Kanban de Pedidos - Dashboard do Tenant.
 * Gerencia o fluxo de vendas desde o pedido inicial até a entrega.
 * Integração com /api/v1/orders.
 */
const TenantOrders: React.FC = () => {
    const [orders, setOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadOrders() {
            try {
                const response = await api.get<Order[]>('/api/v1/orders');
                setOrders(response.data);
            } catch (error) {
                console.error('Erro ao carregar pedidos:', error);
            } finally {
                setLoading(false);
            }
        }
        loadOrders();
    }, []);

    async function updateOrderStatus(orderId: string, newStatus: Order['status']) {
        try {
            await api.patch(`/api/v1/orders/${orderId}/status`, { status: newStatus });
            setOrders(prev => prev.map(o => o.id === orderId ? { ...o, status: newStatus } : o));
        } catch (error) {
            alert('Erro ao atualizar o status do pedido.');
        }
    }

    return (
        <div className="h-full flex flex-col space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-extrabold text-white flex items-center gap-3">
                        <KanbanIcon className="text-netflix-red" />
                        Fluxo de Vendas
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">Acompanhe seus pedidos em tempo real.</p>
                </div>

                <div className="flex items-center gap-4 bg-slate-900/50 p-2 rounded-xl border border-slate-800">
                    <div className="px-4 py-1 text-center">
                        <p className="text-[10px] font-bold text-slate-500 uppercase">Hoje</p>
                        <p className="text-lg font-black text-white">R$ 0,00</p>
                    </div>
                </div>
            </div>

            <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-6 overflow-x-auto pb-6 scrollbar-thin scrollbar-thumb-slate-800">
                {COLUMNS.map((col) => {
                    const colOrders = orders.filter(o => o.status === col.id);

                    return (
                        <div key={col.id} className="flex flex-col min-w-[300px] bg-slate-900/40 rounded-2xl border border-slate-800/50">
                            {/* Header Coluna */}
                            <div className="p-4 border-b border-white/5 flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <col.icon size={16} className={col.color} />
                                    <h2 className="text-xs font-black text-slate-300 uppercase tracking-tighter">{col.title}</h2>
                                </div>
                                <span className="bg-slate-800 text-slate-400 text-[10px] font-bold px-2 py-0.5 rounded-full border border-slate-700">
                                    {colOrders.length}
                                </span>
                            </div>

                            {/* Lista de Cards */}
                            <div className="p-3 space-y-3 overflow-y-auto max-h-[calc(100vh-280px)] scrollbar-hide">
                                {loading ? (
                                    <div className="py-8 text-center animate-pulse text-slate-600 text-xs uppercase font-bold tracking-widest">Sincronizando...</div>
                                ) : colOrders.length === 0 ? (
                                    <div className="py-12 flex flex-col items-center justify-center opacity-20 grayscale">
                                        <KanbanIcon size={32} className="text-slate-500 mb-2" />
                                        <p className="text-[10px] font-bold uppercase">Nenhum Registro</p>
                                    </div>
                                ) : (
                                    colOrders.map((order) => (
                                        <div key={order.id} className="bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 rounded-xl p-4 transition-all group cursor-default shadow-lg">
                                            <div className="flex justify-between items-start mb-3">
                                                <span className="text-[9px] font-mono text-slate-500 bg-slate-950 px-1.5 py-0.5 rounded uppercase font-bold">#{order.id.split('-')[0]}</span>
                                                <button className="text-slate-600 hover:text-white transition-colors opacity-0 group-hover:opacity-100">
                                                    <MoreHorizontal size={14} />
                                                </button>
                                            </div>

                                            <h3 className="text-sm font-bold text-slate-100 truncate">{order.customer_name}</h3>
                                            <p className="text-[11px] text-slate-400 font-medium mt-0.5">{order.product_name}</p>

                                            <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between">
                                                <span className="text-blue-400 text-sm font-black tracking-tight">R$ {order.amount.toFixed(2)}</span>

                                                {/* Ações de Status */}
                                                <div className="flex items-center gap-1">
                                                    {order.status === 'validation' && order.pix_proof_url && (
                                                        <a href={order.pix_proof_url} target="_blank" rel="noreferrer" className="p-1.5 bg-slate-700 hover:bg-amber-500/20 text-amber-400 rounded-lg transition-all" title="Ver Comprovante">
                                                            <Eye size={14} />
                                                        </a>
                                                    )}

                                                    {/* Botões de Avanço (Seta para o próximo status) */}
                                                    {order.status !== 'delivered' && (
                                                        <button
                                                            onClick={() => {
                                                                const next: Order['status'][] = ['pending', 'validation', 'paid', 'delivered'];
                                                                const currentIndex = next.indexOf(order.status);
                                                                updateOrderStatus(order.id, next[currentIndex + 1]);
                                                            }}
                                                            className="p-1.5 bg-netflix-red/10 hover:bg-netflix-red text-netflix-red hover:text-white rounded-lg transition-all shadow-md active:scale-90"
                                                            title="Avançar Pedido"
                                                        >
                                                            <CheckCircle2 size={14} />
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default TenantOrders;
