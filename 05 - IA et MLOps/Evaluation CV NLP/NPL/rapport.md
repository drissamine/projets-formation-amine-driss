# RAPPORT - Cartographie d'un Domaine IA
## Modèles de Langue (LLM) - M2 ESIS

---

## Résumé

Ce rapport présente une cartographie complète du domaine des **Grands Modèles de Langue (LLM)** couvrant la période 2017-2024. Nous analysons les innovations majeures, les benchmarks, les tendances actuelles et les défis futurs.

**Mots-clés**: LLM, NLP, Transformer, BERT, GPT, RLHF, Multimodalité

---

## 0. Méthodologie

### Approche suivie (selon les conseils méthodologiques du PDF)

| Étape | Action | Outils utilisés |
|-------|--------|----------------|
| 1 | Identification des modèles clés et benchmarks | Papers With Code |
| 2 | Recherche des articles originaux | Semantic Scholar, Google Scholar |
| 3 | Construction de la frise (2 passes) | D'abord modèles, puis mécanismes |
| 4 | Création des figures | Matplotlib, Python (figures.py) |
| 5 | Rédaction du poster/layout | Structure visuelle en 5 secondes |

### Ressources utilisées

- **Papers With Code**: Benchmarks, leaderboards, articles avec code
- **arXiv**: Articles originaux (9 PDFs collectés)
- **HuggingFace**: Documentation et modèles
- **Matplotlib/seaborn**: Courbes d'évolution des benchmarks
- **Python**: Génération des figures (300 dpi)

---

## 1. Introduction

### 1.1 Contexte

Les modèles de langue ont connu une révolution depuis 2017 avec l'introduction du Transformer. Cette cartographie vise à documenter l'évolution du domaine, identifier les ruptures technologiques et analyser les tendances futures.

### 1.2 Objectifs

- Documenter l'évolution chronologique des modèles
- Identifier les 5 ruptures technologiques majeures
- Analyser les benchmarks d'évaluation
- Explorer les tendances 2024-2026
- Identifier les questions ouvertes

---

## 2. Frise Chronologique

### 2.1 Vue d'ensemble

| Année | Modèle | Paramètres | Innovation |
|-------|--------|------------|------------|
| 2017 | Transformer | 65-213M | Self-Attention |
| 2018 | BERT | 110-340M | MLM bidirectionnel |
| 2018 | GPT | 117M | Pré-entraînement génératif |
| 2019 | GPT-2 | 1.5B | Zero-shot |
| 2019 | T5 | 770M-11B | Text-to-Text |
| 2020 | GPT-3 | 175B | Few-shot emergence |
| 2022 | InstructGPT | 1.3-175B | RLHF |
| 2023 | LLaMA | 7-65B | Open-source efficient |
| 2023 | LLaMA 2 | 7-70B | Commercial open-source |
| 2023 | GPT-4 | ~1.7T | Multimodalité |

### 2.2 Analyse

L'évolution des paramètres montre une croissance exponentielle:
- 2017: ~100M paramètres
- 2020: ~175B paramètres
- 2024: ~1.7T paramètres (GPT-4 estimé)

---

## 3. Les 5 Ruptures Technologiques

### 3.1 Rupture 1: Transformer (2017)

**Innovation**: Self-Attention comme seul mécanisme

**Impact**:
- Parallélisation O(1) vs O(n) pour RNN
- WMT EN-DE: 28.4 BLEU (SOTA)
- Entraînement 12x plus rapide

**Formule clé**:
```
Attention(Q,K,V) = softmax(QK^T / √d_k)V
```

**Explication intuitive:** Imaginez une recherche sur Amazon - Q est votre requête, K sont les titres de produits, V est le contenu. L'attention calcule la pertinence entre votre recherche et chaque produit, puis récupère l'information pertinente. Le facteur √d_k empêche les scores de devenir trop grands.

### 3.2 Rupture 2: BERT (2018)

**Innovation**: Masked Language Modeling bidirectionnel

**Impact**:
- 11 tâches刷新 SOTA simultanément
- Transfer learning démocratisé

### 3.3 Rupture 3: GPT-3 (2020)

**Innovation**: Few-shot learning à l'échelle

**Impact**:
- Émergence de capacités non entraînées
- API accessible

