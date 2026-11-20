const mongoose = require('mongoose');
const bcryptjs = require('bcryptjs');

const userSchema = new mongoose.Schema({
    nom: { type: String, required: true },
    email: { type: String, required: true, unique: true },
    motDePasse: { type: String, required: true },
    nombreFollowers: { type: Number, default: 0 },
    nombreFollowing: { type: Number, default: 0 },
    nombrePosts: { type: Number, default: 0 },
    followers: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],
    following: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],
    createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model('User', userSchema);

const createDemoUser = async () => {
    try {
        await mongoose.connect('mongodb+srv://drissamine_db_user:XmfechJ7naOLb6iM@cluster0.3m8cfzg.mongodb.net/test'); // Utilise 'test' comme vu dans les logs
        console.log('Connecté à MongoDB');

        const email = 'demo@example.com';
        const pwd = 'password123';

        // Check existing
        const existing = await User.findOne({ email });
        if (existing) {
            console.log('Utilisateur demo existe déjà, mise à jour du mot de passe...');
            const salt = await bcryptjs.genSalt(10);
            existing.motDePasse = await bcryptjs.hash(pwd, salt);
            await existing.save(); // Attention: save() utilise le hook si défini dans le modèle chargé via require... 
            // Mais ici j'ai redéfini le schéma LOCALEMENT sans hook ! Donc pas de risque.
            console.log('Utilisateur demo mis à jour.');
        } else {
            console.log('Création de l\'utilisateur demo...');
            const salt = await bcryptjs.genSalt(10);
            const hashedPassword = await bcryptjs.hash(pwd, salt);

            await User.create({
                nom: 'Demo User',
                email: email,
                motDePasse: hashedPassword
            });
            console.log('Utilisateur demo créé avec succès.');
        }

        mongoose.connection.close();
    } catch (err) {
        console.error('Erreur:', err);
        process.exit(1);
    }
};

createDemoUser();
