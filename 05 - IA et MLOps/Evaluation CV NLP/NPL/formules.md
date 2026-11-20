# Formules et Algorithmes Clés - Modèles de Langue (LLM)

Ce document documente les formules et algorithmes clés des LLM avec des explanations intuitives.

---

## 1. Scaled Dot-Product Attention

### Formule
```
Attention(Q, K, V) = softmax(QK^T / √d_k)V
```

### Explication intuitive
Imaginez que vous faites une recherche sur Amazon:
- **Q (Query)**: Ce que vous cherchez
- **K (Key)**: Les titres des produits
- **V (Value)**: Le contenu des produits

L'attention calcule la "pertinence" entre votre recherche et chaque produit (QK^T), puis utilise ces scores pour récupérer l'information pertinente (V).

### Pourquoi "scaled"?
Le facteur √d_k empêche les produits scalaires de devenir trop grands, ce qui push softmax vers des régions de gradients très petits.

### Code Python
```python
import numpy as np

def scaled_dot_product_attention(Q, K, V, d_k):
    # Q, K, V: (batch, heads, seq_len, d_k)
    scores = np.matmul(Q, K.transpose(-2, -1)) / np.sqrt(d_k)
    attention_weights = softmax(scores, axis=-1)
    return np.matmul(attention_weights, V)
```

---

## 2. Multi-Head Attention

### Formule
```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h)W^O

où head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
```

### Explication intuitive
Plutôt que d'avoir un seul type d'attention, on en a plusieurs qui fonctionnent en parallèle:
- **Head 1**: Peut se concentrer sur la grammaire
- **Head 2**: Peut se concentrer sur les relations sémantiques
- **Head 3**: Peut se concentrer sur les dépendances à longue distance

Chaque "tête" apprend un type de relation différent.

### Code Python
```python
def multi_head_attention(Q, K, V, num_heads, d_model):
    d_k = d_model // num_heads
    
    # Projections linéaires
    Q_proj = linear(Q, d_k, num_heads)
    K_proj = linear(K, d_k, num_heads)
    V_proj = linear(V, d_k, num_heads)
    
    # Attention pour chaque tête
    heads = [scaled_dot_product_attention(Q_proj[:, i], K_proj[:, i], V_proj[:, i], d_k) 
             for i in range(num_heads)]
    
    # Concaténation et projection finale
    output = linear(concat(heads), d_model)
    return output
```

---

## 3. Masked Self-Attention (GPT)

### Formule
```
Masked_Attention(Q, K, V) = softmax(M + QK^T / √d_k)V

où M[i,j] = 0 si j ≤ i (autorisé)
           = -∞ si j > i (masqué)
```

### Explication intuitive
GPT est un modèle **causal** - il prédit le mot suivant en ne regardant que les mots précédents.
Le masque garantit que le modèle ne peut pas "voir" les mots futurs pendant l'entraînement.

### Visualisation
```
Position:    1    2    3    4
Mask:        [0   -∞  -∞  -∞ ]   # Position 1
             [0    0   -∞  -∞ ]   # Position 2
             [0    0    0   -∞ ]  # Position 3
             [0    0    0    0 ]  # Position 4
```

---

## 4. Masked Language Modeling (BERT)

### Formule
```
Loss_MLM = -E[∑_{i ∈ masked} log P(x_i | x_{-context})]
```

### Processus
1. **Masking**: Remplacer 15% des tokens par [MASK]
2. **Prediction**: Le modèle prédit le token original
3. **Loss**: Cross-entropy entre prédiction et réalité

### Types de mask (BERT)
- 80% → [MASK]
- 10% → token aléatoire
- 10% → garder le token original

---

## 5. Positional Encoding (Sinusoidal)

### Formule
```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

### Explication intuitive
Les transformer n'ont pas de notion d'ordre intrinsèque. On ajoute des "signaux" qui indiquent la position:
- **Positions paires** (2i):sinus
- **Positions impaires** (2i+1):cosinus

Les longues wavelengths permettent dcapturer les dépendances à longue distance.

### Propriété importante
```
PE(pos + k) peut être représenté comme une fonction linéaire de PE(pos)
→ Le modèle peut apprendre à raisonner sur les positions relatives
```

---

## 6. Feed-Forward Network

### Formule
```
FFN(x) = max(0, xW_1 + b_1)W_2 + b_2
       = ReLU(xW_1 + b_1)W_2 + b_2
