import axios from 'axios';

const instance = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Intercepteur pour ajouter le token
instance.interceptors.request.use(
    (config) => {
        try {
            const token = localStorage.getItem('token');
            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`;
            }
        } catch (e) {
            console.warn('Axios interceptor: LocalStorage access denied', e);
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default instance;
