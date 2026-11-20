# Utiliser une image légère de Node.js
FROM node:18-alpine

# Mettre à jour les paquets système (Fixes CVEs)
RUN apk update && apk upgrade

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer uniquement les dépendances de production
RUN npm ci --omit=dev && \
    rm -rf /usr/local/lib/node_modules/npm /usr/local/bin/npm /root/.npm

# Copier le reste des fichiers de l'application
COPY . .

# Exposer le port de l'application
EXPOSE 3000

# Commande de démarrage (sans npm)
CMD ["node", "server.js"]