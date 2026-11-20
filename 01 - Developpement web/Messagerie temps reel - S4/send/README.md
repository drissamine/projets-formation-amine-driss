# Application Web de Messagerie en Temps Réel

Une application de messagerie moderne et complète construite avec Node.js, Express, MongoDB, React et Socket.io.

## 🚀 Fonctionnalités

### ✅ Authentification
- Inscription/Connexion utilisateur
- Réinitialisation de mot de passe
- Hachage sécurisé des mots de passe (bcrypt)
- Tokens JWT avec renouvellement automatique
- Protection des routes sensibles

### ✅ Canaux de Discussion
- Création de canaux publics/privés
- Rejoindre/quitter des canaux
- Gestion des participants et rôles
- Recherche de canaux

### ✅ Messagerie
- Envoi/réception de messages en temps réel
- Historique des messages avec pagination
- Modification/suppression de messages
- Réactions aux messages
- Recherche dans les messages

### ✅ Interface Utilisateur
- Design responsive et moderne
- Sidebar avec liste des canaux
- Zone de chat avec messages en temps réel
- Indicateurs de statut utilisateur
- Notifications toast

### ✅ Sécurité
- Rate limiting
- Validation des données
- Middleware d'authentification
- Protection CORS
- Gestion d'erreurs robuste

## 🏗️ Architecture

### Backend (Node.js + Express)
```
backend/
├── config/
│   └── database.js          # Connexion MongoDB
├── controllers/
│   ├── authController.js   # Logique authentification
│   ├── channelController.js# Logique canaux
│   └── messageController.js# Logique messages
├── middleware/
│   └── auth.js            # Middleware JWT
├── models/
│   ├── User.js            # Modèle utilisateur
│   ├── Channel.js         # Modèle canal
│   └── Message.js         # Modèle message
├── routes/
│   ├── auth.js           # Routes authentification
│   ├── channels.js       # Routes canaux
│   └── messages.js       # Routes messages
├── utils/
│   └── jwt.js            # Utilitaires JWT
├── app.js                # Configuration Express
└── server.js             # Serveur principal
```

### Frontend (React)
```
frontend/src/
├── components/           # Composants réutilisables
├── context/
│   └── AuthContext.js   # Context authentification
├── hooks/               # Hooks personnalisés
├── pages/
│   ├── Login.js         # Page de connexion
│   ├── Register.js      # Page d'inscription
│   └── Chat.js          # Page principale
├── services/
│   ├── api.js          # Service API principal
│   ├── authService.js  # Service authentification
│   ├── channelService.js # Service canaux
│   └── messageService.js # Service messages
├── App.js              # Application principale
└── index.js            # Point d'entrée
```

## 🛠️ Installation

### Prérequis
- Node.js (>= 16.0.0)
- npm (>= 8.0.0)
- MongoDB (local ou MongoDB Atlas)

### Installation



1. **Installer les dépendances**
   ```bash
   # Installer les dépendances racine
   npm install
   
   # Installer les dépendances backend
   cd backend
   npm install
   
   # Installer les dépendances frontend
   cd ../frontend
   npm install
   ```

2. **Configuration de la base de données**
   - Créez un compte sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) ou utilisez une instance locale
   - Copiez l'URI de connexion

3. **Configuration des variables d'environnement**
   
   **Backend (.env)**
   ```bash
   cp backend/.env.example backend/.env
   ```
  backend/.env` Éditez ` :
   ```env
   MONGODB_URI=your_mongodb_connection_string
   JWT_SECRET=your_super_secret_jwt_key
   JWT_REFRESH_SECRET=your_super_secret_refresh_key
   PORT=5000
   FRONTEND_URL=http://localhost:3000
   ```
   
   **Frontend (.env)**
   ```bash
   cp frontend/.env.example frontend/.env
   ```
   Éditez `frontend/.env` :
   ```env
   REACT_APP_API_URL=http://localhost:5000/api
   REACT_APP_SOCKET_URL=http://localhost:5000
   ```

## 🚀 Lancement

### Développement
```bash
# Lancer backend et frontend simultanément
npm run dev

# Ou séparément
npm run dev:backend  # Backend sur http://localhost:5000
npm run dev:frontend # Frontend sur http://localhost:3000
```