### 3.4 Rupture 4: InstructGPT (2022)

**Innovation**: RLHF pour l'alignement

**Impact**:
- 70% préférences humaines
- ChatGPT: 100M utilisateurs

### 3.5 Rupture 5: LLaMA (2023)

**Innovation**: Open-source efficient

**Impact**:
- Démocratisation via fine-tuning
- Écosystème open-source florissant

---

## 3.6 Architectures des Transformers

Il existe trois architectures principales de Transformers, chacune adaptée à des tâches spécifiques:

### 3.6.1 Encoder-Only (BERT, RoBERTa, ALBERT)

```
[CLS] token → Encoder Stack → Sortie
```

**Description**: L'encodeur traite bidirectionnellement - il voit le contexte complet (gauche et droite) pour chaque mot.

**Cas d'utilisation**:
- Classification de texte (sentiment analysis)
- Extraction d'entités nommées (NER)
- Question Answering
- Détection de spam

**Exemples concrets**:
| Modèle | Paramètres | Année | Usage principal |
|--------|------------|-------|----------------|
| BERT-base | 110M | 2018 | GLUE, SQuAD |
| BERT-large | 340M | 2018 | NER fin |
| RoBERTa | 355M | 2019 | Classification fine |
| ALBERT | 12M | 2019 | Deployment léger |

**Schéma d'architecture**:
```
Entrée → Embedding → [Bloc Encoder × N] → Pooler → Sortie
                           ↓
                    Self-Attention
                    Feed-Forward
                    LayerNorm + Residuel
```

### 3.6.2 Decoder-Only (GPT, GPT-2, GPT-3, GPT-4)

```
Mot_i → Decoder Stack → Mot_{i+1}
```

**Description**: Le décodeur traite unidirectionnellement - il ne voit que le contexte gauche (précédent). C'est un modèle génératif.

**Cas d'utilisation**:
- Génération de texte créatif
- Résumé abstractif
- Traduction
- Programmation (code generation)

**Exemples concrets**:
| Modèle | Paramètres | Année | Usage principal |
|--------|------------|-------|----------------|
| GPT | 117M | 2018 | Fine-tuning |
| GPT-2 | 1.5B | 2019 | Zero-shot |
| GPT-3 | 175B | 2020 | Few-shot |
| GPT-4 | ~1.7T | 2023 | Multimodal |

**Schéma d'architecture**:
```
Entrée → Embedding → [Bloc Decoder × N] → Sortie
                           ↓
                    Masked Self-Attention
                    Feed-Forward
                    LayerNorm + Residuel
```

### 3.6.3 Encoder-Decoder (T5, BART, mBART)

```
Entrée (source) → Encoder → Decoder → Sortie (target)
```

**Description**: L'encodeur traite la source, le décodeur génère la cible. Chaque composant peut voir son contexte respectif.

**Cas d'utilisation**:
- Traduction automatique
- Résumé extractif/abstractif
- Question Answering génératif
- Dialogue

**Exemples concrets**:
| Modèle | Paramètres | Année | Usage principal |
|--------|------------|-------|----------------|
| T5-base | 220M | 2019 | Text-to-text |
| T5-large | 770M | 2019 | Traduction |
| BART | 140M | 2019 | Denoising |
| mBART | 600M | 2020 | Multilingue |

**Schéma d'architecture**:
```
Source → Embedding → [Bloc Encoder × N] → Représentation
                           ↓
Cible → Embedding → [Bloc Decoder × N] → Sortie
                           ↓
                    Cross-Attention (Encoder→Decoder)
                    Masked Self-Attention
                    Feed-Forward
```

### 3.6.4 Comparatif des Architectures

| Architecture | Contexte | Direction | Usage principal |
|--------------|----------|-----------|------------------|
| Encoder | Bidirectionnel | Gauche+Droite | Compréhension |
| Decoder | Unidirectionnel | Gauche seule | Génération |
| Encoder-Decoder | Séparé | Bidirectionnel+Unidirectionnel | Transformation |

**Quand utiliser quelle architecture ?**
- **Classification/NER** → Encoder-only (BERT)
- **Génération texte** → Decoder-only (GPT)
- **Traduction/Résumé** → Encoder-Decoder (T5)

---

## 4. Benchmarks d'Évaluation

