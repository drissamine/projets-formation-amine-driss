"""
Script Python pour générer les figures originales du projet LLM
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Configuration du style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 12

# =============================================================================
# Figure 1: Frise chronologique des modèles LLM
# =============================================================================

def create_timeline():
    """Crée la frise chronologique des modèles LLM"""
    
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # Données des modèles
    models = [
        ('Transformer', 2017, 65, '#2ecc71'),
        ('BERT', 2018, 110, '#3498db'),
        ('GPT', 2018, 117, '#9b59b6'),
        ('GPT-2', 2019, 1500, '#e74c3c'),
        ('T5', 2019, 770, '#f39c12'),
        ('GPT-3', 2020, 175000, '#1abc9c'),
        ('InstructGPT', 2022, 175000, '#34495e'),
        ('LLaMA', 2023, 65000, '#e67e22'),
        ('LLaMA 2', 2023, 70000, '#d35400'),
        ('GPT-4', 2023, 1700000, '#2c3e50'),
    ]
    
    # Tracer les points
    years = [m[1] for m in models]
    params = [m[2] for m in models]
    colors = [m[3] for m in models]
    
    # Echelle log pour les paramètres
    ax.semilogy(years, params, 'o', markersize=15, color='steelblue', alpha=0.8)
    
    # Ajouter les annotations
    for i, (name, year, param, color) in enumerate(models):
        # Nom du modèle
        offset = 0.15 if i % 2 == 0 else -0.25
        ax.annotate(name, (year, param), 
                   textcoords="offset points", 
                   xytext=(0, 20 if i % 2 == 0 else -25),
                   ha='center', fontsize=10, fontweight='bold')
        
        # Nombre de paramètres
        param_str = f"{param}M" if param < 1000 else f"{param/1000:.1f}B"
        ax.annotate(param_str, (year, param),
                   textcoords="offset points",
                   xytext=(0, -15 if i % 2 == 0 else 15),
                   ha='center', fontsize=8, color='gray')
    
    ax.set_xlabel('Année', fontsize=14)
    ax.set_ylabel('Paramètres (échelle log)', fontsize=14)
    ax.set_title('Évolution des modèles de langue (2017-2024)', fontsize=16, fontweight='bold')
    
    # Ligne verticale pour chaque année
    for year in range(2017, 2025):
        ax.axvline(x=year, color='lightgray', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('figure_timeline.png', dpi=300, bbox_inches='tight')
    print("Figure 1: timeline created -> figure_timeline.png")

# =============================================================================
# Figure 2: Évolution des benchmarks
# =============================================================================

def create_benchmark_evolution():
    """Crée l'évolution des performances sur les benchmarks"""
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Données MMLU
    mmlu_data = {
        'GPT-3 (2020)': 43.9,
        'Gopher (2021)': 60.0,
        'Chinchilla (2022)': 75.0,
        'GPT-4 (2023)': 86.4,
        'Claude 2 (2023)': 86.8,
        'GPT-4.5 (2024)': 87.2,
    }
    
    # Données HumanEval
    humaneval_data = {
        'GPT-3 (2020)': 0.0,
        'CodeGen (2022)': 30.3,
        'Codex (2022)': 47.0,
        'GPT-4 (2023)': 67.0,
        'Claude 3 (2024)': 73.0,
    }
    
    # Plot MMLU
    ax1 = axes[0]
    models_m = list(mmlu_data.keys())
    scores_m = list(mmlu_data.values())
    bars1 = ax1.bar(range(len(models_m)), scores_m, color='#3498db', alpha=0.8)
    ax1.set_xticks(range(len(models_m)))
    ax1.set_xticklabels(models_m, rotation=45, ha='right')
    ax1.set_ylabel('Score MMLU (%)')
    ax1.set_title('Performance MMLU', fontweight='bold')
    ax1.set_ylim(0, 100)
    
    # Ajouter les valeurs
    for bar, score in zip(bars1, scores_m):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{score:.1f}%', ha='center', fontsize=9)
    
    # Plot HumanEval
    ax2 = axes[1]
    models_h = list(humaneval_data.keys())
    scores_h = list(humaneval_data.values())
    bars2 = ax2.bar(range(len(models_h)), scores_h, color='#e74c3c', alpha=0.8)
    ax2.set_xticks(range(len(models_h)))
    ax2.set_xticklabels(models_h, rotation=45, ha='right')
    ax2.set_ylabel('Pass@1 (%)')
    ax2.set_title('Performance HumanEval (Code)', fontweight='bold')
    ax2.set_ylim(0, 100)
    
    # Ajouter les valeurs
    for bar, score in zip(bars2, scores_h):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{score:.1f}%', ha='center', fontsize=9)
    
    plt.suptitle('Évolution des performances sur les benchmarks', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('figure_benchmarks.png', dpi=300, bbox_inches='tight')
    print("Figure 2: benchmarks created -> figure_benchmarks.png")

# =============================================================================
# Figure 3: Architecture du Transformer
# =============================================================================

def create_transformer_architecture():
    """Crée un schéma de l'architecture Transformer"""
    
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Couleurs
    encoder_color = '#3498db'
    decoder_color = '#e74c3c'
    attention_color = '#2ecc71'
    ffn_color = '#f39c12'
    
    # Encoder (gauche)
    encoder_box = mpatches.FancyBboxPatch((1, 7), 3, 2, boxstyle="round,pad=0.05",
                                          facecolor=encoder_color, alpha=0.3, edgecolor=encoder_color, linewidth=2)
    ax.add_patch(encoder_box)
    ax.text(2.5, 8, 'Encoder\n(6 layers)', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Decoder (droite)
    decoder_box = mpatches.FancyBboxPatch((6, 7), 3, 2, boxstyle="round,pad=0.05",
                                          facecolor=decoder_color, alpha=0.3, edgecolor=decoder_color, linewidth=2)
    ax.add_patch(decoder_box)
    ax.text(7.5, 8, 'Decoder\n(6 layers)', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Input
    ax.add_patch(mpatches.FancyBboxPatch((0.5, 8), 0.5, 0.5, boxstyle="round,pad=0.02",
                                         facecolor='gray', alpha=0.5))
    ax.annotate('Input\nEmbeddings', (0.5, 7.5), fontsize=8, ha='center')
    
    # Output
    ax.add_patch(mpatches.FancyBboxPatch((9.5, 8), 0.5, 0.5, boxstyle="round,pad=0.02",
                                         facecolor='gray', alpha=0.5))
    ax.annotate('Output\nProba', (9.5, 7.5), fontsize=8, ha='center')
    
    # Flèches input/output
    ax.annotate('', xy=(1.5, 8.25), xytext=(1, 8.25), arrowprops=dict(arrowstyle='->', color='gray'))
    ax.annotate('', xy=(9, 8.25), xytext=(9.5, 8.25), arrowprops=dict(arrowstyle='->', color='gray'))
    
    # Cross-attention flèche
    ax.annotate('', xy=(6, 8), xytext=(4, 8), arrowprops=dict(arrowstyle='->', color='green', lw=2))
    ax.text(5, 8.3, 'Cross-Attention', ha='center', fontsize=9, color='green')
    
    # Encoder self-attention (dans encoder)
    ax.add_patch(mpatches.FancyBboxPatch((1.2, 5.5), 2.5, 1, boxstyle="round,pad=0.02",
                                         facecolor=attention_color, alpha=0.5))
    ax.text(2.45, 6, 'Self-Attention', ha='center', va='center', fontsize=10)
    
    # FFN (dans encoder)
    ax.add_patch(mpatches.FancyBboxPatch((1.2, 4), 2.5, 1, boxstyle="round,pad=0.02",
                                         facecolor=ffn_color, alpha=0.5))
    ax.text(2.45, 4.5, 'Feed-Forward', ha='center', va='center', fontsize=10)
    
    # Layer Norm
    ax.text(4, 6, 'LayerNorm\n+ Residual', ha='left', va='center', fontsize=8, color='gray')
    ax.text(4, 4.5, 'LayerNorm\n+ Residual', ha='left', va='center', fontsize=8, color='gray')
    
    # Decoder self-attention (dans decoder)
    ax.add_patch(mpatches.FancyBboxPatch((6.2, 5.5), 2.5, 1, boxstyle="round,pad=0.02",
                                         facecolor=attention_color, alpha=0.5))
    ax.text(7.45, 6, 'Masked\nSelf-Attention', ha='center', va='center', fontsize=10)
    
    # Decoder FFN
    ax.add_patch(mpatches.FancyBboxPatch((6.2, 4), 2.5, 1, boxstyle="round,pad=0.02",
                                         facecolor=ffn_color, alpha=0.5))
    ax.text(7.45, 4.5, 'Feed-Forward', ha='center', va='center', fontsize=10)
    
    # Title
    ax.set_title('Architecture du Transformer', fontsize=16, fontweight='bold', y=0.98)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=encoder_color, alpha=0.3, label='Encoder'),
        mpatches.Patch(facecolor=decoder_color, alpha=0.3, label='Decoder'),
        mpatches.Patch(facecolor=attention_color, alpha=0.5, label='Attention'),
        mpatches.Patch(facecolor=ffn_color, alpha=0.5, label='Feed-Forward'),
    ]
    ax.legend(handles=legend_elements, loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.05))
    
    plt.tight_layout()
    plt.savefig('figure_architecture.png', dpi=300, bbox_inches='tight')
    print("Figure 3: architecture created -> figure_architecture.png")

