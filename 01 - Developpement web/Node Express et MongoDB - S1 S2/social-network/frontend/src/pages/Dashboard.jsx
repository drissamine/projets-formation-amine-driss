import { useStats } from '../hooks/useStats';
import { BarChart2, Users, FileText, MessageSquare, TrendingUp, Activity } from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, color, subtitle }) => (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-100 dark:border-gray-700">
        <div className="flex items-center justify-between">
            <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
                <h3 className="text-3xl font-bold mt-2 text-gray-900 dark:text-white">{value}</h3>
                {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
            </div>
            <div className={`p-4 rounded-full ${color}`}>
                <Icon className="w-6 h-6 text-white" />
            </div>
        </div>
    </div>
);

const Dashboard = () => {
    const { stats, isLoading, isError, error } = useStats();

    if (isLoading) return (
        <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
    );

    if (isError) return (
        <div className="p-6 text-red-500 bg-red-50 rounded-lg">
            <p>Impossible de charger les statistiques : {error.message}</p>
        </div>
    );

    if (!stats) return null;

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8">
            <div className="flex items-center space-x-3 mb-8">
                <Activity className="w-8 h-8 text-primary" />
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Tableau de Bord</h1>
            </div>

            {/* Cartes principales */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <StatCard
                    title="Utilisateurs"
                    value={stats.users?.totalUsers || 0}
                    subtitle={`Moy. ${Math.round(stats.users?.avgFollowers || 0)} followers/user`}
                    icon={Users}
                    color="bg-blue-500"
                />
                <StatCard
                    title="Posts Publiés"
                    value={stats.posts?.totalPosts || 0}
                    subtitle={`Moy. ${Math.round(stats.posts?.avgLikes || 0)} likes/post`}
                    icon={FileText}
                    color="bg-green-500"
                />
                <StatCard
                    title="Messages Échangés"
                    value={stats.messages?.totalMessages || 0}
                    subtitle={`${stats.messages?.unreadMessages || 0} non lus`}
                    icon={MessageSquare}
                    color="bg-purple-500"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Utilisateurs Actifs */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-100 dark:border-gray-700">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Utilisateurs les plus actifs</h2>
                        <TrendingUp className="w-5 h-5 text-gray-400" />
                    </div>
                    <div className="space-y-4">
                        {stats.activeUsers?.map((user, index) => (
                            <div key={index} className="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-750 rounded-lg transition-colors">
                                <div className="flex items-center space-x-3">
                                    <div className="shrink-0 w-8 h-8 bg-linear-to-br from-blue-400 to-indigo-500 rounded-full flex items-center justify-center text-white font-bold text-xs">
                                        {user.nom?.charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                        <p className="font-semibold text-gray-900 dark:text-white">{user.nom}</p>
                                        <p className="text-xs text-gray-500">{user.nombreFollowers} abonnés</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <span className="inline-block px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">
                                        {user.nombrePosts} posts
                                    </span>
                                </div>
                            </div>
                        ))}
                        {stats.activeUsers?.length === 0 && (
                            <p className="text-center text-gray-500 py-4">Aucune donnée disponible</p>
                        )}
                    </div>
                </div>

                {/* Posts Populaires */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-100 dark:border-gray-700">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Contenus Populaires</h2>
                        <BarChart2 className="w-5 h-5 text-gray-400" />
                    </div>
                    <div className="space-y-4">
                        {stats.popularPosts?.map((post, index) => (
                            <div key={index} className="p-4 border border-gray-100 dark:border-gray-700 rounded-lg hover:shadow-sm transition-shadow">
                                <p className="text-gray-800 dark:text-gray-200 line-clamp-2 text-sm mb-2">
                                    "{post.contenu}"
                                </p>
                                <div className="flex justify-between items-center text-xs text-gray-500">
                                    <span>{new Date(post.createdAt).toLocaleDateString()}</span>
                                    <span className="flex items-center text-red-500 font-medium">
                                        ❤️ {post.nombreLikes}
                                    </span>
                                </div>
                            </div>
                        ))}
                        {stats.popularPosts?.length === 0 && (
                            <p className="text-center text-gray-500 py-4">Aucune donnée disponible</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
