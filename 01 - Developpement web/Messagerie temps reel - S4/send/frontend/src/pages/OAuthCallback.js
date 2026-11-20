import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Button, Card, CardBody } from "@heroui/react";
import { motion } from "framer-motion";
import ThemeToggle from "../components/ThemeToggle";

const OAuthCallback = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { loginWithOAuth } = useAuth();

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        // Extraire les paramètres de l'URL
        const urlParams = new URLSearchParams(location.search);
        const token = urlParams.get('token');
        const refreshToken = urlParams.get('refreshToken');
        const user = urlParams.get('user');

        if (!token || !refreshToken || !user) {
          throw new Error('Informations OAuth manquantes dans l\'URL');
        }

        // Tenter de connecter l'utilisateur avec les tokens reçus
        const result = await loginWithOAuth({
          token,
          refreshToken,
          user: JSON.parse(user)
        });

        if (result.success) {
          // Rediriger vers le chat après une courte pause
          setTimeout(() => {
            navigate('/chat');
          }, 1000);
        } else {
          throw new Error(result.message || 'Erreur lors de la connexion OAuth');
        }
      } catch (err) {
        console.error('Erreur OAuth callback:', err);
        setError(err.message);
        setIsLoading(false);
      }
    };

    handleOAuthCallback();
  }, [location, navigate, loginWithOAuth]);

  return (
    <div className="flex min-h-screen w-full bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 relative">
      {/* Theme Toggle */}
      <div className="absolute top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      <div className="flex w-full items-center justify-center p-8 lg:p-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md space-y-8"
        >
          <Card className="border-none shadow-xl bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl overflow-hidden">
            <CardBody className="p-8 space-y-6">
              <div className="text-center">
                <motion.h2 
                  className="text-3xl font-extrabold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent"
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6 }}
                >
                  {isLoading ? "Authentification en cours..." : "Erreur d'authentification"}
                </motion.h2>
                <motion.p 
                  className="mt-2 text-sm text-gray-600 dark:text-gray-400"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                >
                  {isLoading 
                    ? "Veuillez patienter pendant que nous finalisons votre connexion..." 
                    : "Une erreur est survenue lors de votre authentification."
                  }
                </motion.p>
              </div>

              {isLoading ? (
                <div className="flex justify-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                </div>
              ) : (
                <div className="space-y-4">
                  {error && (
                    <div className="p-4 rounded-lg bg-red-50/50 border-l-4 border-red-500 text-red-700 text-sm dark:bg-red-900/20 dark:text-red-300">
                      <p className="font-bold">Erreur</p>
                      <p>{error}</p>
                    </div>
                  )}
                  
                  <div className="flex gap-4">
                    <Button
                      variant="bordered"
                      className="flex-1 font-medium text-gray-700 border-gray-300 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700 transition-all duration-200"
                      onClick={() => navigate('/login')}
                    >
                      Retour à la connexion
                    </Button>
                    <Button
                      className="flex-1 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700 text-white font-bold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
                      onClick={() => navigate('/register')}
                    >
                      Créer un compte
                    </Button>
                  </div>
                </div>
              )}
            </CardBody>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default OAuthCallback;