import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import {
    Play,
    Info,
    Search,
    ChevronRight,
    X,
    CreditCard,
    CheckCircle2,
    Clock
} from 'lucide-react';
import api from '../../api/client';

interface Product {
    id: string;
    name: string;
    description: string;
    price: number;
    image_url: string;
}

/**
 * Catálogo WebApp (Telegram Mini App) - Fase 6.
 * Design premium inspirado na Netflix: Dark mode, trilhos horizontais e micro-animações.
 * Integração silenciosa via window.Telegram.WebApp.sendData.
 */
const WebAppCatalog: React.FC = () => {
    const { tenant_id } = useParams<{ tenant_id: string }>();
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

    useEffect(() => {
        // Scroll para o topo e expansão do TMA
        window.scrollTo(0, 0);
        const tg = (window as any).Telegram?.WebApp;
        if (tg) {
            tg.expand();
            tg.ready();
            tg.headerColor = '#141414';
            tg.backgroundColor = '#141414';
        }

        async function loadPublicCatalog() {
            try {
                // Rota pública do catálogo
                const response = await api.get<Product[]>(`/api/v1/webapp/${tenant_id}/catalog`);
                setProducts(response.data);
            } catch (error) {
                console.error('Erro ao carregar catálogo público:', error);
            } finally {
                setLoading(false);
            }
        }

        if (tenant_id) loadPublicCatalog();
    }, [tenant_id]);

    /**
     * Dispara a intenção de compra para o Bot do Telegram.
     */
    function handlePurchase(productId: string) {
        const tg = (window as any).Telegram?.WebApp;
        if (tg) {
            // Envia os dados e fecha o WebApp, o bot recebe via SERVICE_WEBAPP_DATA
            tg.sendData(JSON.stringify({
                action: "checkout",
                product_id: productId
            }));
            tg.close();
        } else {
            alert('Esta ação só funciona dentro do Telegram.');
        }
    }

    if (loading) return (
        <div className="flex h-screen w-full items-center justify-center bg-netflix-black">
            <div className="h-10 w-10 border-4 border-netflix-red border-t-transparent rounded-full animate-spin" />
        </div>
    );

    return (
        <div className="min-h-screen bg-netflix-black text-slate-100 font-sans selection:bg-netflix-red pb-20">

            {/* Header Estilo Netflix */}
            <header className="sticky top-0 z-40 flex items-center justify-between px-4 py-4 bg-gradient-to-b from-black/80 to-transparent backdrop-blur-sm">
                <div className="flex items-center gap-6">
                    <div className="text-netflix-red font-black text-2xl tracking-tighter italic">VimaBOT</div>
                    <nav className="hidden sm:flex gap-4 text-xs font-bold uppercase tracking-widest text-slate-400">
                        <span className="text-white">Início</span>
                        <span>Populares</span>
                        <span>Novidades</span>
                    </nav>
                </div>
                <div className="flex items-center gap-4">
                    <Search size={20} className="text-slate-300" />
                    <div className="h-7 w-7 bg-netflix-red rounded shadow-lg shadow-netflix-red/20" />
                </div>
            </header>

            {/* Hero / Destaque Principal */}
            {products.length > 0 && (
                <section className="relative h-[65vh] w-full overflow-hidden">
                    <img
                        src={products[0].image_url}
                        className="w-full h-full object-cover brightness-75 scale-105"
                        alt="Hero"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-netflix-black via-netflix-black/20 to-transparent" />

                    <div className="absolute bottom-12 left-0 w-full px-6 space-y-4">
                        <div className="flex items-center gap-2 mb-2">
                            <span className="bg-netflix-red text-[10px] font-black px-1.5 py-0.5 rounded italic">TOP 10</span>
                            <span className="text-xs font-bold text-slate-300">Mais vendidos esta semana</span>
                        </div>
                        <h1 className="text-4xl font-black text-white tracking-tighter drop-shadow-lg">{products[0].name}</h1>
                        <p className="text-sm text-slate-300 max-w-xs line-clamp-3 leading-relaxed drop-shadow-md">
                            {products[0].description}
                        </p>
                        <div className="flex gap-3 pt-2">
                            <button
                                onClick={() => setSelectedProduct(products[0])}
                                className="flex-1 bg-white text-black py-2.5 rounded font-black text-sm flex items-center justify-center gap-2 active:scale-95 transition-transform"
                            >
                                <Play size={18} fill="currentColor" /> Assistir / Ver
                            </button>
                            <button
                                onClick={() => setSelectedProduct(products[0])}
                                className="bg-slate-600/50 text-white p-2.5 rounded backdrop-blur-xl"
                            >
                                <Info size={18} />
                            </button>
                        </div>
                    </div>
                </section>
            )}

            {/* Trilhos Horizontais de Conteúdo */}
            <div className="px-4 mt-8 space-y-12">
                <section className="space-y-4">
                    <h2 className="text-lg font-bold flex items-center gap-1.5 text-white">
                        Populares no VimaBOT <ChevronRight size={16} className="text-netflix-red" />
                    </h2>
                    <div className="flex gap-3 overflow-x-auto hide-scrollbar pb-4 -mx-1 px-1">
                        {products.map((prod) => (
                            <div
                                key={prod.id}
                                onClick={() => setSelectedProduct(prod)}
                                className="min-w-[125px] sm:min-w-[160px] aspect-[2/3] bg-slate-900 rounded-md overflow-hidden transition-transform duration-300 hover:scale-105 active:scale-95 cursor-pointer shadow-2xl relative"
                            >
                                <img src={prod.image_url} className="w-full h-full object-cover" alt={prod.name} />
                                <div className="absolute top-2 right-2 bg-black/60 px-1 py-0.5 rounded text-[8px] font-black tracking-widest uppercase border border-white/10 backdrop-blur-sm">4K Ultra</div>
                            </div>
                        ))}
                    </div>
                </section>

                <section className="space-y-4">
                    <h2 className="text-lg font-bold flex items-center gap-1.5 text-white">
                        Novas Adições <ChevronRight size={16} className="text-netflix-red" />
                    </h2>
                    <div className="flex gap-3 overflow-x-auto hide-scrollbar pb-4 -mx-1 px-1">
                        {[...products].reverse().map((prod) => (
                            <div
                                key={`rev-${prod.id}`}
                                onClick={() => setSelectedProduct(prod)}
                                className="min-w-[125px] sm:min-w-[160px] aspect-[2/3] bg-slate-900 rounded-md overflow-hidden transition-transform duration-300 hover:scale-105 active:scale-95 cursor-pointer shadow-2xl"
                            >
                                <img src={prod.image_url} className="w-full h-full object-cover" alt={prod.name} />
                            </div>
                        ))}
                    </div>
                </section>
            </div>

            {/* Modal / BottomSheet de Detalhes (Estética Netflix) */}
            {selectedProduct && (
                <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/90 backdrop-blur-sm animate-in fade-in duration-300 px-0 sm:px-4">
                    <div className="w-full max-w-2xl bg-netflix-black border-t sm:border border-white/10 sm:rounded-2xl overflow-hidden shadow-2xl animate-in slide-in-from-bottom duration-300">

                        {/* Cabeçalho do Modal com Imagem */}
                        <div className="relative h-[250px] w-full">
                            <img src={selectedProduct.image_url} className="w-full h-full object-cover" alt="Detail" />
                            <div className="absolute inset-0 bg-gradient-to-t from-netflix-black via-transparent to-transparent" />
                            <button
                                onClick={() => setSelectedProduct(null)}
                                className="absolute top-4 right-4 p-2 bg-black/60 rounded-full text-white"
                            >
                                <X size={20} />
                            </button>
                            <div className="absolute bottom-4 left-6">
                                <h2 className="text-2xl font-black">{selectedProduct.name}</h2>
                            </div>
                        </div>

                        <div className="p-8 space-y-6">
                            <div className="flex flex-wrap items-center gap-3">
                                <span className="text-green-500 font-bold text-sm">98% de Relevância</span>
                                <span className="text-slate-400 text-sm">2026</span>
                                <span className="px-1 border border-slate-600 text-[10px] text-slate-400 rounded">16+</span>
                                <span className="bg-slate-800 px-1 py-0.5 rounded text-[8px] font-bold text-slate-400 uppercase tracking-widest border border-white/5">Digital Content</span>
                            </div>

                            <p className="text-slate-300 text-sm leading-relaxed">
                                {selectedProduct.description}
                            </p>

                            <div className="space-y-4 pt-4 border-t border-white/5">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <Clock size={16} className="text-slate-500" />
                                        <span className="text-xs font-bold text-slate-500 uppercase">Entrega Imediata via Bot</span>
                                    </div>
                                    <span className="text-2xl font-black text-white">R$ {selectedProduct.price.toFixed(2)}</span>
                                </div>

                                <button
                                    onClick={() => handlePurchase(selectedProduct.id)}
                                    className="w-full bg-green-500 hover:bg-green-600 text-black py-4 rounded-lg font-black text-sm transition-all flex items-center justify-center gap-2 active:scale-95 shadow-lg shadow-green-500/20"
                                >
                                    <CreditCard size={18} fill="currentColor" /> 💳 COMPRAR AGORA (PIX)
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Footer Nav simulada para Mobile */}
            <footer className="fixed bottom-0 left-0 w-full h-16 bg-[#181818] border-t border-white/5 flex items-center justify-around z-30">
                <div className="flex flex-col items-center gap-1 group active:scale-90 transition-transform">
                    <Info className="text-slate-400 group-hover:text-white" size={20} />
                    <span className="text-[8px] font-bold uppercase text-slate-500 group-hover:text-white">Home</span>
                </div>
                <div className="flex flex-col items-center gap-1 group active:scale-90 transition-transform">
                    <Search size={20} className="text-slate-400" />
                    <span className="text-[8px] font-bold uppercase text-slate-500">Busca</span>
                </div>
                <div className="flex flex-col items-center gap-1 group active:scale-90 transition-transform">
                    <div className="h-5 w-5 bg-netflix-red rounded-sm" />
                    <span className="text-[8px] font-bold uppercase text-white">Minha Conta</span>
                </div>
            </footer>

        </div>
    );
};

export default WebAppCatalog;
