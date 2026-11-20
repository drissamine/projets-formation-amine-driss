# Progrès Technologiques Majeurs - Modèles de Langue (LLM)

Ce document identifie les 5 ruptures technologiques majeures dans l'évolution des modèles de langue de 2017 à 2024.

---

## Rupture 1: Transformer (2017) - L'Architecture Self-Attention

### Contexte
Avant 2017, les modèles de séquence utilisent des RNN (LSTM, GRU) qui traitent les tokens séquentiellement.

### Innovation
Remplacer la récurrence par **l'attention mécanismes** uniquement.

### Changement de paradigme
- **Avant**: Traitement séquentiel O(n) - impossible à paralléliser
- **Après**: Traitement parallèle O(1) - entièrement parallélisable
- **Complexité**: O(n²·d) pour attention, contre O(n·d²) pour RNN

### Impact
- Révolution dans la traduction automatique (WMT 2014: 28.4 BLEU)
- Foundation de tous les modèles modernes (BERT, GPT, T5, etc.)
- Formation 12x plus rapide que les modèles RNN

### Formule clé
```
Attention(Q, K, V) = softmax(QK^T / √d_k)V
```

---

## Rupture 2: BERT (2018) - Pré-entraînement Bidirectionnel

### Contexte
GPT (2018) utilise un pré-entraînement unidirectionnel (gauche-à-droite).

### Innovation
**Masked Language Modeling (MLM)** -masquer 15% des tokens et les prédire.

### Changement de paradigme
- **Avant**: Fine-tuning depuis zéro sur chaque tâche
- **Après**: Pré-entraînement général → Fine-tuning spécifique
- **Bidirectionnalité**: Le modèle voit le contexte des deux côtés

### Impact
- 11 tâches NLP刷新 SOTA sur GLUE
- Approche "transfer learning" devient standard
- BERT-base: 110M paramètres, BERT-large: 340M

### Formule clé
```
MLM: 15% tokens masqués → prédire les tokens manquants
Next Sentence Prediction: Prédire si B suit A
```

---

## Rupture 3: GPT-3 (2020) - Émergence à l'Échelle

### Contexte
Les modèles précédents nécessitent un fine-tuning pour chaque tâche.

### Innovation
**Few-shot learning** - Capacité à effectuer des tâches avec seulement quelques exemples dans le prompt.

### Changement de paradigme
- **Avant**: Fine-tuning obligatoire (apprentissage supervisé)
- **Après**: Zéro-shot / Few-shot via le prompt
- **Émergence**: À 175B paramètres, des capacités non entraînées apparaissent

### Scaling Laws
```
Performance ~ Parameters^(-0.075)
Performance ~ Compute^(-0.050)
Performance ~ Data^(-0.095)
```

### Impact
- 175B paramètres - plus grand modèle à l'époque
- 45TB de texte entraîné
- Aucune tâche spécifique pendant l'entraînement

### Métriques
- LAMBADA: 76.2% (PPL) - +15% vs SOTA
- TriviaQA: 64.3% zero-shot
- 70% des tâches improves with more parameters

---

## Rupture 4: InstructGPT (2022) - RLHF pour l'Alignement

### Contexte
GPT-3 peut générer du texte toxique ou non utile.

### Innovation
**Reinforcement Learning from Human Feedback (RLHF)**:
1. Fine-tuning supervisé (SFT)
2. Reward Model (RM) entraîné sur préférences humaines
3. PPO pour optimiser contre le RM

### Changement de paradigme
- **Avant**: Maximiser la probabilité du texte (MLE)
- **Après**: Maximiser l'utilité perçue par les humains
- **Alignement**: Le modèle suit les instructions humaines

### Impact
- 70% préférences humaines vs GPT-3
- 50% moins de toxicité
- ChatGPT: 100M utilisateurs en 2 mois

### Processus RLHF
```
1. SFT: Fine-tuning sur données labelisées (13K prompts)
2. RM: Entraîner un modèle de récompense (500K comparaisons)
3. PPO: Optimiser la politique contre le RM
```

---

## Rupture 5: LLaMA (2023) - Open-Source Efficient

### Contexte
GPT-4 et Claude sont propriétaires (API payante, pas d'accès aux poids).

### Innovation
**Open-source avec efficacité**:
- Meilleure performance avec moins de paramètres
- Entraînés sur plus de tokens
- Architectures optimisées

### Changement de paradigme
- **Avant**: Closed-source (GPT-4, Claude)
- **Après**: Open-source accessible à tous
- **Démocratisation**: Anyone peut fine-tuner

### Innovations techniques
1. **Pre-norm**: Normalisation avant les residual
2. **SwiGLU**: Activation plus efficace que ReLU
3. **Rotary Embeddings**: Position embeddings rotatifs
4. **Attention without masks**: Pour les grands modèles

### Impact
- LLaMA-2 70B rivalise avec GPT-3.5
- Écosystème de fine-tuning (LoRA, QLoRA)
- Mistral, Qwen, Yi: clones open-source

---

## Tableau Récapitulatif

| Rupture | Année | Modèle | Paramètre clé | Impact |
|---------|-------|--------|---------------|--------|
| 1 | 2017 | Transformer | Self-attention | Parallélisation |
| 2 | 2018 | BERT | MLM bidirectionnel | Transfer learning |
| 3 | 2020 | GPT-3 | Few-shot | Émergence |
| 4 | 2022 | InstructGPT | RLHF | Alignement |
| 5 | 2023 | LLaMA | Open-source | Démocratisation |

---

## Questions Ouvertes

1. **Limite d'échelle**: Est-ce que les lois de scaling continuent ?
2. **Raisonnement**: Les LLM peuvent-ils raisonner véritablement ?
3. **Biais**: Comment éliminer les biais systémiques ?
4. **Coût**: Impact environnemental training (estimation: 552 tonnes CO2 pour GPT-3)
5. **Multimodalité**: Comment intégrer efficacement vision/audio ?

---

## Références

1. Vaswani et al. (2017). "Attention Is All You Need". NeurIPS.
2. Devlin et al. (2018). "BERT". NAACL.
3. Brown et al. (2020). "GPT-3". NeurIPS.
4. Ouyang et al. (2022). "InstructGPT". arXiv:2203.02155.
5. Touvron et al. (2023). "LLaMA". arXiv:2302.13971.