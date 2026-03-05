import React, { useEffect, useState } from 'react';
import {
    Bot,
    Key,
    ExternalLink,
    Play,
    Square,
    CheckCircle2,
    AlertCircle,
    Database,
    CreditCard,
    Loader2
} from 'lucide-react';
import api from '../../api/client';

interface BotConfig {
    telegram_token: string;
    minio_endpoint: string;
    minio_access_key: string;
    minio_secret_key: string;
    vimapix_token: string;
    bot_name?: string;
    is_active: boolean;
}

/**
 * Página de Configuração do Bot - Dashboard do Tenant.
 * Permite ao inquilino configurar suas chaves do Telegram, S3 e Pix.
 * Integração com /api/v1/bot-config e controles de Start/Stop.
 */
const TenantBotConfig: React.FC = () => {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [config, setConfig] = useState<BotConfig>({
        telegram_token: '',
        minio_endpoint: '',
        minio_access_key: '',
        minio_secret_key: '',
        vimapix_token: '',
        is_active: false
    });
    const [status, setStatus] = useState<'online' | 'offline' | 'starting'>('offline');

    useEffect(() => {
        async function loadConfig() {
            try {
                const response = await api.get<BotConfig>('/api/v1/bot-config');
                setConfig(response.data);
                setStatus(response.data.is_active ? 'online' : 'offline');
            } catch (error) {
                console.error('Erro ao carregar configuração do bot:', error);
            } finally {
                setLoading(false);
            }
        }
        loadConfig();
    }, []);

    async function handleSave(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        try {
            await api.put('/api/v1/bot-config', config);
            alert('Configurações salvas com sucesso!');
        } catch (error) {
            alert('Erro ao salvar as configurações.');
        } finally {
            setSaving(false);
        }
    }

    async function toggleBot(action: 'start' | 'stop') {
        setStatus('starting');
        try {
            await api.post(`/api/v1/bot/${action}`);
            setStatus(action === 'start' ? 'online' : 'offline');
        } catch (error) {
            alert(`Falha ao ${action === 'start' ? 'iniciar' : 'parar'} o bot.`);
            setStatus(status); // volta ao estado anterior
        }
    }

    if (loading) return (
        <div className="flex h-64 items-center justify-center text-slate-500 italic">
            Sincronizando com o motor do bot...
        </div>
    );

    return (
        <div className="max-w-4xl space-y-8 pb-12">
            {/* Header Bot Status */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 h-32 w-32 bg-netflix-red/5 blur-3xl -z-10" />

                <div className="flex items-center gap-4">
                    <div className={`h-16 w-16 rounded-2xl flex items-center justify-center ${status === 'online' ? 'bg-green-500/20 text-green-500' : 'bg-slate-800 text-slate-500'}`}>
                        <Bot size={36} />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-white uppercase tracking-tight">Status do Seu Robô</h1>
                        <div className="flex items-center gap-2 mt-1">
                            <div className={`h-2.5 w-2.5 rounded-full ${status === 'online' ? 'bg-green-500 animate-pulse' : 'bg-slate-600'}`} />
                            <span className={`text-sm font-bold uppercase tracking-widest ${status === 'online' ? 'text-green-500' : 'text-slate-500'}`}>
                                {status === 'online' ? 'OPERANDO AGORA' : status === 'offline' ? 'BOT DESLIGADO' : 'INICIALIZANDO...'}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {status === 'online' ? (
                        <button
                            onClick={() => toggleBot('stop')}
                            className="flex items-center gap-2 bg-slate-800 hover:bg-red-600 text-white px-6 py-2.5 rounded-xl font-bold text-sm transition-all"
                        >
                            <Square size={16} fill="currentColor" />
                            DESLIGAR BOT
                        </button>
                    ) : (
                        <button
                            onClick={() => toggleBot('start')}
                            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-6 py-2.5 rounded-xl font-bold text-sm transition-all shadow-lg shadow-green-500/20"
                        >
                            <Play size={16} fill="currentColor" />
                            LIGAR ROBÔ
                        </button>
                    )}
                </div>
            </div>

            <form onSubmit={handleSave} className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Telegram Config */}
                <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 space-y-6">
                    <div className="flex items-center gap-3 border-b border-white/5 pb-4">
                        <Bot className="text-blue-400" size={20} />
                        <h2 className="font-bold text-white tracking-widest uppercase text-xs">Motor Telegram</h2>
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-slate-500 uppercase ml-1">Token da API (@BotFather)</label>
                        <div className="relative">
                            <Key className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-600" size={16} />
                            <input
                                type="password"
                                value={config.telegram_token}
                                onChange={(e) => setConfig({ ...config, telegram_token: e.target.value })}
                                placeholder="000000:AAAAAA..."
                                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                            />
                        </div>
                        <p className="text-[10px] text-slate-600 ml-1 italic flex items-center gap-1">
                            <AlertCircle size={10} />
                            Nunca compartilhe este token com terceiros.
                        </p>
                    </div>
                </div>

                {/* Storage Minio */}
                <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 space-y-6">
                    <div className="flex items-center gap-3 border-b border-white/5 pb-4">
                        <Database className="text-amber-400" size={20} />
                        <h2 className="font-bold text-white tracking-widest uppercase text-xs">Storage Cloud (Minio S3)</h2>
                    </div>
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-slate-500 uppercase ml-1">Minio Endpoint</label>
                            <input
                                type="text"
                                value={config.minio_endpoint}
                                onChange={(e) => setConfig({ ...config, minio_endpoint: e.target.value })}
                                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500/50"
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-slate-500 uppercase ml-1">Access Key</label>
                                <input
                                    type="text"
                                    value={config.minio_access_key}
                                    onChange={(e) => setConfig({ ...config, minio_access_key: e.target.value })}
                                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500/50"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-slate-500 uppercase ml-1">Secret Key</label>
                                <input
                                    type="password"
                                    value={config.minio_secret_key}
                                    onChange={(e) => setConfig({ ...config, minio_secret_key: e.target.value })}
                                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-amber-500/50"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Pagamentos Pix */}
                <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 space-y-6 md:col-span-2">
                    <div className="flex items-center gap-3 border-b border-white/5 pb-4">
                        <CreditCard className="text-green-400" size={20} />
                        <h2 className="font-bold text-white tracking-widest uppercase text-xs">Gateway de Pagamentos (Pix)</h2>
                    </div>
                    <div className="flex flex-col md:flex-row gap-6 items-start">
                        <div className="flex-1 space-y-2 w-full">
                            <label className="text-xs font-bold text-slate-500 uppercase ml-1">Tokan de API Vimapix / OpenPix</label>
                            <input
                                type="password"
                                value={config.vimapix_token}
                                onChange={(e) => setConfig({ ...config, vimapix_token: e.target.value })}
                                placeholder="Ex: app_..."
                                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-green-500/50"
                            />
                        </div>
                        <div className="bg-green-500/5 border border-green-500/20 p-4 rounded-xl text-[11px] text-slate-400 max-w-xs">
                            <h4 className="font-bold text-green-500 uppercase mb-1">Dica de Segurança</h4>
                            <p>Recomendamos o uso de tokens restritos do Vimapix para garantir que apenas recebimentos PIX possam ser consultados.</p>
                        </div>
                    </div>
                </div>

                <div className="md:col-span-2 flex justify-end">
                    <button
                        type="submit"
                        disabled={saving}
                        className="group flex items-center gap-2 bg-white text-slate-950 px-10 py-3 rounded-xl font-black text-sm transition-all hover:bg-slate-200 active:scale-95 disabled:opacity-50"
                    >
                        {saving ? <Loader2 className="animate-spin" size={18} /> : <CheckCircle2 size={18} />}
                        SALVAR ALTERAÇÕES
                    </button>
                </div>
            </form>
        </div>
    );
};

export default TenantBotConfig;
