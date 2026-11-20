import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { HeroUIProvider } from '@heroui/react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import OAuthCallback from './pages/OAuthCallback';
import Chat from './pages/Chat';

// Composant pour protéger les routes authentifiées
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="chat-loading">
        <div className="loading-spinner"></div>
        <p>Vérification de l'authentification...</p>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Composant pour rediriger les utilisateurs déjà connectés
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="chat-loading">
        <div className="loading-spinner"></div>
        <p>Chargement...</p>
      </div>
    );
  }

  return !isAuthenticated ? children : <Navigate to="/chat" replace />;
};

function App() {
  return (
    <ThemeProvider>
      <HeroUIProvider>
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <AuthProvider>
            <div className="App">
            <Routes>
              {/* Routes publiques (non authentifiées) */}
              <Route 
                path="/login" 
                element={
                  <PublicRoute>
                    <Login />
                  </PublicRoute>
                } 
              />
              <Route
                path="/register"
                element={
                  <PublicRoute>
                    <Register />
                  </PublicRoute>
                }
              />
              <Route
                path="/forgot-password"
                element={
                  <PublicRoute>
                    <ForgotPassword />
                  </PublicRoute>
                }
              />
              <Route
                path="/auth/callback"
                element={
                  <PublicRoute>
                    <OAuthCallback />
                  </PublicRoute>
                }
              />
              
              {/* Routes protégées (authentifiées) */}
              <Route 
                path="/chat" 
                element={
                  <ProtectedRoute>
                    <Chat />
                  </ProtectedRoute>
                } 
              />
              
              {/* Redirection par défaut */}
              <Route path="/" element={<Navigate to="/chat" replace />} />
              
              {/* Route 404 */}
              <Route 
                path="*" 
                element={
                  <div className="chat-loading">
                    <h2>Page non trouvée</h2>
                    <p>La page que vous recherchez n'existe pas.</p>
                  </div>
                } 
              />
            </Routes>
            
            {/* Notifications toast */}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  duration: 3000,
                  iconTheme: {
                    primary: '#4ade80',
                    secondary: '#fff',
                  },
                },
                error: {
                  duration: 5000,
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: '#fff',
                  },
                },
              }}
            />
          </div>
        </AuthProvider>
      </Router>
      </HeroUIProvider>
    </ThemeProvider>
  );
}

export default App;
