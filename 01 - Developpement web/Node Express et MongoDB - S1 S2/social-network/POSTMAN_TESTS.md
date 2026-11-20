# Plan de Test Postman - API Posts

## Vue d'ensemble
Ce document contient tous les tests nécessaires pour valider l'API posts du réseau social.

## Prérequis
1. Démarrer le serveur : `npm start` (ou `node app.js`)
2. MongoDB doit être en cours d'exécution
3. Postman installé et configuré
4. URL de base : `http://localhost:3000/api`

## Endpoints à tester

### 1. POST /api/posts - Créer des posts

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "contenu": "Mon premier post de test",
  "auteur": "5f8b7c6d5e4f3a2b1c9d8e7f",
  "images": ["https://example.com/image1.jpg"]
}
```

**Tests à effectuer:**
- [ ] Test avec données valides (201 Created)
- [ ] Test sans contenu (400 Bad Request)
- [ ] Test sans auteur (400 Bad Request)
- [ ] Test avec auteur inexistant (400 Bad Request)
- [ trop long (> ] Test avec contenu5000 caractères)

### 2. GET /api/posts - Lister tous les posts

**URL:** `http://localhost:3000/api/posts`

**Tests à effectuer:**
- [ ] Test avec posts existants (200 OK)
- [ ] Test avec liste vide (200 OK)
- [ ] Vérifier la structure de réponse
- [ ] Vérifier le populate des auteurs et commentaires

### 3. GET /api/posts/user/:userId - Posts d'un utilisateur

**URL:** `http://localhost:3000/api/posts/user/5f8b7c6d5e4f3a2b1c9d8e7f`

**Tests à effectuer:**
- [ ] Test avec utilisateur existant (200 OK)
- [ ] Test avec utilisateur sans posts (200 OK)
- [ ] Test avec ID utilisateur inexistant (200 OK - liste vide)
- [ ] Test avec ID invalide (400 Bad Request)

### 4. POST /api/posts/:id/like/:userId - Liker un post

**URL:** `http://localhost:3000/api/posts/5f8b7c6d5e4f3a2b1c9d8e7f/like/5f9c8d7e6f5a4b3c2d1e0f9a`

**Tests à effectuer:**
- [ ] Test avec post et utilisateur valides (200 OK)
- [ ] Test avec ID post inexistant (404 Not Found)
- [ ] Test avec ID utilisateur inexistant (400 Bad Request)
- [ ] Test de double like (même résultat)
- [ ] Vérifier l'incrémentation du compteur

### 5. POST /api/posts/:id/unlike/:userId - Unliker un post

**URL:** `http://localhost:3000/api/posts/5f8b7c6d5e4f3a2b1c9d8e7f/unlike/5f9c8d7e6f5a4b3c2d1e0f9a`

**Tests à effectuer:**
- [ ] Test de unlike valide (200 OK)
- [ ] Test avec utilisateur n'ayant pas liked (200 OK)
- [ ] Test avec ID post inexistant (404 Not Found)
- [ ] Vérifier la décrémentation du compteur

### 6. POST /api/posts/:id/comment - Commenter

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "auteur": "5f9c8d7e6f5a4b3c2d1e0f9a",
  "nom": "John Doe",
  "avatar": "https://via.placeholder.com/150",
  "texte": "Super post !"
}
```

**Tests à effectuer:**
- [ ] Test avec données valides (200 OK)
- [ ] Test sans auteur (400 Bad Request)
- [ ] Test sans texte (400 Bad Request)
- [ ] Test avec ID post inexistant (400 Bad Request)
- [ ] Vérifier l'ajout du commentaire

### 7. PUT /api/posts/:id - Modifier un post

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "contenu": "Contenu modifié du post"
}
```

**Tests à effectuer:**
- [ ] Test avec données valides (200 OK)
- [ ] Test avec ID inexistant (404 Not Found)
- [ ] Test avec contenu vide (400 Bad Request)
- [ ] Test avec contenu trop long (400 Bad Request)
- [ ] Vérifier la mise à jour de updatedAt

### 8. DELETE /api/posts/:id - Supprimer un post

**URL:** `http://localhost:3000/api/posts/5f8b7c6d5e4f3a2b1c9d8e7f`

**Tests à effectuer:**
- [ ] Test avec ID valide (200 OK)
- [ ] Test avec ID inexistant (404 Not Found)
- [ ] Vérifier la décrémentation du compteur posts utilisateur

## Collection Postman

### Variables à définir dans Postman
```
baseUrl: http://localhost:3000/api
postId: (à récupérer après création)
userId: (ID utilisateur valide)
```

### Tests automatisés Postman

#### Test 1 - Vérifier la création d'un post
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Post créé avec succès", function () {
    const responseJson = pm.response.json();
    pm.expect(responseJson.success).to.be.true;
    pm.expect(responseJson.data).to.have.property('_id');
    pm.expect(responseJson.data).to.have.property('contenu');
});
```

#### Test 2 - Vérifier la récupération des posts
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Liste de posts récupérée", function () {
    const responseJson = pm.response.json();
    pm.expect(responseJson.success).to.be.true;
    pm.expect(responseJson).to.have.property('data');
    pm.expect(responseJson.data).to.be.an('array');
});
```

#### Test 3 - Vérifier le like
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Post liké", function () {
    const responseJson = pm.response.json();
    pm.expect(responseJson.success).to.be.true;
});
```

## Données de test

### Utilisateurs de test à créer
```javascript
// Utilisateur 1
{
  "nom": "Alice Test",
  "email": "alice.test@example.com",
  "motDePasse": "password123",
  "bio": "Je teste l'API"
}

// Utilisateur 2
{
  "nom": "Bob Test", 
  "email": "bob.test@example.com",
  "motDePasse": "password123",
  "bio": "Tests intensifs"
}
```

### Posts de test à créer
```javascript
// Post 1
{
  "contenu": "Premier post de test avec images",
  "auteur": "userId1",
  "images": ["https://picsum.photos/400/300"]
}

// Post 2
{
  "contenu": "Deuxième post avec mention @alice",
  "auteur": "userId2"
}
```

## Ordre d'exécution des tests

1. **Créer des utilisateurs de test**
2. **Créer des posts de test**
3. **Tester GET /api/posts**
4. **Tester GET /api/posts/user/:userId**
5. **Tester POST /api/posts/:id/like/:userId**
6. **Tester POST /api/posts/:id/unlike/:userId**
7. **Tester POST /api/posts/:id/comment**
8. **Tester PUT /api/posts/:id**
9. **Tester DELETE /api/posts/:id**

## Critères de validation

### Structure de réponse attendue
```javascript
{
  "success": true|false,
  "message": "Message descriptif",
  "data": {...}, // optionnel
  "count": 0, // pour les listes
  "erreur": "Message d'erreur" // en cas d'erreur
}
```

### Codes de statut attendus
- 200 OK : Opération réussie
- 201 Created : Ressource créée
- 400 Bad Request : Données invalides
- 404 Not Found : Ressource non trouvée
- 500 Internal Server Error : Erreur serveur

## Notes importantes

1. Les IDs d'objets MongoDB doivent être valides (ObjectId)
2. Le champ `auteur` dans les posts doit référencer un utilisateur existant
3. Les likes sont stockés comme tableau d'ObjectIds
4. Les commentaires incluent les infos de l'auteur au moment du post
5. Le compteur `nombreLikes` doit être maintenu automatiquement
