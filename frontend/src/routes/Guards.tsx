import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Componente que protege rotas que exigem autenticação.
 * Redireciona para o login se o usuário não estiver autenticado.
 */
export const PrivateRoute: React.FC = () => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="flex h-screen w-full items-center justify-center bg-background text-foreground">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            </div>
        );
    }

    return user ? <Outlet /> : <Navigate to="/admin/login" replace />;
};

/**
 * Componente que protege rotas exclusivas do Super-Admin.
 * Redireciona para o Dashboard do Tenant se o usuário for um inquilino comum.
 */
export const AdminRoute: React.FC = () => {
    const { user } = useAuth();

    if (!user?.is_superadmin) {
        return <Navigate to="/admin/dashboard" replace />;
    }

    return <Outlet />;
};

/**
 * Componente para rotas públicas que não devem ser acessadas se logado (ex: Login).
 * Redireciona para o dashboard se o usuário já estiver autenticado.
 */
export const PublicRoute: React.FC = () => {
    const { user, loading } = useAuth();

    if (loading) return null;

    return user ? <Navigate to="/admin/dashboard" replace /> : <Outlet />;
};
