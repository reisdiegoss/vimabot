import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

import { PublicRoute, PrivateRoute, AdminRoute } from './Guards';

// Lazy load das páginas para melhor performance
// FASE 5: Admin / Tenant
const Login = React.lazy(() => import('../pages/admin/Login'));
const AdminDashboard = React.lazy(() => import('../pages/admin/Dashboard'));
const AdminTenants = React.lazy(() => import('../pages/admin/Tenants'));
const TenantDashboard = React.lazy(() => import('../pages/tenant/Dashboard'));
const TenantBotConfig = React.lazy(() => import('../pages/tenant/BotConfig'));
const TenantCatalog = React.lazy(() => import('../pages/tenant/Catalog'));
const TenantOrders = React.lazy(() => import('../pages/tenant/Orders'));

// FASE 6: Telegram WebApp
const WebAppCatalog = React.lazy(() => import('../pages/webapp/Catalog'));

/**
 * Switcher central de rotas da aplicação.
 * Divide a navegação entre áreas públicas, protegidas por login 
 * e acessíveis apenas por Super-Admin.
 */
const AppRoutes: React.FC = () => {
    return (
        <React.Suspense fallback={
            <div className="flex h-screen w-full items-center justify-center bg-background">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-netflix-red border-t-transparent"></div>
            </div>
        }>
            <Routes>
                {/* Rotas Públicas */}
                <Route element={<PublicRoute />}>
                    <Route path="/admin/login" element={<Login />} />
                </Route>

                {/* Rotas Protegidas (SaaS Panel) */}
                <Route element={<PrivateRoute />}>
                    {/* Dashboard Geral (Redirect baseado em Role) */}
                    <Route path="/admin/dashboard" element={<TenantDashboard />} />

                    {/* Rotas Super-Admin */}
                    <Route element={<AdminRoute />}>
                        <Route path="/admin/super" element={<AdminDashboard />} />
                        <Route path="/admin/tenants" element={<AdminTenants />} />
                    </Route>

                    {/* Rotas Tenant (Inquilino) */}
                    <Route path="/admin/bot" element={<TenantBotConfig />} />
                    <Route path="/admin/catalog" element={<TenantCatalog />} />
                    <Route path="/admin/orders" element={<TenantOrders />} />
                </Route>

                {/* Universo Telegram Mini App (Sempre Público) */}
                <Route path="/webapp/:tenant_id" element={<WebAppCatalog />} />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/admin/login" replace />} />
            </Routes>
        </React.Suspense>
    );
};

export default AppRoutes;