```

### Explication intuitive
Après l'attention, un réseau feed-forward traite chaque position indépendamment:
- **Couche 1**: Projette vers un espace plus grand (d_ff = 4 * d_model)
- **Activation**: ReLU introduit la non-linéarité
- **Couche 2**: Revient à la dimension originale

### Code Python
```python
def feed_forward(x, d_model, d_ff):
    W1 = np.random.randn(d_model, d_ff)
    b1 = np.zeros(d_ff)
    W2 = np.random.randn(d_ff, d_model)
    b2 = np.zeros(d_model)
    
    hidden = np.maximum(0, x @ W1 + b1)  # ReLU
    return hidden @ W2 + b2
```

---

## 7. Layer Normalization

### Formule
```
LN(x) = γ * (x - μ) / σ + β

où μ = (1/n) ∑x_i
     σ = sqrt((1/n) ∑(x_i - μ)²)
```

### Explication intuitive
Standardiser les activations pour avoir:
- Moyenne = 0
- Écart-type = 1

Puis learnable scale (γ) et shift (β) pour permettre au réseau de apprendre la bonne échelle.

### Différence avec Batch Norm
- **Batch Norm**: Normalise sur le batch
- **Layer Norm**: Normalise sur les features (indépendant du batch)

---

## 8. Résidual Connection

### Formule
```
Output = LayerNorm(x + Sublayer(x))
```

### Explication intuitive
Le "sublayer" (attention ou FFN) apprend une transformation, mais on ajoute l'entrée originale.
- Si la transformation est inutile, le réseau peut simplement la "zéroer"
- Facilitates le gradient flow pour les couches profondes
- Permet d'entraîner des réseaux de 100+ couches

---

## 9. Cross-Entropy Loss

### Formule
```
Loss = -∑_i y_i * log(ŷ_i)
```

### Explication intuitive
Mesure la "distance" entre:
- **y**: Distribution de probabilité目标 (one-hot du vrai mot)
- **ŷ**: Distribution de probabilité prédite par le modèle

Minimiser cette loss = maximiser la probabilité du vrai mot.

---

## 10. Beam Search

### Formule
```
Pour chaque étape:
  1. Prendre les top-k candidats
  2. Pour chaque candidat, calculer le score cumulé
  3. Garder les top-k pour l'étape suivante
```

### Explication intuitive
Au lieu de choisir greedy (le mot le plus probable à chaque étape), on garde plusieurs "hypothèses" en parallèle:
- **Beam size = 1**: Greedy search
- **Beam size = 3-5**: Bon compromis qualité/vitesse

### Code Python
```python
def beam_search(model, start_token, beam_size=3, max_len=50):
    # Initialiser avec le token de départ
    beams = [(0.0, [start_token])]
    
    for _ in range(max_len):
        candidates = []
        for score, seq in beams:
            # Proposer les nächsten mots
            probs = model.predict(seq[-1])
            top_k = np.argsort(probs)[-beam_size:]
            
            for p in top_k:
                new_score = score + np.log(probs[p])
                new_seq = seq + [p]
                candidates.append((new_score, new_seq))
        
        # Garder les top-k
        beams = sorted(candidates, key=lambda x: x[0])[-beam_size:]
    
    return beams[0][1]  # Retourner la meilleure séquence
```

---

## 11. RLHF - PPO

### Formule
```
Loss_RLHF = E[min(r_t(θ) * A_t, clip(r_t(θ), 1-ε, 1+ε) * A_t)]
```

### Explication intuitive
PPO (Proximal Policy Optimization) empêche les changements trop radicaux de la politique:
- **r_t(θ)**: Ratio entre nouvelle et ancienne probabilité
- **clip**: Limite les changements à ±ε (typiquement 0.2)
- **A_t**: Avantage estimé (reward - baseline)

---

## Tableau Récapitulatif

| Formule | Contexte | Purpose |
|---------|----------|---------|
| Attention(Q,K,V) | Transformer | Capturer dépendances |
| MultiHead | BERT, GPT | Apprendre relations multiples |
| Masked Attention | GPT | Préserver causalité |
| MLM | BERT | Pré-entraînement bidirectionnel |
| PE | Transformer | Représenter positions |
| FFN | Transformer | Apprentissage non-linéaire |
| LayerNorm | Tous | Stabiliser entraînement |
| Residual | Tous | Faciliter gradient flow |
| Cross-Entropy | Fine-tuning | Mesurer erreur |
| Beam Search | Génération | Améliorer qualité |

---

## Références

1. Vaswani et al. (2017). "Attention Is All You Need". Section 3.2.
2. Devlin et al. (2018). "BERT". Section 3.1.
3. Radford et al. (2019). "GPT-2". Section 2.
4. Brown et al. (2020). "GPT-3". Section 2.
5. Ouyang et al. (2022). "InstructGPT". Section 3.3.