### Production
```bash
# Construire le frontend
npm run build

# Lancer le serveur backend
npm start
```

## 📚 API Endpoints

### Authentification
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `POST /api/auth/logout` - Déconnexion
- `GET /api/auth/profile` - Profil utilisateur
- `PUT /api/auth/profile` - Mise à jour profil
- `POST /api/auth/refresh` - Renouveler token

### Canaux
- `GET /api/channels` - Liste des canaux
- `POST /api/channels` - Créer un canal
- `GET /api/channels/:id` - Détails d'un canal
- `POST /api/channels/:id/join` - Rejoindre un canal
- `POST /api/channels/:id/leave` - Quitter un canal
- `PUT /api/channels/:id` - Mettre à jour un canal
- `DELETE /api/channels/:id` - Supprimer un canal
- `GET /api/channels/search` - Rechercher des canaux

### Messages
- `POST /api/messages` - Envoyer un message
- `GET /api/messages/channel/:channelId` - Messages d'un canal
- `GET /api/messages/:id` - Détails d'un message
- `PUT /api/messages/:id` - Modifier un message
- `DELETE /api/messages/:id` - Supprimer un message
- `POST /api/messages/:id/reactions` - Ajouter une réaction
- `DELETE /api/messages/:id/reactions/:emoji` - Retirer une réaction
- `GET /api/messages/search/:channelId` - Rechercher des messages

## 🔐 Sécurité

- **Authentification JWT** avec tokens d'accès et de rafraîchissement
- **Hachage bcrypt** pour les mots de passe
- **Rate limiting** pour prévenir les attaques
- **Validation des données** avec express-validator
- **CORS configuré** pour la sécurité cross-origin
- **Helmet.js** pour les headers de sécurité
- **Protection des routes** avec middleware d'authentification

## 🎨 Interface

### Design Responsive
- Interface adaptative pour mobile, tablette et desktop
- Thème moderne avec gradients et animations
- Scrollbar personnalisée
- Animations fluides et feedback visuel

### Fonctionnalités UX
- États de chargement
- Gestion d'erreurs avec notifications
- Formulaires avec validation en temps réel
- Navigation intuitive
- Indicateurs de statut

## 🗄️ Base de Données

### Modèles MongoDB

**User**
- Informations d'authentification (email, username, password)
- Avatar et statut (online/offline/away)
- Liste des canaux membership
- Timestamps (createdAt, updatedAt)

**Channel**
- Nom, description et type (public/private/direct)
- Créateur et participants avec rôles
- Dernier message et statut d'activité
- Timestamps

**Message**
- Contenu et type (text/image/file/system)
- Auteur et canal associé
- Pièces jointes et réponses
- Réactions et mentions
- États d'édition/suppression
- Timestamps

## 🚀 Déploiement

### Heroku
1. Créez une app Heroku
2. Ajoutez MongoDB Atlas comme addon
3. Configurez les variables d'environnement
4. Déployez le code

```bash
# Commandes Heroku
heroku create messagerie-app
heroku addons:create mongolab:sandbox
git push heroku main
heroku config:set JWT_SECRET=your_secret
```

### Autres plateformes
- **Vercel** (Frontend) + **Railway/Render** (Backend)
- **Netlify** (Frontend) + **DigitalOcean** (Backend)
- **AWS/GCP/Azure** pour une solution complète

## 🧪 Tests

```bash
# Tests backend
cd backend && npm test

# Tests frontend
cd frontend && npm test
```

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- [Express.js](https://expressjs.com/) - Framework web pour Node.js
- [React](https://reactjs.org/) - Bibliothèque JavaScript pour interfaces utilisateur
- [MongoDB](https://www.mongodb.com/) - Base de données NoSQL
- [Socket.io](https://socket.io/) - Communication temps réel
- [JWT](https://jwt.io/) - JSON Web Tokens
- [bcrypt](https://www.npmjs.com/package/bcrypt) - Hachage de mots de passe

---

**Développé avec ❤️ pour une expérience de messagerie moderne et sécurisée**
