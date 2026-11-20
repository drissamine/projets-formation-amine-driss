import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../api/axios';
import { AuthContext } from './AuthContextValue';



const safeStorage = {
  getItem: (key) => {
    try {
      return localStorage.getItem(key);
    } catch (e) {
      console.warn('LocalStorage access denied:', e);
      return null;
    }
  },
  setItem: (key, value) => {
    try {
      localStorage.setItem(key, value);
    } catch (e) {
      console.warn('LocalStorage access denied:', e);
    }
  },
  removeItem: (key) => {
    try {
      localStorage.removeItem(key);
    } catch (e) {
      console.warn('LocalStorage access denied:', e);
    }
  }
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => safeStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Vérifier le token au chargement
  useEffect(() => {
    const verifyToken = async () => {
      if (token) {
        try {
          const response = await axios.get('/users/me', {
            headers: { Authorization: `Bearer ${token}` }
          });
          setUser(response.data.data ? response.data.data : response.data.user);
        } catch (err) {
          console.error('Token verification failed:', err);
          safeStorage.removeItem('token');
          setToken(null);
          setUser(null);
          navigate('/login');
        }
      }
      setLoading(false);
    };

    verifyToken();
  }, [token, navigate]);

  const setTokenSafe = (newToken) => {
    try {
      if (newToken) {
        localStorage.setItem('token', newToken);
      } else {
        localStorage.removeItem('token');
      }
      setToken(newToken);
    } catch (e) {
      console.warn('LocalStorage access denied via setTokenSafe', e);
      setToken(newToken); // Update state anyway
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post('/users/login', { email, motDePasse: password });
      const { token, user } = response.data;

      setTokenSafe(token);
      setUser(user);
      setError(null);

      // Configure axios default header for subsequent requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      return true;
    } catch (err) {
      console.error("Login Error Full Object:", err);
      console.error("Login Error Response:", err.response);
      console.error("Login Error Message:", err.message);

      const errorMessage = err.response?.data?.erreur || err.message || 'Login failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  };

  const logout = () => {
    setTokenSafe(null);
    setUser(null);
    navigate('/login');
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API_URL}/users`, userData);
      return { success: true, user: response.data.user };
    } catch (err) {
      return { success: false, error: err.response?.data?.erreur || 'Registration failed' };
    }
  };

  const updateProfile = async (userData) => {
    try {
      const response = await axios.put(`${API_URL}/users/${user._id}`, userData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data.user);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.response?.data?.erreur || 'Update failed' };
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, error, login, logout, register, updateProfile }}>
      {loading ? (
        <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
};
