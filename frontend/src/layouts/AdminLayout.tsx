import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
    Bot,
    LayoutDashboard,
    Users,
    Package,
    Kanban,
    Settings,
    LogOut,
    ChevronRight
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface SidebarItem {
    name: string;
    path: string;
    icon: React.ElementType;
    adminOnly?: boolean;
}

/**
 * Layout Principal do Painel Administrativo.
 * Contém a Sidebar lateral responsiva e a Topbar de perfil.
 * Utilizado por todas as rotas protegidas em /admin.
 */
const AdminLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { user, signOut } = useAuth();
    const navigate = useNavigate();

    // Definição dos itens de navegação
    const navigation: SidebarItem[] = [
        { name: 'Dashboard', path: '/admin/dashboard', icon: LayoutDashboard },
        { name: 'Meus Clientes', path: '/admin/tenants', icon: Users, adminOnly: true },
        { name: 'Meu Bot', path: '/admin/bot', icon: Bot },
        { name: 'Catálogo', path: '/admin/catalog', icon: Package },
        { name: 'Pedidos Kanban', path: '/admin/orders', icon: Kanban },
    ];

    const handleSignOut = () => {
        signOut();
        navigate('/admin/login');
    };

    return (
        <div className="flex h-screen w-full bg-slate-950 font-sans text-slate-200">
            {/* Sidebar Lateral */}
            <aside className="w-64 flex flex-col bg-slate-900/50 border-r border-slate-800 backdrop-blur-sm">
                {/* Logo */}
                <div className="p-6 flex items-center gap-3">
                    <div className="bg-netflix-red p-2 rounded-lg shadow-lg shadow-netflix-red/20">
                        <Bot size={24} className="text-white" />
                    </div>
                    <span className="font-black text-xl tracking-tighter text-white">VimaBOT</span>
                </div>

                {/* Menu de Navegação */}
                <nav className="flex-1 mt-4 px-3 space-y-1">
                    {navigation.map((item) => {
                        // Filtra itens exclusivos do Super-Admin
                        if (item.adminOnly && !user?.is_superadmin) return null;

                        return (
                            <NavLink
                                key={item.path}
                                to={item.path}
                                className={({ isActive }) => `
                  flex items-center justify-between px-4 py-3 rounded-xl transition-all duration-200 group
                  ${isActive
                                        ? 'bg-netflix-red text-white shadow-lg shadow-netflix-red/10'
                                        : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                                    }
                `}
                            >
                                <div className="flex items-center gap-3">
                                    <item.icon size={20} className="group-hover:scale-110 transition-transform" />
                                    <span className="text-sm font-semibold">{item.name}</span>
                                </div>
                                <ChevronRight size={14} className="opacity-0 group-hover:opacity-40" />
                            </NavLink>
                        );
                    })}
                </nav>

                {/* Rodapé da Sidebar - Usuário e Logout */}
                <div className="p-4 border-t border-slate-800 space-y-4">
                    <div className="flex items-center gap-3 px-2">
                        <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-netflix-red to-blue-600 flex items-center justify-center font-bold text-white">
                            {user?.company_name.charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-bold text-white truncate">{user?.company_name}</p>
                            <p className="text-xs text-slate-500 truncate">{user?.email}</p>
                        </div>
                    </div>

                    <button
                        onClick={handleSignOut}
                        className="flex items-center gap-3 w-full px-4 py-3 text-slate-400 hover:text-red-400 hover:bg-red-400/10 rounded-xl transition-all font-semibold text-sm"
                    >
                        <LogOut size={20} />
                        Sair
                    </button>
                </div>
            </aside>

            {/* Área de Conteúdo Principal */}
            <main className="flex-1 flex flex-col overflow-hidden">
                {/* Topbar */}
                <header className="h-16 flex items-center justify-between px-8 bg-slate-900/30 border-b border-slate-800/50 backdrop-blur-md">
                    <h2 className="text-sm font-medium text-slate-400 uppercase tracking-widest">
                        Painel {user?.is_superadmin ? 'SaaS Global' : 'de Gestão'}
                    </h2>

                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded-full border border-slate-700">
                            <div className={`h-2 w-2 rounded-full ${user?.is_superadmin ? 'bg-amber-400' : 'bg-green-400'} animate-pulse`} />
                            <span className="text-[10px] font-bold text-slate-300 uppercase letter tracking-tighter">
                                {user?.is_superadmin ? 'Super Admin' : 'Tenant Active'}
                            </span>
                        </div>
                    </div>
                </header>

                {/* Conteúdo Dinâmico */}
                <div className="flex-1 overflow-y-auto bg-slate-950 p-8 scrollbar-thin scrollbar-thumb-slate-800">
                    <div className="max-w-7xl mx-auto animate-in fade-in duration-500">
                        {children}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default AdminLayout;
