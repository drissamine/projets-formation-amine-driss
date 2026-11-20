const Profile = () => {
    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">Mon Profil</h1>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <div className="flex items-center space-x-4 mb-6">
                    <div className="h-20 w-20 rounded-full bg-blue-500 flex items-center justify-center text-white text-2xl font-bold">
                        U
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Utilisateur</h2>
                        <p className="text-gray-500 dark:text-gray-400">user@example.com</p>
                    </div>
                </div>
                <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                    <h3 className="font-semibold mb-2 text-gray-900 dark:text-white">Détails</h3>
                    <p className="text-gray-700 dark:text-gray-300">Membre depuis: Janvier 2024</p>
                </div>
            </div>
        </div>
    );
};
export default Profile;
