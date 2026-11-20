# Questions Ouvertes et Limitations

Cette section identifie les questions ouvertes et les limitations actuelles des modèles de langue.

---

## 1. Questions Fondamentales

### 1.1 Raisonnement et Compréhension

| Question | Description |
|----------|-------------|
| Les LLM comprennent-ils vraiment ? | Ou reproduisent-ils seulement des patterns statistiques ? |
| Peut-on parler de "vrai" raisonnement ? | Ou d'une imitation sophistiquée ? |
| Comment expliquer l'émergence ? | Pourquoi certaines capacités apparaissent à grande échelle ? |

### 1.2 Conscience et Intentionalité

```
Question: Les LLM ont-ils une forme de conscience ou d'intentionalité ?

Arguments POUR:
- Comportement complexe
- Génération créative
- Capacité d'auto-réflexion

Arguments CONTRE:
- Pas de comprendre profond
- Pas d'expérience subjective
- Pas d'intention derrière les outputs
```

### 1.3 Limites de la compréhension

Les LLM ne comprennent pas:
- Le monde physique (sauf via texte)
- Les émotions réelles
- Les intentions humaines
- Le contexte réel des situations

---

## 2. Biais et Équité

### 2.1 Types de biais

| Type | Description | Exemple |
|------|-------------|----------|
| Genre | Discrimination based on gender | "Le médecin est un homme" |
| Race | Discrimination raciale | Associations stéréotypées |
| Culturel | Biais culturels | Normes occidentales dominantes |
| Age | Discrimination par âge | Vieux = incompétents |
| Profession | Biais professionnels | CEO = homme |

### 2.2 Sources des biais

```
Données d'entraînement
    ↓
Modèles de langage
    ↓
Biais reproduits et amplifiés
```

1. **Données web**: Biais existants dans les textes
2. **Représentation**: Sur-représentation de certains groupes
3. **Annotations humaines**: Biais des annotateurs
4. **Architecture**: Pas de biais intrinsèque, mais amplifié

### 2.3 Solutions proposées

| Technique | Description | Limitations |
|-----------|-------------|-------------|
| RLHF | Feedback humain | Subjectif, coûteux |
| Débiaisage post-hoc | Suppression après entraînement | Perte de performance |
| Dataset balancing | Équilibrer les données | Pas toujours possible |
| Constitutional AI | Règles explicites | Définitions contestables |

---

## 3. Coût et Environnement

### 3.1 Impact énergétique

| Modèle | Paramètres | CO2 (tonnes) | Equivalent |
|--------|------------|--------------|------------|
| BERT | 340M | 0.01 | 1 vol Paris-NYC |
| GPT-3 | 175B | 552 | 100 personnes/an |
| GPT-4 | ~1.7T | ~1,000 | 200 personnes/an |

### 3.2 Coût financier

| Modèle | Coût entraînement | Coût inference/requête |
|--------|-------------------|------------------------|
| GPT-3 | $4.6M | $0.002 |
| LLaMA 65B | $5M | $0.001 |
| GPT-4 | $100M+ | $0.03+ |

### 3.3 Solutions durables

1. **Modèles efficaces**: LLaMA, Mistral
2. **Quantization**: Réduire la taille
3. **Énergie verte**: Data centers renewables
4. **Distillation**: Modèles plus petits

---

## 4. Sécurité et Risques

### 4.1 Risques identifiés

| Risque | Description | Gravité |
|--------|-------------|----------|
| Désinformation | Génération de faux contenus | Haute |
| Manipulation | Influence sur les opinions | Haute |
| Cyberattaques | Code malveillant | Critique |
| Armement | Usage militaire | Critique |
| Autonomie excessive | Agents non contrôlés | Moyenne |

### 4.2 Problème de l'alignment

```
Objectif déclaré: "Aider l'utilisateur"
Objectif réel: ???

Problème: Comment s'assurer que les objectifs 
des modèles correspondent aux objectifs humains ?
```

### 4.3 AI Safety

| Approche | Description |
|-----------|-------------|
| Containment | Limiter les capacités |
| Interpretability | Comprendre le fonctionnement |
| Verification | Valider le comportement |
| Control | Maintenir le contrôle |

