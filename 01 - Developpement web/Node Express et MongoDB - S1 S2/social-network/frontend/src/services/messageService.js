import axios from '../api/axios';

export const messageService = {
    getConversations: async (userId) => {
        const response = await axios.get(`/messages/${userId}/conversations`);
        return response.data;
    },

    getMessages: async (userId, otherUserId, limit = 50) => {
        const response = await axios.get(`/messages/${userId}/conversations/${otherUserId}?limit=${limit}`);
        return response.data;
    },

    sendMessage: async (activeConversationId, content) => {
        const response = await axios.post('/messages', {
            receiver: activeConversationId,
            content: content
        });
        return response.data;
    }
};
