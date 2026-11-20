# Frise Chronologique - Modèles de Langue (LLM)

##Vue d'Ensemble
Ce document présente la frise chronologique des modèles de langue (LLM) de 2017 à 2024, construite en deux passes:
- **Première passe**: Identification des modèles/architectures clés
- **Deuxième passe**: Identification des mécanismes sous-jacents

---

## 2017 - Transformer

### Modèle: Transformer
- **Publication**: "Attention Is All You Need" (Vaswani et al.)
- **Date**: 12 Juin 2017 (initial), NeurIPS 2017
- **Conférence**: NeurIPS 2017 (Long Beach, CA, USA)
- **arXiv**: 1706.03762
- **Auteurs**: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin

### Contribution principale
Architecture entièrement basée sur l'attention机制 (self-attention), sans récurrence ni convolution.

### Résultats clés
- WMT 2014 English-to-German: **28.4 BLEU** (nouveau SOTA)
- WMT 2014 English-to-French: **41.8 BLEU** (nouveau SOTA)
- Entraînement: 3.5 jours sur 8 GPUs P100

### Mécanismes clés identifiés
1. **Scaled Dot-Product Attention**: Attention(Q,K,V) = softmax(QK^T / √d_k)V
2. **Multi-Head Attention**: h=8 heads parallèle, d_k = d_v = 64
3. **Positional Encoding**: Sinusoidal (sin/cos functions)
4. **Encoder-Decoder**: 6 couches chacun
5. **Residual Connections + Layer Normalization**

### Architecture
- d_model = 512 (base), 1024 (big)
- d_ff = 2048 (base), 4096 (big)
- Paramètres: 65M (base), 213M (big)

---

## 2018 - BERT & GPT

### Modèle 1: BERT
- **Publication**: "BERT: Pre-training of Deep Bidirectional Transformers"
- **Date**: 11 Octubre 2018
- **arXiv**: 1810.04805
- **Conférence**: NAACL-HLT 2019 (Minneapolis)
- **Auteurs**: Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova (Google AI Language)

### Contribution principale
Pré-entraînement par **Masked Language Modeling (MLM)** + **Next Sentence Prediction**
- Bidirectionnel (contrairement à GPT qui est unidirectionnel)
- Fine-tuning sur tâches en aval

### Résultats clés
- GLUE: 78.3% (SOTA)
- SQuAD v1.1: 93.2% (F1)
- SQuAD v2.0: 83.1% (F1)

### Mécanismes clés
1. **MLM (Masked LM)**: 15% des tokens masqués
2. **Next Sentence Prediction**: Prédit si B suit A
3. **Segment embeddings**: Pour les paires de phrases

---

### Modèle 2: GPT
- **Publication**: "Improving Language Understanding by Generative Pre-Training"
- **Date**: Juin 2018
- **Auteurs**: Alec Radford, Karthik Narasimhan, Tim Salimans, Ilya Sutskever (OpenAI)

### Contribution principale
Pré-entraînement non supervisé sur un grand corpus + fine-tuning supervisé
- **Unidirectionnel** (gauche-à-droite)
- Approach: "Generative Pre-Training"

### Architecture
- 12 couches decoder
- d_model = 768
- 117M paramètres

---

##2019 - GPT-2

### Modèle: GPT-2
- **Publication**: "Language Models are Unsupervised Multitask Learners"
- **Date**: Février 2019 (réinitial release), Mai 2019 (full)
- **arXiv**: 1908.09203
- **Auteurs**: Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, Ilya Sutskever (OpenAI)

### Contribution principale
**Zéro-shot learning** - Capacité à effectuer des tâches sans fine-tuning
- Modèle plus grand: 1.5B paramètres
- WebText: 40GB de webpages filtrées

### Architecture
- 48 couches
- d_model = 1024
- 1.5B paramètres
- Context: 1024 tokens

### Mécanismes clés
1. **Zero-shot prompting**: Instructions en language naturel
2. **Task conditioning**: Le modèle s'adapte à la tâche via le prompt
3. **Layer normalization** modifiée

