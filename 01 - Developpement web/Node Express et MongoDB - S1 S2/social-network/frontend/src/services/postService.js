import axios from '../api/axios';

export const postService = {
    getAll: async (page = 1, limit = 10) => {
        const response = await axios.get(`/posts?page=${page}&limit=${limit}`);
        return response.data;
    },

    create: async (formData) => {
        // Note: Do not set explicit Content-Type header when using FormData; 
        // let the browser set it with the boundary.
        const response = await axios.post('/posts', formData);
        return response.data;
    },

    delete: async (postId) => {
        const response = await axios.delete(`/posts/${postId}`);
        return response.data;
    },

    toggleLike: async (postId, userId, isLiked) => {
        const endpoint = isLiked ? 'unlike' : 'like';
        const response = await axios.post(`/posts/${postId}/${endpoint}/${userId}`);
        return response.data;
    }
};