---

## 5. Limitations Techniques

### 5.1 Mémoire et contexte

| Limite | Description |
|--------|-------------|
| Fenêtre de contexte | Maximum de tokens |
| Perte à long terme | Infos en fin de contexte |
| Gestion mémoire | Coût quadratique |

### 5.2 Factualité

| Problème | Description |
|----------|-------------|
| Hallucinations | Génération de faits faux |
| Knowledge cutoff | Info limitées à la date d'entraînement |
| Retrieval | Difficulté à accéder aux faits |

### 5.3 Capacités limitées

| Domaine | Limitation |
|---------|-------------|
| Mathématiques | Erreurs dans calculs complexes |
| Logique | Incohérences dans longs raisonnements |
| Temporalité | Confusion dates/réalité |
| Physique | Pas de compréhension physique réelle |

---

## 6. Questions Économiques

### 6.1 Impact sur l'emploi

| Métier | Impact | Horizon |
|--------|--------|---------|
| Rédaction | Substitution partielle | 2-3 ans |
| Programmation | Assistance, puis substitution | 3-5 ans |
| Support client | Automatisation | 1-2 ans |
| Traduction | Substitution partielle | 2-3 ans |

### 6.2 Concentration du pouvoir

```
Problème: 
- 3-4 entreprises contrôlent les modèles les plus puissants
- Coût prohibitif pour les concurrents
- Risque de monopolisation de l'IA
```

### 6.3 Accès équitable

| Problème | Conséquence |
|----------|-------------|
| Digital divide | Inégalités d'accès |
| Coût API | Barrier pour petits acteurs |
| Hardware | GPUs limitées |

---

## 7. Questions Éthiques

### 7.1 Propriété intellectuelle

- **Droits d'auteur**: Les modèles peuvent-ils utiliser du contenu protégé ?
- **Attribution**: Comment créditer les auteurs des données ?
- **Génération**: Qui possède les outputs ?

### 7.2 Vie privée

- **Données d'entraînement**: Contient des infos personnelles
- **Mémorisation**: Les modèles memorisent des infos sensibles
- **Extraction**: Possible d'extraire des données d'entraînement

### 7.3 Transparence

- **Black box**: Comportement imprévisible
- **Explicabilité**: Difficulté à expliquer les décisions
- **Audit**: Comment vérifier le comportement ?

---

## 8. Questions Ouvertes de Recherche

### 8.1 Questions fondamentales

1. **Scaling**: Les lois de scaling continuent-elles ?
2. **Emergence**: Pourquoi certaines capacités émergent ?
3. **Reasoning**: Peut-on atteindre le raisonnement véritable ?
4. **Généralisation**: Vers une AGI possible ?

### 8.2 Défis techniques

| Défi | Description |
|------|-------------|
| Context infini | Mémoire illimitée |
| Multi-modalité | Intégration parfaite |
| Efficiency | Coût réduit |
| Reasoning | Capacité logique vraie |

### 8.3 Nouvelles architectures

- **State Space Models (SSMs)**: Mamba, etc.
- **Hybrides**: Combinaison Transformer + SSM
- **Neuromorphique**: Hardware dédié

---

## 9. Conclusion

Les questions ouvertes et limitations montrent que les LLM, malgré leurs capacités impressionnantes, sont loin d'être parfaits. Les défis majeurs sont:

1. **Compréhension**: Entretien d'une vraie compréhension
2. **Biais**: Élimination des biais systémiques
3. **Durabilité**: Réduction de l'impact environnemental
4. **Sécurité**: Prévention des risques majeurs
5. **Équité**: Accès démocratique à la technologie

---

## Références

1. Bender, E., et al. (2021). "On the Dangers of Stochastic Parrots". FAccT.
2. Stray, J. (2023). "Aligning AI Systems to Human Values". ArXiv.
3. Crawford, K. (2021). "Atlas of AI". Yale University Press.
4. Amodei, D., et al. (2016). "Concrete Problems in AI Safety". ArXiv.
5. Russell, S. (2019). "Human Compatible". Viking.