### 4.1 Benchmarks principaux

| Benchmark | Domaine | Métrique | GPT-4 |
|-----------|---------|----------|-------|
| GLUE | Compréhension | Moyenne | 100+ |
| MMLU | Multitâche | Accuracy | 86.4% |
| HumanEval | Code | Pass@1 | 67% |
| BIG-Bench | Raisonnement | Average | 83.1% |
| GSM8K | Math | Accuracy | 92% |

### 4.2 Évolution des performances

Les benchmarks montrent une amélioration continue:
- MMLU: 44% (2020) → 86.4% (2024)
- HumanEval: 0% (2020) → 67% (2024)

---

## 5. Tendances 2024-2026

### 5.1 Modèles fondationaux

- Multimodalité native (texte + image + audio)
- Contexte long (1M+ tokens)
- Agents autonomes

### 5.2 Optimisation

- Quantization (INT4, INT8)
- Fine-tuning efficient (LoRA, QLoRA)
- Distillation

### 5.3 Sécurité

- RLHF et DPO
- Constitutional AI
- Régulation (EU AI Act)

---

## 6. Questions Ouvertes

### 6.1 Défis techniques

- **Coût énergétique**: 552 tonnes CO2 pour GPT-3
- **Hallucinations**: Factualité des réponses
- **Biais**: Reproduction de préjugés

### 6.2 Défis éthiques

- Concentration du pouvoir
- Accès équitable
- Propriété intellectuelle

### 6.3 Défis scientifiques

- Compréhension profonde vs pattern matching
- Reasoning véritable vs imitation
- Émergence: pourquoi certaines capacités apparaissent?

---

## 7. Conclusion

### 5 points clés à retenir

1. **Transformer (2017)**: Architecture fondatrice permettant la parallélisation
2. **BERT (2018)**: Transfer learning démocratisé
3. **GPT-3 (2020)**: Émergence de capacités à grande échelle
4. **InstructGPT (2022)**: Alignement via RLHF
5. **LLaMA (2023)**: Démocratisation open-source

### Perspectives

L'avenir des LLM dépendra de notre capacité à:
- Réduire l'impact environnemental
- Garantir la sécurité et l'éthique
- Assurer un accès équitable à la technologie

---

## Références

1. Vaswani, A., et al. (2017). "Attention Is All You Need". NeurIPS.
2. Devlin, J., et al. (2018). "BERT". NAACL.
3. Brown, T., et al. (2020). "GPT-3". NeurIPS.
4. Ouyang, L., et al. (2022). "InstructGPT". ArXiv.
5. Touvron, H., et al. (2023). "LLaMA". ArXiv.
6. OpenAI. (2023). "GPT-4 Technical Report". ArXiv.

---

## Annexes

### A. Figures originales

- Figure 1: Timeline des modèles LLM
- Figure 2: Évolution des benchmarks
- Figure 3: Architecture du Transformer
- Figure 4: Impact des innovations
- Figure 5: Scaling Laws

### B. Code source

- Script Python pour générer les figures (figures.py)

### C. Articles collectés

- 9 PDFs dans le dossier papers/LLM

---

---

**Format du document:**
- Police: Inter 11pt
- Marges: 2,5 cm
- Nombre de pages: ~10 pages (hors références)

**Sources et citations:**
- Toutes les affirmations sont sourcées via les références bibliographiques
- Les figures sont originales et générées programmatiquement
- Les données de benchmarks proviennent de Papers With Code et articles originaux

**Figures originales:**
- Figure 1: Timeline des modèles LLM (échelle logarithmique) - Données: articles originaux
- Figure 2: Évolution des benchmarks (MMLU, HumanEval, GSM8K) - Source: Papers With Code
- Figure 3: Architecture du Transformer (schéma conceptuel) - Inspirée de Vaswani et al., 2017
- Figure 4: Impact des innovations par modèle - Analyse basée sur les articles
- Figure 5: Scaling Laws - Source: Kaplan et al. (2021), Brown et al. (2020)

**Code source:**
- Script Python pour générer les figures (figures.py)

---

*Rapport soumis dans le cadre du cours de Cartographie d'un Domaine IA*
*M2 ESIS*
*Sous-domaine: N1 - Modèles de langue (LLM)*