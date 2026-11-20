FROM node:24-alpine

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm install --legacy-peer-deps

# Copier le reste de l'application
COPY . .

# Exposer le port 4200
EXPOSE 4200

# Lancer le serveur de développement Angular
CMD ["npx", "ng", "serve", "--host", "0.0.0.0"]
