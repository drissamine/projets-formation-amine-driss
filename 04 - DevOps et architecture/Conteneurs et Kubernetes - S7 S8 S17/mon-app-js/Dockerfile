# Image de base legere contenant Node.js
FROM node:18-alpine

# Definition du repertoire de travail dans le conteneur
WORKDIR /app

# Copie des fichiers de dependances (optimisation du cache Docker)
COPY package*.json ./

# Installation des dependances de production
RUN npm install --only=production

# Copie du reste du projet
COPY . .

# Securite : utilisation d'un utilisateur non-root
USER node

# Port utilise par l'application
EXPOSE 3000

# Commande de demarrage (forme exec pour une bonne gestion des signaux)
CMD ["node", "server.js"]
