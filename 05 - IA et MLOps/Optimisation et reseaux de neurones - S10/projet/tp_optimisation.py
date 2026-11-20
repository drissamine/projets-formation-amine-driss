
"""
Projet TP Deep Learning - Optimisation From Scratch
Auteur: DRISS Amine
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# ========== 1. FONCTIONS D'ACTIVATION ==========
def sigmoid(z):
    """Sortie entre 0 et 1 (proba)"""
    return 1 / (1 + np.exp(-z))

def sigmoid_derivative(z):
    s = sigmoid(z)
    return s * (1 - s)

def relu(z):
    """Max(0, z) - Standard pour couches cachées"""
    return np.maximum(0, z)

def relu_derivative(z):
    """1 si z > 0 sinon 0"""
    return (z > 0).astype(float)

# ========== 2. INITIALISATION ==========
def initialize_parameters(layer_dims):
    """Initialisation de He pour ReLU"""
    np.random.seed(42)
    parameters = {}
    L = len(layer_dims)

    for l in range(1, L):
        # Initialisation de He (recommandé pour ReLU)
        parameters['W' + str(l)] = np.random.randn(layer_dims[l], layer_dims[l-1]) * np.sqrt(2 / layer_dims[l-1]) 
        # Biais à zéro
        parameters['b' + str(l)] = np.zeros((layer_dims[l], 1))
        
    return parameters

# ========== 3. FORWARD PROPAGATION ==========
def forward_propagation(X, parameters, activation_hidden='relu'):
    cache = {}
    A = X.T # Transpose pour avoir (n_features, m_samples)
    L = len(parameters) // 2
    
    # Couches cachées
    for l in range(1, L):
        A_prev = A 
        W = parameters['W' + str(l)]
        b = parameters['b' + str(l)]
        
        Z = np.dot(W, A_prev) + b
        
        if activation_hidden == 'relu':
            A = relu(Z)
        else: # sigmoid
            A = sigmoid(Z)
            
        cache['A' + str(l-1)] = A_prev
        cache['Z' + str(l)] = Z
    
    # Couche de sortie (Toujours Sigmoid pour classification binaire)
    W = parameters['W' + str(L)]
    b = parameters['b' + str(L)]
    ZL = np.dot(W, A) + b
    AL = sigmoid(ZL)
    
    cache['A' + str(L-1)] = A
    cache['Z' + str(L)] = ZL
    cache['AL'] = AL
    
    return AL, cache

# ========== 4. COÛT ==========
def compute_cost(AL, Y):
    m = Y.shape[0]
    Y = Y.T # Pour matcher AL
    
    # Ajout d'epsilon pour éviter log(0)
    epsilon = 1e-8
    cost = -1/m * np.sum(Y * np.log(AL + epsilon) + (1-Y) * np.log(1-AL + epsilon))
    return np.squeeze(cost)

# ========== 5. BACKWARD PROPAGATION ==========
def backward_propagation(AL, Y, parameters, cache, activation_hidden='relu'):
    gradients = {}
    L = len(parameters) // 2
    m = AL.shape[1]
    Y = Y.reshape(AL.shape) 
    
    # Gradient sortie
    dZL = AL - Y # Dérivée simplifiée BCE + Sigmoid
    gradients["dW" + str(L)] = 1./m * np.dot(dZL, cache['A' + str(L-1)].T)
    gradients["db" + str(L)] = 1./m * np.sum(dZL, axis=1, keepdims=True)
    
    dA_prev = np.dot(parameters['W' + str(L)].T, dZL)
    
    # Gradients couches cachées
    for l in reversed(range(1, L)):
        Z = cache['Z' + str(l)]
        
        if activation_hidden == 'relu':
            dZ = dA_prev * relu_derivative(Z)
        else:
            dZ = dA_prev * sigmoid_derivative(Z)
            
        gradients["dW" + str(l)] = 1./m * np.dot(dZ, cache['A' + str(l-1)].T)
        gradients["db" + str(l)] = 1./m * np.sum(dZ, axis=1, keepdims=True)
        
        if l > 1:
            dA_prev = np.dot(parameters['W' + str(l)].T, dZ)
            
    return gradients

# ========== 6. UPDATE ==========
def update_parameters(parameters, gradients, learning_rate):
    L = len(parameters) // 2 
    for l in range(1, L + 1):
        parameters["W" + str(l)] = parameters["W" + str(l)] - learning_rate * gradients["dW" + str(l)]
        parameters["b" + str(l)] = parameters["b" + str(l)] - learning_rate * gradients["db" + str(l)]
    return parameters

# ========== 7. ENTRAÎNEMENT ==========
def train_neural_network(X, Y, layer_dims, learning_rate=0.01, num_iterations=1000, activation_hidden='relu', print_cost=False):
    parameters = initialize_parameters(layer_dims)
    costs = []
    
    for i in range(num_iterations):
        AL, cache = forward_propagation(X, parameters, activation_hidden)
        cost = compute_cost(AL, Y)
        gradients = backward_propagation(AL, Y, parameters, cache, activation_hidden)
        parameters = update_parameters(parameters, gradients, learning_rate)
        
        if i % 100 == 0:
            costs.append(cost)
            if print_cost:
                print(f"Cost after iteration {i}: {cost:.6f}")
                
    return parameters, costs

# ========== 8. PRÉDICTION ==========
def predict(X, parameters, activation_hidden='relu'):
    AL, _ = forward_propagation(X, parameters, activation_hidden)
    predictions = (AL > 0.5).astype(int)
    return predictions.T 

def compute_accuracy(predictions, Y):
    return (100 - np.mean(np.abs(predictions - Y)) * 100)

# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    print("=== PROJET DEEP LEARNING : PARTIE 1 - Chargement ===")
    
    # 1. Charger
    data = load_breast_cancer()
    X = data.data
    y = data.target

    # 2. Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. Normalisation
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # 4. Reshape
    y_train = y_train.reshape(-1, 1)
    y_test = y_test.reshape(-1, 1)

    print(f"Données chargées : {X_train.shape[0]} exemples d'entraînement, {X_test.shape[0]} exemples de test")
    print("-" * 50)

    # --- Configuration Optimale ---
    final_arch = [30, 20, 10, 1]
    final_lr = 0.01 
    final_iter = 3000
    final_activation = 'relu'

    print(f"=== PARTIE 2 - Entraînement Optimisé ===")
    print(f"Architecture: {final_arch}")
    print(f"Learning Rate: {final_lr}")
    print(f"Iterations: {final_iter}")
    print(f"Activation: {final_activation}")
    print("-" * 50)

    parameters_final, costs_final = train_neural_network(
        X_train, y_train, 
        final_arch, 
        learning_rate=final_lr, 
        num_iterations=final_iter, 
        activation_hidden=final_activation,
        print_cost=True
    )

    # --- Résultats ---
    print("-" * 50)
    print("=== PARTIE 3 - Résultats ===")
    y_pred_final = predict(X_test, parameters_final, final_activation)
    acc_final = compute_accuracy(y_pred_final, y_test)

    print(f"🏆 ACCURACY FINALE SUR TEST : {acc_final:.2f}%")

    if acc_final >= 95:
        print("✅ OBJECTIF ATTEINT ! Bravo !")
    else:
        print("⚠️ Presque ! Essayez d'ajuster les hyperparamètres.")
    
    # --- Visualisation ---
    try:
        plt.plot(costs_final)
        plt.ylabel('Coût')
        plt.xlabel('Itérations (x100)')
        plt.title("Courbe d'apprentissage")
        plt.savefig('courbe_apprentissage.png')
        print("Graphique sauvegardé sous 'courbe_apprentissage.png'.")
    except Exception as e:
        print(f"Impossible de générer le graphique: {e}")
