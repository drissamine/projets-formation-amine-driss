import axios from '../api/axios';

export const statsService = {
    getGlobalStats: async () => {
        const response = await axios.get('/stats');
        return response.data;
    }
};
