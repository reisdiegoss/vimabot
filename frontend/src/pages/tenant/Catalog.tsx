import React, { useEffect, useState } from 'react';
import {
    Package,
    Plus,
    Trash2,
    Edit3,
    ImageIcon,
    Search,
    CheckCircle2,
    AlertTriangle,
    Loader2,
    X
} from 'lucide-react';
import api from '../../api/client';

interface Product {
    id: string;
    name: string;
    description: string;
    price: number;
    image_url: string;
    is_active: boolean;
}

/**
 * Página de Gestão do Catálogo de Produtos - Dashboard do Tenant.
 * Permite CRUD de produtos digitais que serão exibidos no Bot e TMA.
 * Integração com /api/v1/products.
 */
const TenantCatalog: React.FC = () => {
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [saving, setSaving] = useState(false);

    // Estados para o novo produto
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        price: '',
        image_url: 'https://via.placeholder.com/300x450/141414/ffffff?text=VimaBOT' // Default Netflix-like
    });

    useEffect(() => {
        async function loadProducts() {
            try {
                const response = await api.get<Product[]>('/api/v1/products');
                setProducts(response.data);
            } catch (error) {
                console.error('Erro ao carregar catálogo:', error);
            } finally {
                setLoading(false);
            }
        }
        loadProducts();
    }, []);

    async function handleAddProduct(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        try {
            const response = await api.post<Product>('/api/v1/products', {
                ...formData,
                price: parseFloat(formData.price)
            });
            setProducts([response.data, ...products]);
            setIsModalOpen(false);
            setFormData({ name: '', description: '', price: '', image_url: 'https://via.placeholder.com/300x450/141414/ffffff?text=VimaBOT' });
        } catch (error) {
            alert('Erro ao cadastrar produto.');
        } finally {
            setSaving(false);
        }
    }

    async function handleDelete(id: string) {
        if (!confirm('Deseja realmente excluir este item do catálogo?')) return;
        try {
            await api.delete(`/api/v1/products/${id}`);
            setProducts(products.filter(p => p.id !== id));
        } catch (error) {
            alert('Erro ao excluir produto.');
        }
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-black text-white flex items-center gap-3 tracking-tight">
                        <Package className="text-netflix-red" />
                        Catálogo de Conteúdo
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">Gerencie os produtos que estarão disponíveis no seu catálogo.</p>
                </div>

                <button
                    onClick={() => setIsModalOpen(true)}
                    className="flex items-center justify-center gap-2 bg-netflix-red hover:bg-red-700 text-white px-6 py-3 rounded-xl font-black text-xs transition-all shadow-lg shadow-netflix-red/20 active:scale-95 uppercase tracking-widest"
                >
                    <Plus size={18} />
                    Adicionar Produto
                </button>
            </div>

            {/* Grid de Produtos */}
            {loading ? (
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
                    {[1, 2, 3, 4, 5].map(i => (
                        <div key={i} className="aspect-[2/3] bg-slate-900 animate-pulse rounded-xl border border-slate-800" />
                    ))}
                </div>
            ) : products.length === 0 ? (
                <div className="py-24 text-center border-2 border-dashed border-slate-800 rounded-3xl group hover:border-slate-700 transition-colors">
                    <div className="mx-auto w-16 h-16 bg-slate-900 rounded-2xl flex items-center justify-center text-slate-700 mb-4 group-hover:scale-110 transition-transform">
                        <Package size={32} />
                    </div>
                    <p className="text-slate-500 font-medium">Seu catálogo está vazio.</p>
                    <button onClick={() => setIsModalOpen(true)} className="text-netflix-red text-sm font-bold mt-2 hover:underline">Comece postando seu primeiro produto</button>
                </div>
            ) : (
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
                    {products.map((product) => (
                        <div key={product.id} className="group relative flex flex-col bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden transition-all hover:border-slate-600 hover:-translate-y-1 shadow-2xl">
                            <div className="aspect-[2/3] w-full overflow-hidden relative">
                                <img
                                    src={product.image_url}
                                    alt={product.name}
                                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                                />

                                {/* Overlay de Ações (Aparece no Hover) */}
                                <div className="absolute inset-0 bg-slate-950/80 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-4 gap-2 backdrop-blur-sm">
                                    <div className="space-y-1 mb-2">
                                        <p className="text-blue-400 font-black text-lg leading-none">R$ {product.price.toFixed(2)}</p>
                                        <p className="text-[10px] text-slate-400 line-clamp-2 italic">{product.description}</p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button className="flex-1 bg-slate-800 hover:bg-slate-700 text-white p-2 rounded-lg transition-colors flex justify-center">
                                            <Edit3 size={16} />
                                        </button>
                                        <button
                                            onClick={() => handleDelete(product.id)}
                                            className="flex-1 bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white p-2 rounded-lg transition-colors flex justify-center"
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div className="p-3">
                                <h3 className="text-xs font-bold text-slate-200 truncate pr-4">{product.name}</h3>
                                <div className="flex items-center gap-1.5 mt-1">
                                    <div className={`h-1.5 w-1.5 rounded-full ${product.is_active ? 'bg-green-500' : 'bg-slate-600'}`} />
                                    <span className="text-[9px] font-black uppercase text-slate-500 tracking-tighter">
                                        {product.is_active ? 'Público' : 'Rascunho'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Modal de Criação (Ultra Moderno) */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/90 backdrop-blur-md animate-in fade-in duration-300">
                    <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
                        <div className="p-6 border-b border-white/5 flex items-center justify-between bg-slate-950/50">
                            <h2 className="text-xl font-black text-white uppercase tracking-tighter">Novo Produto Digital</h2>
                            <button onClick={() => setIsModalOpen(false)} className="text-slate-500 hover:text-white">
                                <X size={24} />
                            </button>
                        </div>

                        <form onSubmit={handleAddProduct} className="p-8 space-y-6">
                            <div className="grid grid-cols-1 gap-6">
                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Título do Conteúdo</label>
                                    <input
                                        required
                                        type="text"
                                        placeholder="Ex: Curso de Python Masterclass"
                                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:ring-2 focus:ring-netflix-red/50"
                                        value={formData.name}
                                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-6">
                                    <div className="space-y-1.5">
                                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Preço Sugerido (R$)</label>
                                        <input
                                            required
                                            type="number"
                                            step="0.01"
                                            placeholder="97.00"
                                            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:ring-2 focus:ring-blue-500/50 appearance-none"
                                            value={formData.price}
                                            onChange={e => setFormData({ ...formData, price: e.target.value })}
                                        />
                                    </div>
                                    <div className="space-y-1.5">
                                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Ativo no Chat?</label>
                                        <div className="h-[46px] flex items-center px-4 bg-slate-950 border border-slate-800 rounded-xl">
                                            <span className="text-xs font-bold text-green-500 uppercase">Sim</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Sinopse / Descrição</label>
                                    <textarea
                                        required
                                        rows={3}
                                        placeholder="Breve descrição do produto..."
                                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:ring-2 focus:ring-netflix-red/50"
                                        value={formData.description}
                                        onChange={e => setFormData({ ...formData, description: e.target.value })}
                                    />
                                </div>

                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">URL da Imagem de Capa</label>
                                    <div className="relative group">
                                        <ImageIcon className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600 group-focus-within:text-amber-400" size={18} />
                                        <input
                                            type="text"
                                            placeholder="https://cloud.minio.com/..."
                                            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-3 text-sm text-white focus:ring-2 focus:ring-amber-500/50"
                                            value={formData.image_url}
                                            onChange={e => setFormData({ ...formData, image_url: e.target.value })}
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="pt-4">
                                <button
                                    type="submit"
                                    disabled={saving}
                                    className="w-full bg-netflix-red hover:bg-red-700 text-white py-4 rounded-xl font-black text-sm transition-all shadow-xl shadow-netflix-red/10 flex items-center justify-center gap-2"
                                >
                                    {saving ? <Loader2 className="animate-spin" /> : <CheckCircle2 size={18} />}
                                    FINALIZAR CADASTRO
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TenantCatalog;
