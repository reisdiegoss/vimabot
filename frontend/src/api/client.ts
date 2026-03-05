import axios from 'axios';

/**
 * Instância centralizada do Axios para comunicação com o Backend FastAPI.
 * 
 * Configurações incluídas:
 * - URL base vinda das variáveis de ambiente.
 * - Interceptor de Request: Injeta o token JWT do localStorage em todas as chamadas.
 * - Interceptor de Response: Captura erros 401 e limpa o estado de login se necessário.
 */
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor para injetar o Token JWT em cada requisição
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('@VimaBOT:token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor para tratamento global de erros (ex: Token expirado)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Se receber 401 Unauthorized, removemos o token e deslogamos o usuário
            localStorage.removeItem('@VimaBOT:token');
            localStorage.removeItem('@VimaBOT:user');

            // Redireciona para login se não estiver em ambiente de catálogo público
            if (!window.location.pathname.startsWith('/webapp')) {
                window.location.href = '/admin/login';
            }
        }
        return Promise.reject(error);
    }
);

export default api;