# =============================================================================
# Figure 4: Comparaison des innovations
# =============================================================================

def create_innovations_comparison():
    """Crée un graphique comparatif des innovations"""
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Données: [(Model, Innovation, Impact, Year)]
    data = [
        ('Transformer\n(2017)', 'Self-Attention\nParallélisation', 9, '#2ecc71'),
        ('BERT\n(2018)', 'MLM\nTransfer Learning', 10, '#3498db'),
        ('GPT\n(2018)', 'Pre-training\nGenerative', 7, '#9b59b6'),
        ('GPT-2\n(2019)', 'Zero-shot\nScaling', 8, '#e74c3c'),
        ('T5\n(2019)', 'Text-to-Text\nUnified', 6, '#f39c12'),
        ('GPT-3\n(2020)', 'Few-shot\nEmergence', 10, '#1abc9c'),
        ('InstructGPT\n(2022)', 'RLHF\nAlignment', 9, '#34495e'),
        ('LLaMA\n(2023)', 'Open-source\nEfficiency', 10, '#e67e22'),
        ('GPT-4\n(2023)', 'Multimodal\nReasoning', 10, '#2c3e50'),
    ]
    
    names = [d[0] for d in data]
    innovations = [d[1] for d in data]
    impacts = [d[2] for d in data]
    colors = [d[3] for d in data]
    
    x = np.arange(len(names))
    
    bars = ax.bar(x, impacts, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
    
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9)
    ax.set_ylabel('Impact (1-10)', fontsize=12)
    ax.set_title('Impact des innovations par modèle', fontsize=16, fontweight='bold')
    ax.set_ylim(0, 12)
    
    # Ajouter les labels d'innovation
    for i, (bar, innov) in enumerate(zip(bars, innovations)):
        ax.text(bar.get_x() + bar.get_width()/2, 0.5, innov,
               ha='center', va='bottom', fontsize=7, rotation=0,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Ajouter les valeurs
    for bar, impact in zip(bars, impacts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
               f'{impact}', ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('figure_innovations.png', dpi=300, bbox_inches='tight')
    print("Figure 4: innovations created -> figure_innovations.png")

# =============================================================================
# Figure 5: Scaling Laws
# =============================================================================

def create_scaling_laws():
    """Crée le graphique des scaling laws"""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Données simulées basées sur les paper
    params = np.array([100, 1e9, 1e11, 1e12])
    
    # Performance (simulée)
    performance = 30 + 10 * np.log10(params / 1e8)
    
    ax.loglog(params, performance, 'o-', color='#3498db', markersize=10, linewidth=2)
    
    # Annotations
    ax.annotate('GPT-1\n117M', (117e6, 58), fontsize=9, ha='center')
    ax.annotate('GPT-2\n1.5B', (1.5e9, 68), fontsize=9, ha='center')
    ax.annotate('GPT-3\n175B', (175e9, 78), fontsize=9, ha='center')
    ax.annotate('GPT-4\n~1.7T', (1.7e12, 88), fontsize=9, ha='center')
    
    ax.set_xlabel('Paramètres', fontsize=12)
    ax.set_ylabel('Performance (score simulé)', fontsize=12)
    ax.set_title('Scaling Laws: Performance vs Paramètres', fontsize=16, fontweight='bold')
    
    # Grille
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('figure_scaling.png', dpi=300, bbox_inches='tight')
    print("Figure 5: scaling laws created -> figure_scaling.png")

# =============================================================================
# Exécution principale
# =============================================================================

if __name__ == "__main__":
    print("Génération des figures originales...")
    create_timeline()
    create_benchmark_evolution()
    create_transformer_architecture()
    create_innovations_comparison()
    create_scaling_laws()
    print("\nAll figures created successfully!")
    print("Generated files:")
    print("  - figure_timeline.png")
    print("  - figure_benchmarks.png")
    print("  - figure_architecture.png")
    print("  - figure_innovations.png")
    print("  - figure_scaling.png")