# Introduction et Contexte

## 1. Contexte Général

### 1.1 Qu'est-ce que le NLP ?

Le **Traitement du Langage Naturel** (NLP, Natural Language Processing) est un domaine de l'intelligence artificielle qui se concentre sur l'interaction entre les ordinateurs et le langage humain. L'objectif du NLP est de permettre aux machines de comprendre, interpréter et générer le langage naturel de manière utile.

### 1.2 Évolution historique

L'histoire des modèles de langage peut être divisée en plusieurs périodes:

- **Années 1990**: Modèles statistiques (n-grammes, HMM, CRF)
- **Années 2010**: Premiers réseaux de neurones (LSTM, GRU)
- **2017-2024**: Révolution des Transformers et des grands modèles de langue

### 1.3 Pourquoi les LLM sont-ils importants ?

Les **Grands Modèles de Langue** (LLM, Large Language Models) ont transformé le domaine du NLP:

| Aspect | Avant LLM | Après LLM |
|--------|-----------|-----------|
| Entraînement | Supervisé par tâche | Pré-entraînement non supervisé |
| Généralisation | Tâche-spécifique | Multi-tâches |
| Données nécessaires | Grand jeu de tâches | Few-shot / Zero-shot |
| Performance | Limité | SOTA sur la plupart des tâches |

---

## 2. Définitions Clés

### 2.1 Modèle de Langue

Un **modèle de langue** est une distribution de probabilité sur des séquences de tokens:

```
P(w_1, w_2, ..., w_n) = ∏ P(w_i | w_1, ..., w_{i-1})
```

### 2.2 Architecture Transformer

L'architecture **Transformer** (Vaswani et al., 2017) est la base de tous les LLM modernes. Elle utilise:

- **Self-Attention**: Permet de capturer les dépendances à longue distance
- **Parallélisation**: Entraînement efficace sur GPU
- **Encodeur-Décodeur**: Flexibilité pour différentes tâches

### 2.3 Pré-entraînement vs Fine-tuning

| Phase | Description | Objectif |
|-------|-------------|-----------|
| **Pré-entraînement** | Entraînement sur un grand corpus non labelisé | Apprendre des représentations générales |
| **Fine-tuning** | Entraînement supplémentaire sur données spécifiques | Adapter à une tâche particulière |

---

## 3. Taxonomie des LLM

### 3.1 Par architecture

```
Modèles de Langue
├── Encoder-only (BERT)
│   ├── RoBERTa
│   ├── DeBERTa
│   └── ELECTRA
├── Decoder-only (GPT)
│   ├── GPT-2
│   ├── GPT-3
│   ├── GPT-4
│   └── LLaMA
└── Encoder-Decoder (T5)
    ├── BART
    └── FLAN-T5
```

### 3.2 Par taille

| Catégorie | Paramètres | Exemples |
|-----------|------------|----------|
| Petit | < 1B | BERT-base, GPT-2 small |
| Moyen | 1-10B | RoBERTa-large, LLaMA-7B |
| Grand | 10-100B | GPT-3, LLaMA-70B |
| Très grand | > 100B | GPT-4 (≈1.7T), PaLM (540B) |

### 3.3 Par modalité

- **Unimodaux**: Texte uniquement (GPT-3, LLaMA)
- **Multimodaux**: Texte + Image (GPT-4, Claude 3)

---

## 4. Applications des LLM

### 4.1 Applications grand public

1. **Chatbots et assistants virtuels**
   - ChatGPT, Claude, Gemini
   
2. **Génération de contenu**
   - Rédaction d'articles, code, poésie
   
3. **Recherche d'information**
   - Moteurs de recherche augmentés

### 4.2 Applications professionnelles

| Domaine | Application |
|---------|-------------|
| Santé | Analyse de dossiers médicaux, diagnostic assisté |
| Juridique | Recherche de précédents, résumé de contrats |
| Finance | Analyse de sentiments, rapports automatisés |
| Éducation | Tutoring personnalisé, correction d'essais |

---

## 5. Enjeux et Défis

### 5.1 Enjeux sociétaux

- **Désinformation**: Capacité à générer du faux contenu
- **Biais**: Reproduction de préjugés présents dans les données
- **Emploi**: Automatisation de tâches cognitives
- **Éducation**: Impact sur l'apprentissage

### 5.2 Défis techniques

- **Coût**: Entraînement prohibitif (millions de dollars)
- **Énergie**: Impact environnemental significatif
- **Latence**: Inference temps réel difficile pour grands modèles
- **Context**: Limite de mémoire (tokens)

---

## 6. Structure du Document

Ce document est organisé comme suit:

1. **Frise chronologique**: Évolution des modèles de 2017 à 2024
2. **Ruptures technologiques**: Les 5 innovations majeures
3. **Formules clés**: Explications intuitives des algorithmes
4. **Benchmarks**: Métriques d'évaluation
5. **Tendances 2022-2026**: État de l'art actuel
6. **Questions ouvertes**: Défis non résolus
7. **Conclusion**: Synthèse et perspectives

---

## 7. Méthodologie

### 7.1 Sources utilisées

- **Papers With Code**: Benchmarks et排行榜
- **Semantic Scholar / Google Scholar**: Articles originaux
- **ArXiv**: Prépublications récentes
- **OpenAI / Meta AI**: Documentation officielle

### 7.2 Approche de cartographie

La cartographie du domaine a été réalisée en deux passes:

1. **Première passe**: Identification des modèles clés et de leurs dates
2. **Deuxième passe**: Identification des mécanismes sous-jacents

---

## Références

1. Vaswani, A., et al. (2017). "Attention Is All You Need". NeurIPS.
2. Devlin, J., et al. (2018). "BERT: Pre-training of Deep Bidirectional Transformers". NAACL.
3. Brown, T., et al. (2020). "Language Models are Few-Shot Learners". NeurIPS.
4. Ouyang, L., et al. (2022). "Training language models to follow instructions with human feedback". ArXiv.
5. Touvron, H., et al. (2023). "LLaMA: Open and Efficient Foundation Language Models". ArXiv.