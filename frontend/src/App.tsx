import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import AppRoutes from './routes';
import './index.css';

/**
 * Componente Raiz da Aplicação.
 * Envolve a aplicação com os provedores necessários:
 * - AuthProvider: Estado global de autenticação.
 * - BrowserRouter: Gerenciamento de rotas.
 */
const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