---

##2019 - T5

### Modèle: T5 (Text-to-Text Transfer Transformer)
- **Publication**: "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer"
- **Date**: Octobre 2019
- **arXiv**: 1910.10683
- **Auteurs**: Colin Raffel, Noam Shazeer, Adam Roberts et al. (Google Research)

### Contribution principale
**Unified Framework** - Toutes les tâches NLP formulées comme "text-to-text"
- Traduction, résumé, QA, classification: même format d'entrée/sortie

### Architecture
- Encoder-Decoder Transformer
- Variantes: small (60M), base (220M), large (770M), 3B, 11B

### Résultats clés
- GLUE: 89.7 (SOTA à l'époque)
- SuperGLUE: 88.0 (SOTA à l'époque)
- CNN/DailyMail摘要: 19.5 ROUGE

---

##2020 - GPT-3

### Modèle: GPT-3
- **Publication**: "Language Models are Few-Shot Learners"
- **Date**: Mai 2020
- **arXiv**: 2005.14165
- **Auteurs**: Tom B. Brown, Benjamin Mann, Nick Ryder et al. (OpenAI)

### Contribution principale
**Few-shot learning** - Emergence de capacités à l'échelle
- 175B paramètres
-上下文学习 sans gradient update

### Architecture
- 96 couches
- d_model = 12288
- 96 heads d_attention = 128
- 175B paramètres
- Context: 4096 tokens

### Mécanismes clés
1. **Few-shot (FS)**: K exemples dans le prompt
2. **One-shot (1S)**: 1 exemple
3. **Zero-shot (0S)**: Pas d'exemple
4. **Scaling laws**: Performance ~ N^(-0.075)

### Benchmarks
- LAMBADA: 76.2% (PPL)
- TriviaQA: 64.3%
- WebQuestions: 41.5%
- PIQA: 81.0%

---

##2022 - InstructGPT / ChatGPT

### Modèle: InstructGPT
- **Publication**: "Training language models to follow instructions with human feedback"
- **Date**: Mars 2022
- **arXiv**: 2203.02155
- **Auteurs**: Long Ouyang, Jeff Wu, Xu Jiang et al. (OpenAI)

### Contribution principale
**RLHF** (Reinforcement Learning from Human Feedback)
- Alignement: le modèle suit les instructions
- Plus utile, moins dangereux

### Processus
1. **SFT**: Fine-tuning supervisé sur données labelisées
2. **RM**: Entraîner un Reward Model
3. **PPO**: Optimiser contre le RM

### Architecture
- Same architecture as GPT-3
- 1.3B paramètres ( InstructGPT 1.3B > GPT-3 175M sur certaines tâches)

### Résultats
- 70% préférences humaines pour InstructGPT vs GPT-3
- Amélioration sur vérité/honnêteté

---

##2023 - LLaMA

### Modèle: LLaMA
- **Publication**: "LLaMA: Open and Efficient Foundation Language Models"
- **Date**: Février 2023
- **arXiv**: 2302.13971
- **Auteurs**: Hugo Touvron, Laurent Mazare et al. (Meta AI)

### Contribution principale
**Open-source** - Modèles高效的
- 7B, 13B, 33B, 65B paramètres
- Entraînés sur plus de tokens que GPT-3

### Mécanismes clés
1. **Pre-norm**: Normalisation avant les residual
2. **SwiGLU**: Activation Swiglu au lieu de ReLU
3. **Rotary Embeddings**: Position embeddings rotatifs
4. **Attention without masks**: Pour 33B et 65B

### Architecture
- Variantes: 7B, 13B, 33B, 65B
- Tokens entraînés: 1.4T (7B), 1T (13B), 1.4T (33B/65B)

---

##2023 - LLaMA 2

### Modèle: LLaMA 2
- **Publication**: "Llama 2: Open Foundation and Chat Models"
- **Date**: Juillet 2023
- **arXiv**: 2307.01394
- **Auteurs**: Hugo Touvron, Louis Martin et al. (Meta AI)

### Contribution principale
**Open-source commercial** - LLaMA 2 disponible pour usage commercial
- Fine-tuned sur RLHF (PPO et Rejection Sampling)
- Chat version: LLaMA 2 Chat

### Architecture
- 7B, 13B, 70B paramètres
- Contexte: 4096 tokens (extensible à 32K)

### Améliorations vs LLaMA 1
- +40% données d'entraînement
- +1M annotations humaines pour RLHF
- Ghost Attention pour的长对话

---

##2023 - GPT-4

### Modèle: GPT-4
- **Publication**: "GPT-4 Technical Report"
- **Date**: Mars 2023
- **arXiv**: 2303.08774
- **Auteurs**: OpenAI

### Contribution principale
**Multimodal** - Comprend images en entrée
- +40% plus performant que GPT-3.5 sur tâches complexes
- Capacité de raisonnement avancée

### Architecture (non révélé)
- Modèle multimodal (vision + texte)
- Contexte: 8K tokens (32K pour certains)

### Résultats
- MMLU: 86.4% (vs 70% GPT-3.5)
- HumanEval: 67% (vs 48%)
- SAT: 90e percentile

---

##Tendances 2024-2025 (àdocumenter)

### Modèles attendus
- GPT-4.5 / GPT-5
- Claude 3 (Anthropic)
- Gemini 1.5 (Google)
- Mistral (Mistral AI)
- Qwen (Alibaba)

### Tendances clés
1. **Contexte long**: 100K-1M tokens
2. **Multimodalité native**: Image, audio, vidéo
3. **Agents**: Capacités de raisonnement autonome
4. **Efficiency**: Quantification, distillation
5. **Open-source**: Llama 3, Mistral, Qwen

---

##Tableau Récapitulatif

| Année | Modèle | Paramètres | Innovation clé | Benchmark clé |
|-------|--------|------------|----------------|---------------|
| 2017 | Transformer | 65M-213M | Self-attention | WMT EN-DE 28.4 |
| 2018 | BERT | 110M-340M | MLM bidirectionnel | GLUE 78.3 |
| 2018 | GPT | 117M | Pre-training + fine-tuning | - |
| 2019 | GPT-2 | 1.5B | Zéro-shot | - |
| 2019 | T5 | 770M-11B | Text-to-text | SuperGLUE 88.0 |
| 2020 | GPT-3 | 175B | Few-shot | LAMBADA 76.2 |
| 2022 | InstructGPT | 1.3B-175B | RLHF | HH preferences |
| 2023 | LLaMA | 7B-65B | Open-source efficient | MMLU 68.2 |
| 2023 | LLaMA 2 | 7B-70B | Open commercial | MMLU 69.4 |
| 2023 | GPT-4 | ~1.7T (?) | Multimodal | MMLU 86.4 |

---

## Références

1. Vaswani et al. (2017). "Attention Is All You Need". arXiv:1706.03762
2. Devlin et al. (2018). "BERT: Pre-training of Deep Bidirectional Transformers". arXiv:1810.04805
3. Radford et al. (2018). "Improving Language Understanding by Generative Pre-Training". OpenAI
4. Radford et al. (2019). "Language Models are Unsupervised Multitask Learners". arXiv:1908.09203
5. Raffel et al. (2019). "Exploring the Limits of Transfer Learning with T5". arXiv:1910.10683
6. Brown et al. (2020). "Language Models are Few-Shot Learners". arXiv:2005.14165
7. Ouyang et al. (2022). "Training language models with human feedback". arXiv:2203.02155
8. Touvron et al. (2023). "LLaMA: Open and Efficient Foundation Language Models". arXiv:2302.13971
9. Touvron et al. (2023). "Llama 2: Open Foundation and Chat Models". arXiv:2307.01394
10. OpenAI (2023). "GPT-4 Technical Report". arXiv:2303.08774