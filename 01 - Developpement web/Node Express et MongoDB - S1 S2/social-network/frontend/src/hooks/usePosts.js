import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { postService } from '../services/postService';

export const usePosts = (page = 1) => {
    const queryClient = useQueryClient();

    const postsQuery = useQuery({
        queryKey: ['posts', page],
        queryFn: () => postService.getAll(page),
        keepPreviousData: true,
    });

    const createPostMutation = useMutation({
        mutationFn: postService.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['posts'] });
        },
    });

    const deletePostMutation = useMutation({
        mutationFn: postService.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['posts'] });
        },
    });

    const toggleLikeMutation = useMutation({
        mutationFn: ({ postId, userId, isLiked }) => postService.toggleLike(postId, userId, isLiked),
        onSuccess: () => {
            // Invalider pour rafraîchir, mais l'UI optimiste gère l'affichage immédiat
            queryClient.invalidateQueries({ queryKey: ['posts'] });
        },
    });

    return {
        posts: postsQuery.data?.data || [],
        totalPages: postsQuery.data?.totalPages || 1,
        isLoading: postsQuery.isLoading,
        isError: postsQuery.isError,
        error: postsQuery.error,
        createPost: createPostMutation.mutateAsync,
        isCreating: createPostMutation.isPending,
        deletePost: deletePostMutation.mutateAsync,
        toggleLike: toggleLikeMutation.mutateAsync,
    };
};
