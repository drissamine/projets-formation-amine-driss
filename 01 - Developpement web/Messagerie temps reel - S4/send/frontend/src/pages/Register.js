import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '@heroui/react';
import { FaEye, FaEyeSlash, FaUser, FaGoogle, FaGithub } from 'react-icons/fa';
import { HiOutlineMail, HiOutlineLockClosed } from 'react-icons/hi';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [isConfirmPasswordVisible, setIsConfirmPasswordVisible] = useState(false);
  const [localError, setLocalError] = useState('');

  const { register, error: authError, clearError } = useAuth();
  const navigate = useNavigate();

  const togglePasswordVisibility = () => setIsPasswordVisible(!isPasswordVisible);
  const toggleConfirmPasswordVisibility = () => setIsConfirmPasswordVisible(!isConfirmPasswordVisible);



  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (authError) clearError();
    if (localError) setLocalError('');
  };

  const validateForm = () => {
    if (!formData.username.trim()) {
      return 'Le nom d\'utilisateur est requis';
    }

    if (!formData.email.trim()) {
      return 'L\'email est requis';
    }

    if (!formData.password) {
      return 'Le mot de passe est requis';
    }

    if (!formData.confirmPassword) {
      return 'La confirmation du mot de passe est requise';
    }

    if (formData.password !== formData.confirmPassword) {
      return 'Les mots de passe ne correspondent pas';
    }

    if (formData.password.length < 6) {
      return 'Le mot de passe doit contenir au moins 6 caractères';
    }

    if (formData.username.length < 3) {
      return 'Le nom d\'utilisateur doit contenir au moins 3 caractères';
    }

    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      setLocalError(validationError);
      return;
    }

    setIsLoading(true);

    try {
      const result = await register({
        username: formData.username,
        email: formData.email,
        password: formData.password
      });
      
      if (result.success) {
        navigate('/chat');
      }
    } catch (error) {
      console.error('Erreur d\'inscription:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const error = localError || authError;

  return (
    <div className="flex min-h-screen w-full bg-gray-50 dark:bg-gray-900">
      {/* Côté gauche - Visuel / Image de marque */}
      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-blue-600 to-indigo-700 relative overflow-hidden items-center justify-center p-12 text-white">
        <div className="absolute inset-0 bg-black/10"></div>
        {/* Cercles décoratifs */}
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse"></div>
        <div className="absolute top-0 -right-4 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-80 h-80 bg-teal-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse animation-delay-4000"></div>

        <div className="z-10 text-center max-w-lg">
          <h1 className="text-5xl font-bold mb-6 tracking-tight">Rejoignez la Communauté.</h1>
          <p className="text-lg text-blue-100 mb-8">
            Créez votre compte aujourd'hui et commencez à échanger avec des milliers d'utilisateurs.
          </p>
          <div className="grid grid-cols-2 gap-4 text-left">
             <div className="p-4 bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20">
                <div className="font-bold text-lg mb-1">Sécurisé</div>
                <div className="text-xs text-blue-200">Vos données sont protégées par un chiffrement de bout en bout.</div>
             </div>
             <div className="p-4 bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20">
                <div className="font-bold text-lg mb-1">Gratuit</div>
                <div className="text-xs text-blue-200">Accès illimité à toutes les fonctionnalités de base.</div>
             </div>
          </div>
        </div>
      </div>

      {/* Côté droit - Formulaire */}
      <div className="flex w-full lg:w-1/2 items-center justify-center p-8 bg-white dark:bg-gray-900">
        <div className="w-full max-w-md space-y-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white">Créer un compte</h2>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Remplissez le formulaire ci-dessous pour commencer.
            </p>
          </div>

          <div className="space-y-6">
              {error && (
                 <div className="p-4 rounded-lg bg-red-50 border-l-4 border-red-500 text-red-700 text-sm">
                   <p className="font-bold">Erreur</p>
                   <p>{error}</p>
                 </div>
              )}

              <form onSubmit={handleSubmit} className="flex flex-col gap-6">
                <div className="space-y-2">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FaUser className="text-gray-400" />
                    </div>
                    <input
                      type="text"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      placeholder="jdoe"
                      className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <HiOutlineMail className="text-gray-400" />
                    </div>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="votre@email.com"
                      className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <HiOutlineLockClosed className="text-gray-400" />
                    </div>
                    <input
                      type={isPasswordVisible ? "text" : "password"}
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="••••••••"
                      className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                      required
                    />
                    <button
                      className="absolute inset-y-0 right-0 pr-3 flex items-center focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
                      type="button"
                      onClick={togglePasswordVisibility}
                      aria-label={isPasswordVisible ? "Cacher le mot de passe" : "Afficher le mot de passe"}
                    >
                      {isPasswordVisible ? (
                        <FaEyeSlash className="text-gray-400" />
                      ) : (
                        <FaEye className="text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <HiOutlineLockClosed className="text-gray-400" />
                    </div>
                    <input
                      type={isConfirmPasswordVisible ? "text" : "password"}
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      placeholder="••••••••"
                      className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                      required
                    />
                    <button
                      className="absolute inset-y-0 right-0 pr-3 flex items-center focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
                      type="button"
                      onClick={toggleConfirmPasswordVisibility}
                      aria-label={isConfirmPasswordVisible ? "Cacher le mot de passe" : "Afficher le mot de passe"}
                    >
                      {isConfirmPasswordVisible ? (
                        <FaEyeSlash className="text-gray-400" />
                      ) : (
                        <FaEye className="text-gray-400" />
                      )}
                    </button>
                  </div>
                </div>

                <div className="pt-2">
                  <Button
                    type="submit"
                    size="lg"
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-lg hover:shadow-blue-500/30 transition-all duration-200 transform hover:-translate-y-0.5"
                    loading={isLoading}
                    disabled={isLoading}
                    aria-label="Créer un compte"
                  >
                    {isLoading ? 'Création en cours...' : 'Créer mon compte'}
                  </Button>
                </div>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-gray-300"></span>
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-white px-2 text-gray-500 dark:bg-gray-900 dark:text-gray-400">Ou s'inscrire avec</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    disabled
                    className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-lg shadow-sm bg-gray-50 text-sm font-medium text-gray-400 cursor-not-allowed focus:outline-none transition-colors duration-200"
                  >
                    <FaGoogle className="w-5 h-5 text-red-300 mr-2" />
                    Bientôt disponible
                  </button>

                  <button
                    type="button"
                    disabled
                    className="w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-lg shadow-sm bg-gray-50 text-sm font-medium text-gray-400 cursor-not-allowed focus:outline-none transition-colors duration-200"
                  >
                    <FaGithub className="w-5 h-5 text-gray-400 mr-2" />
                    Bientôt disponible
                  </button>
                </div>
              </form>
          </div>
           
          <p className="text-center text-sm text-gray-600 dark:text-gray-400">
            Déjà un compte ?{' '}
            <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-500 transition-colors">
              Se connecter
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
