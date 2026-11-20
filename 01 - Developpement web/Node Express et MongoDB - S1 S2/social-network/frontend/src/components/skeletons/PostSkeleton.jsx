import { Skeleton } from '../ui/Skeleton';

export const PostSkeleton = () => {
    return (
        <div className="space-y-6">
            {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4 border border-gray-100 dark:border-gray-700">
                    <div className="flex items-center space-x-3 mb-4">
                        <Skeleton className="h-10 w-10 rounded-full" />
                        <div className="space-y-2">
                            <Skeleton className="h-4 w-32" />
                            <Skeleton className="h-3 w-20" />
                        </div>
                    </div>
                    <div className="space-y-2">
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-5/6" />
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 flex space-x-6">
                        <Skeleton className="h-4 w-12" />
                        <Skeleton className="h-4 w-12" />
                    </div>
                </div>
            ))}
        </div>
    );
};
