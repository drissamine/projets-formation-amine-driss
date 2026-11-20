import { useQuery } from '@tanstack/react-query';
import { statsService } from '../services/statsService';

export const useStats = () => {
    const statsQuery = useQuery({
        queryKey: ['stats'],
        queryFn: statsService.getGlobalStats,
    });

    return {
        stats: statsQuery.data?.stats,
        isLoading: statsQuery.isLoading,
        isError: statsQuery.isError,
        error: statsQuery.error,
    };
};
