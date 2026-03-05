import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../api/client';
import { Bot, Mail, Lock, Loader2, AlertCircle } from 'lucide-react';
import { AuthResponse } from '../../types/auth';

/**
 * Página de Login - Fase 5
 * Design moderno focado em estética premium, utilizando Tailwind CSS.
 * Integração real com o endpoint POST /api/v1/auth/login do FastAPI.
 */
const Login: React.FC = () => {
    const navigate = useNavigate();
    const { signIn } = useAuth();

    // Estados do formulário
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    /**
     * Gerencia a submissão do formulário de login.
     */
    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            // Chamada para a API backend
            const response = await api.post<AuthResponse>('/api/v1/auth/login', {
                email,
                password,
            });

            // Salva os dados no contexto global
            signIn(response.data);

            // Redireciona baseado no tipo de usuário
            if (response.data.is_superadmin) {
                navigate('/admin/super');
            } else {
                navigate('/admin/dashboard');
            }
        } catch (err: any) {
            // Tratamento de erros vindo do backend (401, 403, 500)
            const message = err.response?.data?.detail || 'Falha na autenticação. Verifique suas credenciais.';
            setError(message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="flex h-screen w-full items-center justify-center bg-slate-950 px-4">
            {/* Decoração de fundo com gradientes */}
            <div className="absolute top-0 right-0 h-[500px] w-[500px] bg-netflix-red/10 blur-[120px] rounded-full -z-10" />
            <div className="absolute bottom-0 left-0 h-[500px] w-[500px] bg-blue-600/10 blur-[120px] rounded-full -z-10" />

            <div className="w-full max-w-md space-y-8 bg-slate-900/50 p-10 rounded-2xl border border-slate-800 shadow-2xl backdrop-blur-xl">
                {/* Cabeçalho */}
                <div className="text-center">
                    <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-netflix-red shadow-lg shadow-netflix-red/20 mb-4 animate-pulse">
                        <Bot size={36} className="text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">VimaBOT</h1>
                    <p className="mt-2 text-slate-400 text-sm">Sua plataforma SaaS de vendas via Telegram</p>
                </div>

                {/* Formulário */}
                <form onSubmit={handleSubmit} className="mt-8 space-y-6">
                    {error && (
                        <div className="flex items-center gap-3 rounded-lg bg-red-500/10 border border-red-500/50 p-4 text-sm text-red-500 animate-in fade-in zoom-in duration-300">
                            <AlertCircle size={18} />
                            <span>{error}</span>
                        </div>
                    )}

                    <div className="space-y-4">
                        {/* E-mail */}
                        <div className="space-y-1">
                            <label className="text-sm font-medium text-slate-300 ml-1">E-mail</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500 group-focus-within:text-netflix-red transition-colors">
                                    <Mail size={18} />
                                </div>
                                <input
                                    type="email"
                                    required
                                    placeholder="Seu e-mail cadastrado"
                                    className="block w-full pl-10 pr-3 py-3 bg-slate-950/50 border border-slate-800 rounded-xl text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-netflix-red/50 focus:border-netflix-red transition-all"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                        </div>

                        {/* Senha */}
                        <div className="space-y-1">
                            <label className="text-sm font-medium text-slate-300 ml-1">Senha</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500 group-focus-within:text-netflix-red transition-colors">
                                    <Lock size={18} />
                                </div>
                                <input
                                    type="password"
                                    required
                                    placeholder="••••••••"
                                    className="block w-full pl-10 pr-3 py-3 bg-slate-950/50 border border-slate-800 rounded-xl text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-netflix-red/50 focus:border-netflix-red transition-all"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center justify-between text-xs sm:text-sm">
                        <div className="flex items-center gap-2">
                            <input type="checkbox" className="rounded-sm border-slate-700 bg-slate-900 text-netflix-red focus:ring-netflix-red" />
                            <span className="text-slate-400">Lembrar de mim</span>
                        </div>
                        <a href="#" className="font-medium text-netflix-red hover:text-red-400 transition-colors">Esqueceu a senha?</a>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="group relative flex w-full justify-center rounded-xl bg-netflix-red py-4 text-sm font-semibold text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-netflix-red focus:ring-offset-2 focus:ring-offset-slate-950 transition-all disabled:opacity-70 disabled:cursor-not-allowed shadow-xl shadow-netflix-red/10"
                    >
                        {loading ? (
                            <Loader2 className="h-5 w-5 animate-spin" />
                        ) : (
                            "ENTRAR NO SISTEMA"
                        )}
                    </button>
                </form>

                <div className="text-center text-xs text-slate-500">
                    &copy; 2026 VimaBOT SaaS. Todos os direitos reservados.
                </div>
            </div>
        </div>
    );
};

export default Login;
