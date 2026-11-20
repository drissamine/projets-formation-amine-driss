# Benchmarks de Référence - Modèles de Langue (LLM)

Ce document recense les benchmarks utilisés pour évaluer les modèles de langue.

---

## 1. GLUE (General Language Understanding Evaluation)

### Description
Ensemble de 9 tâches de compréhension du langage naturel.

### Tâches
| Tâche | Description | Métrique |
|-------|-------------|----------|
| CoLA | Acceptabilité grammaticale | Matthews Corr |
| SST-2 | Analyse de sentiment | Accuracy |
| MRPC | Paraphrase detection | F1 |
| STS-B | Similarité sémantique | Pearson/Spearman |
| QQP | Questions duplicates | F1 |
| MNLI | Inférence naturelle | Matched/Mismatched |
| QNLI | QA natural language | Accuracy |
| RTE | Recognizing Textual Entailment | Accuracy |
| WNLI | Winograd NLI | Accuracy |

### Métriques
- **GLUE score**: Moyenne des scores sur toutes les tâches
- **SuperGLUE**: Version plus difficile

### Résultats historiques
| Modèle | Année | GLUE Score |
|--------|-------|------------|
| BERT-base | 2018 | 68.9 |
| BERT-large | 2018 | 72.8 |
| RoBERTa | 2019 | 80.5 |
| ALBERT | 2020 | 89.4 |
| DeBERTa-v3 | 2022 | 91.1 |

---

## 2. MMLU (Massive Multitask Language Understanding)

### Description
57 tâches multitâches couvrant różne domaines:
- Sciences exactes
- Sciences humaines
- Histoire
- Éthique
- Mathématiques

### Format
Questions à choix multiples (4 options)

### Métriques
- **Accuracy %**: Pourcentage de réponses correctes

### Résultats historiques
| Modèle | Année | MMLU Score |
|--------|-------|------------|
| GPT-3 | 2020 | 43.9 |
| Gopher | 2021 | 60.0 |
| Chinchilla | 2022 | 75.0 |
| GPT-4 | 2023 | 86.4 |
| Claude 2 | 2023 | 86.8 |
| GPT-4.5 | 2024 | 87.2 |

---

## 3. HumanEval

### Description
Évaluation de la génération de code Python.
164 problèmes de codage avec tests unitaires.

### Format
- Entrée: Description du problème en language naturel
- Sortie: Code Python solution

### Métriques
- **Pass@1**: Le code passe les tests du premier coup
- **Pass@10**: Au moins un des 10 premiers candidats passe
- **Pass@100**: Au moins un des 100 candidats passe

### Résultats historiques
| Modèle | Année | Pass@1 |
|--------|-------|--------|
| GPT-3 | 2020 | 0.0 |
| CodeGen | 2022 | 30.3 |
| Codex | 2022 | 47.0 |
| GPT-4 | 2023 | 67.0 |
| Claude 3 | 2024 | 73.0 |

---

## 4. BIG-Bench (Beyond the Imitation Game)

### Description
Plus de 200 tâches difficiles 测试ant:
- Raisonnement
- Mathématiques
- Programmation
- Compréhension

### Format
- **Many-shot**: Instructions dans le prompt
- **JSON**: Format structuré

### Métriques
- **Average**: Score moyen sur toutes les tâches
- **ROUGE**: Pour les tâches de génération

### Résultats historiques
| Modèle | Année | BIG-Bench Average |
|--------|-------|-------------------|
| GPT-3 | 2020 | 31.7 |
| Gopher | 2021 | 47.9 |
| PaLM 540B | 2022 | 73.3 |
| GPT-4 | 2023 | 83.1 |
| GPT-4 Turbo | 2024 | 85.4 |

---

## 5. HellaSwag

### Description
Test de bon sens physique et social.

### Format
Complétion de scénarios:
- 4 options de fin
- 1 correcte, 3 distracteurs (adversarial)

### Métriques
- **Accuracy %**

### Résultats historiques
| Modèle | Année | HellaSwag |
|--------|-------|-----------|
| BERT | 2018 | 41.0 |
| GPT-2 | 2019 | 50.0 |
| GPT-3 | 2020 | 78.9 |
| LLaMA 2 70B | 2023 | 85.0 |
| GPT-4 | 2023 | 87.5 |

---

## 6. ARC (Abstraction and Reasoning Corpus)

### Description
Problèmes de raisonnement abstrait (type IQ test).

