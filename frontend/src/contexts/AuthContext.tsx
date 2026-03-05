import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, AuthResponse } from '../types/auth';
import api from '../api/client';

interface AuthContextData {
    user: User | null;
    loading: boolean;
    signIn: (data: AuthResponse) => void;
    signOut: () => void;
}

const AuthContext = createContext<AuthContextData>({} as AuthContextData);

/**
 * Provedor de Autenticação Global.
 * Gerencia o estado do usuário logado, persistência no localStorage e 
 * sincronização com o token JWT.
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Carrega dados persistidos ao inicializar o app
        function loadStorageData() {
            const storedUser = localStorage.getItem('@VimaBOT:user');
            const storedToken = localStorage.getItem('@VimaBOT:token');

            if (storedUser && storedToken) {
                setUser(JSON.parse(storedUser));
            }
            setLoading(false);
        }

        loadStorageData();
    }, []);

    const signIn = (data: AuthResponse) => {
        const userData: User = {
            tenant_id: data.tenant_id,
            email: data.email,
            company_name: data.company_name,
            is_superadmin: data.is_superadmin,
        };

        localStorage.setItem('@VimaBOT:token', data.access_token);
        localStorage.setItem('@VimaBOT:user', JSON.stringify(userData));

        setUser(userData);
    };

    const signOut = () => {
        localStorage.removeItem('@VimaBOT:token');
        localStorage.removeItem('@VimaBOT:user');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, signIn, signOut }}>
            {children}
        </AuthContext.Provider>
    );
};

// Hook personalizado para facilitar o uso do contexto em outros componentes
export function useAuth() {
    const context = useContext(AuthContext);

    if (!context) {
        throw new Error('useAuth deve ser usado dentro de um AuthProvider');
    }

    return context;
}
