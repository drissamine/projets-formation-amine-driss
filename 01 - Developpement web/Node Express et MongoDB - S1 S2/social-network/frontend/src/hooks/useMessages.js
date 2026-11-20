import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { messageService } from '../services/messageService';

export const useMessages = (userId, activeConversationId) => {
    const queryClient = useQueryClient();

    const conversationsQuery = useQuery({
        queryKey: ['conversations', userId],
        queryFn: () => messageService.getConversations(userId),
        enabled: !!userId,
    });

    const messagesQuery = useQuery({
        queryKey: ['messages', userId, activeConversationId],
        queryFn: () => messageService.getMessages(userId, activeConversationId),
        enabled: !!userId && !!activeConversationId,
        refetchInterval: 5000, // Polling every 5s
    });

    const sendMessageMutation = useMutation({
        mutationFn: ({ conversationId, content }) => messageService.sendMessage(conversationId, content),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['messages', userId, activeConversationId] });
            queryClient.invalidateQueries({ queryKey: ['conversations', userId] });
        },
    });

    return {
        conversations: conversationsQuery.data?.data || [],
        messages: messagesQuery.data?.data || [],
        isLoadingConversations: conversationsQuery.isLoading,
        isLoadingMessages: messagesQuery.isLoading,
        sendMessage: sendMessageMutation.mutateAsync,
    };
};