### Format
- Grilles à transformer
- Plusieurs exemples d'entraînement
- Test final à prédire

### Métriques
- **Accuracy %**

### Résultats historiques
| Modèle | Année | ARC |
|--------|-------|-----|
| GPT-3 | 2020 | 21.0 |
| PaLM 540B | 2022 | 42.0 |
| GPT-4 | 2023 | 53.0 |
| GPT-4.5 | 2024 | 58.0 |

---

## 7. GSM8K (Grade School Math 8K)

### Description
Problèmes de mathématiques niveau école primaire.

### Format
- Problème en texte
- Réponse: suite de calculs + réponse numérique

### Métriques
- **Accuracy %**

### Résultats historiques
| Modèle | Année | GSM8K |
|--------|-------|-------|
| GPT-3 | 2020 | 34.0 |
| GPT-3.5 | 2022 | 52.0 |
| GPT-4 | 2023 | 92.0 |
| Minerva | 2023 | 94.0 |
| GPT-4 Turbo | 2024 | 95.0 |

---

## 8. LAMBADA

### Description
Prédiction du dernier mot d'une phrase (夹击 long-range dependencies).

### Format
- Phrases de 4-8 mots
- Prédire le dernier mot

### Métriques
- **Accuracy** (perplexity aussi utilisée)

### Résultats historiques
| Modèle | Année | LAMBADA |
|--------|-------|---------|
| LSTM | 2016 | 7.0 (PPL) |
| GPT-2 | 2019 | 8.6 (PPL) |
| GPT-3 | 2020 | 76.2 (accuracy) |
| GPT-4 | 2023 | 86.4 |

---

## 9. TriviaQA

### Description
Réponses à des questions factuelles (avec contexte).

### Format
- Question + Document contexte
- Réponse libre

### Métriques
- **Exact Match**
- **F1**

### Résultats historiques
| Modèle | Année | EM |
|--------|-------|---|
| DrQA | 2017 | 27.0 |
| T5 | 2019 | 48.0 |
| GPT-3 (zero) | 2020 | 64.3 |
| GPT-3 (few) | 2020 | 71.2 |

---

## 10. MBPP (Mostly Basic Python Problems)

### Description
494 problèmes de programmation Python de base.

### Format
- Description en langage naturel
- Solution code

### Métriques
- **Pass@10**

### Résultats historiques
| Modèle | Année | Pass@10 |
|--------|-------|----------|
| CodeGen | 2022 | 41.0 |
| Codex | 2022 | 62.0 |
| LLaMA 2 70B | 2023 | 56.0 |
| GPT-4 | 2023 | 84.0 |

---

## Tableau Récapitulatif

| Benchmark | Type | Métrique principale | # Tâches |
|-----------|------|---------------------|----------|
| GLUE | Compréhension | Accuracy/F1 | 9 |
| MMLU | Multitâche | Accuracy | 57 |
| HumanEval | Code | Pass@1 | 164 |
| BIG-Bench | Raisonnement | Average | 200+ |
| HellaSwag | Bon sens | Accuracy | 10K |
| ARC | Raisonnement abstrait | Accuracy | 800 |
| GSM8K | Mathématiques | Accuracy | 8.5K |
| LAMBADA | Dependencies | Accuracy/PPL | 10K |
| TriviaQA | QA | Exact Match | 95K |
| MBPP | Code | Pass@10 | 494 |

---

## Tendances 2024-2025

### Nouveaux Benchmarks
1. **MMLU-Pro**: Version plus difficile de MMLU
2. **GPQA**: Questions de recherche doctorale
3. **MathVista**: Mathématiques visuelles
4. **MMMU**: Multimodal understanding
5. **IFEval**: Instruction following

### Métriques émergentes
- **Aide humaine (HIE)**: Qualité de l'aide fournie
- **Alignment**: Fidélité aux instructions
- **Truthfulness**: Véracité des réponses

---

## Références

1. GLUE: https://gluebenchmark.com/
2. MMLU: https://github.com/hendrycks/test
3. HumanEval: https://github.com/openai/human-eval
4. BIG-Bench: https://github.com/google/BIG-Bench
5. HellaSwag: https://rowanzellers.com/hellaswag/
6. ARC: https://github.com/fchollet/ARC
7. GSM8K: https://github.com/openai/grade-school-math
8. LAMBADA: https://arxiv.org/abs/1606.06031