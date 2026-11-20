"""
Solutions aux exercices du TP Prétraitement des Images
Ce script contient les implémentations complètes de tous les exercices.
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2
from skimage import io, filters, exposure, transform, util, color
from skimage import morphology, restoration
from skimage.metrics import peak_signal_noise_ratio as psnr, structural_similarity as ssim
from skimage.restoration import denoise_nl_means, estimate_sigma
import warnings
warnings.filterwarnings("ignore")

# Configuration matplotlib
plt.rcParams.update({
    "figure.facecolor": "#F8F9FA",
    "axes.facecolor":   "#FFFFFF",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   12,
    "axes.titleweight": "bold",
    "figure.dpi":       100,
})

# Palette de couleurs
NAVY   = "#0F2044"
BLUE   = "#2E86DE"
TEAL   = "#0DC0C0"
ORANGE = "#F97316"
GREEN  = "#22C55E"
RED    = "#E74C3C"
PURPLE = "#9B59B6"

# ============================================================
# CONFIGURATION INITIALE (Same as TP)
# ============================================================
np.random.seed(42)
H, W = 256, 256

def make_base_image():
    img = np.zeros((H, W, 3), dtype=np.uint8)
    img[:, :]          = [200, 210, 220]   # fond gris-bleu
    img[180:, :]       = [60, 120, 50]     # sol vert
    img[80:180, 70:190]= [190, 80, 60]     # bâtiment rouge
    for i in range(40):                     # toit triangulaire
        s = max(0, 70 - i); e = min(W, 190 + i)
        img[40+i, s:e] = [100, 50, 30]
    img[110:160, 100:130] = [180, 210, 230] # fenêtre gauche
    img[110:160, 150:180] = [180, 210, 230] # fenêtre droite
    img[150:180, 120:140] = [90, 55, 30]   # porte
    return img

def make_noisy_image(img, sigma=25):
    noise = np.random.randn(*img.shape) * sigma
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)

def make_dark_image(img, factor=0.35):
    return np.clip(img.astype(np.float32) * factor, 0, 255).astype(np.uint8)

def make_overexposed_image(img, factor=2.8):
    return np.clip(img.astype(np.float32) * factor, 0, 255).astype(np.uint8)

BASE_IMG   = make_base_image()
NOISY_IMG  = make_noisy_image(BASE_IMG, sigma=30)
DARK_IMG   = make_dark_image(BASE_IMG)
BRIGHT_IMG = make_overexposed_image(BASE_IMG)

# Images bruitées pour les exercices
def add_gaussian_noise(img, sigma=30):
    noise = np.random.randn(*img.shape) * sigma
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)

def add_salt_pepper(img, density=0.05):
    result = img.copy()
    mask   = np.random.rand(img.shape[0], img.shape[1])
    result[mask < density/2]        = 0
    result[mask > 1 - density/2]    = 255
    return result

def add_speckle(img, sigma=0.2):
    noise = np.random.randn(*img.shape) * sigma
    return np.clip(img.astype(np.float32) * (1 + noise), 0, 255).astype(np.uint8)

np.random.seed(0)
img_gauss = add_gaussian_noise(BASE_IMG, sigma=35)
img_sp    = add_salt_pepper(BASE_IMG, density=0.08)
img_speck = add_speckle(BASE_IMG, sigma=0.25)

# ============================================================
# EXERCICE 1 — Sélection de couleur par masque HSV
# ============================================================
print("=" * 60)
print("EXERCICE 1 — Sélection de couleur par masque HSV")
print("=" * 60)

# 1. Convertir BASE_IMG en HSV
img_hsv_ex1 = cv2.cvtColor(BASE_IMG, cv2.COLOR_RGB2HSV)

# 2. Créer le masque rouge (deux plages HSV)
lower1 = np.array([0,   80, 60])
upper1 = np.array([10, 255, 255])
lower2 = np.array([165, 80, 60])
upper2 = np.array([179, 255, 255])
mask1 = cv2.inRange(img_hsv_ex1, lower1, upper1)
mask2 = cv2.inRange(img_hsv_ex1, lower2, upper2)
mask_rouge = cv2.bitwise_or(mask1, mask2)

# 3. Appliquer le masque : fond grisé, zones rouges en couleur
gray_percep = (0.2126 * BASE_IMG[:,:,0] + 0.7152 * BASE_IMG[:,:,1] + 0.0722 * BASE_IMG[:,:,2]).astype(np.uint8)
gray3 = np.stack([gray_percep]*3, axis=2)
result = np.where(mask_rouge[:,:,np.newaxis] > 0, BASE_IMG, gray3 // 2)

# 4. Afficher : image originale | masque binaire | résultat
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
axes[0].imshow(BASE_IMG);           axes[0].set_title("Originale"); axes[0].axis("off")
axes[1].imshow(mask_rouge, cmap="gray"); axes[1].set_title("Masque rouge"); axes[1].axis("off")
axes[2].imshow(result);             axes[2].set_title("Sélection rouge"); axes[2].axis("off")
plt.tight_layout()
plt.suptitle("Exercice 1 — Sélection de couleur HSV", fontsize=14, fontweight="bold")
plt.show()

# 5. Histogramme H dans la zone sélectionnée
h_vals = img_hsv_ex1[:,:,0][mask_rouge > 0]
plt.figure(figsize=(8, 3))
plt.hist(h_vals, bins=60, color=ORANGE, edgecolor="white", alpha=0.85)
plt.title("Distribution du canal H dans la zone rouge sélectionnée")
plt.xlabel("Valeur H (0–179 en OpenCV)")
plt.ylabel("Fréquence")
plt.tight_layout()
plt.show()

# ============================================================
# EXERCICE 2 — Égalisation d'histogramme manuelle
# ============================================================
print("=" * 60)
print("EXERCICE 2 — Égalisation d'histogramme manuelle")
print("=" * 60)

def equalize_histogram_manual(img_gray):
    """Égalisation d'histogramme manuelle (image niveaux de gris)."""
    # 1. Calculer l'histogramme (256 niveaux, valeurs 0-255)
    hist, _ = np.histogram(img_gray.ravel(), bins=256, range=(0, 256))
    
    # 2. Calculer la CDF (histogramme cumulé)
    cdf = hist.cumsum()
    
    # 3. Normaliser la CDF : mapping vers [0, 255]
    cdf_min = cdf[cdf > 0].min()
    total   = img_gray.size
    mapping = np.round((cdf - cdf_min) / (total - cdf_min) * 255).astype(np.uint8)
    
    # 4. Appliquer le mapping pixel par pixel (via indexation NumPy)
    return mapping[img_gray]

# Test
gray_dark = (0.2126*DARK_IMG[:,:,0] + 0.7152*DARK_IMG[:,:,1] + 0.0722*DARK_IMG[:,:,2]).astype(np.uint8)

gray_eq_manual = equalize_histogram_manual(gray_dark)
gray_eq_ref    = cv2.equalizeHist(gray_dark)

diff = np.abs(gray_eq_manual.astype(np.int16) - gray_eq_ref.astype(np.int16))
print(f"Différence max avec la référence OpenCV : {diff.max()}")
print(f"Différence moyenne : {diff.mean():.4f}")

# Affichage
fig, axes = plt.subplots(1, 4, figsize=(18, 5))
axes[0].imshow(gray_dark,      cmap="gray"); axes[0].set_title("Originale (sombre)"); axes[0].axis("off")
axes[1].imshow(gray_eq_manual, cmap="gray"); axes[1].set_title("Votre égalisation");  axes[1].axis("off")
axes[2].imshow(gray_eq_ref,    cmap="gray"); axes[2].set_title("Référence OpenCV");   axes[2].axis("off")
axes[3].imshow(diff,           cmap="hot");  axes[3].set_title("Différence (absolu)");axes[3].axis("off")
plt.tight_layout()
plt.suptitle("Exercice 2 — Égalisation d'histogramme", fontsize=14, fontweight="bold")
plt.show()

# ============================================================
# EXERCICE 3 — CLAHE : hyperparamètres
# ============================================================
print("=" * 60)
print("EXERCICE 3 — CLAHE : hyperparamètres")
print("=" * 60)

clip_limits = [1.0, 2.0, 4.0, 8.0]
tile_sizes  = [(4,4), (8,8), (16,16)]

fig, axes = plt.subplots(len(clip_limits), len(tile_sizes), figsize=(12, 16))
for i, clip in enumerate(clip_limits):
    for j, tile in enumerate(tile_sizes):
        clahe   = cv2.createCLAHE(clipLimit=clip, tileGridSize=tile)
        lab     = cv2.cvtColor(BRIGHT_IMG, cv2.COLOR_RGB2LAB)
        lab[:,:,0] = clahe.apply(lab[:,:,0])
        result  = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        axes[i,j].imshow(result)
        axes[i,j].set_title("clip=%.1f, tile=%s" % (clip, str(tile)), fontsize=9)
        axes[i,j].axis("off")
plt.suptitle("Exercice 3 — CLAHE exploration hyperparamètres (image surexposée)", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.show()

print("Meilleure combinaison visuellement : clip=2.0, tile=(8,8) est un bon compromis")

# ============================================================
# EXERCICE 4 — Débruitage sélectif
# ============================================================
print("=" * 60)
print("EXERCICE 4 — Débruitage sélectif")
print("=" * 60)

# Dictionnaires
noisy_dict = {
    "Gaussien (sigma=35)":  img_gauss,
    "Sel & Poivre (8%)": img_sp,
    "Speckle (0.25)":   img_speck,
}

filters_dict = {
    "Moyen 5x5":     lambda x: cv2.blur(x, (5, 5)),
    "Gaussien sigma=2":  lambda x: cv2.GaussianBlur(x, (9,9), 2),
    "Median k=5":    lambda x: cv2.medianBlur(x, 5),
    "Bilateral":     lambda x: cv2.bilateralFilter(x, 9, 75, 75),
}

# Calculer PSNR et SSIM pour chaque combinaison
results = {}
for noise_name, noisy_img in noisy_dict.items():
    results[noise_name] = {}
    for filter_name, filter_fn in filters_dict.items():
        denoised = filter_fn(noisy_img)
        p = psnr(BASE_IMG, denoised, data_range=255)
        s = ssim(BASE_IMG, denoised, channel_axis=2, data_range=255)
        results[noise_name][filter_name] = {"psnr": p, "ssim": s}

# Afficher le tableau et le meilleur filtre par bruit
print(f"{'':25} {'Moyen':>14} {'Gaussien':>14} {'Median':>14} {'Bilateral':>14}")
print("-" * 82)
for noise_name in results:
    psnr_vals = [results[noise_name][f]["psnr"] for f in filters_dict]
    best_idx  = np.argmax(psnr_vals)
    print(f"{noise_name:25}", end="")
    for i, (fname, vals) in enumerate(results[noise_name].items()):
        marker = " *" if i == best_idx else "  "
        print(f"  {vals['psnr']:5.1f}dB{marker}", end="")
    print()

# ============================================================
# EXERCICE 5 — Non-Local Means
# ============================================================
print("=" * 60)
print("EXERCICE 5 — Non-Local Means")
print("=" * 60)

# Estimation de sigma du bruit
# D'abord essayer avec skimage, sinon méthode simple
try:
    from skimage.restoration import estimate_sigma
    # IMPORTANT: estimate_sigma attend une image normalisée entre 0 et 1
    img_normalized = img_gauss.astype(np.float32) / 255.0
    sigma_est = estimate_sigma(img_normalized, channel_axis=-1, average_sigmas=True)
    print(f"Sigma estimé (skimage): {round(sigma_est * 255, 2)}")
except ImportError:
    # Fallback: estimation simple basée sur la variance locale
    def estimate_sigma_simple(img, channel_axis=-1):
        """Estime le sigma du bruit gaussien."""
        if channel_axis == -1 and len(img.shape) == 3:
            gray = np.mean(img, axis=2)
        else:
            gray = img
        sigma = np.std(gray) / 255.0 * 0.5
        return sigma
    sigma_est = estimate_sigma_simple(img_gauss.astype(np.float32) / 255.0)
    print(f"Sigma estimé (simple): {round(sigma_est * 255, 2)}")

# Tester différents facteurs h
h_factors  = [0.6, 0.8, 1.0, 1.2, 1.5, 2.0]
results_nlm = []

for hf in h_factors:
    try:
        # Utiliser NLM avec le sigma estimé une seule fois
        denoised = denoise_nl_means(
            img_gauss.astype(np.float32) / 255.0,
            h=hf * sigma_est,
            fast_mode=True,
            patch_size=5,
            patch_distance=6,
            channel_axis=-1
        )
        denoised_u8 = (denoised * 255).clip(0, 255).astype(np.uint8)
        p = psnr(BASE_IMG, denoised_u8, data_range=255)
        results_nlm.append((hf, denoised_u8, p))
        print(f"  h = {hf:.1f} x sigma_est -> PSNR = {p:.2f} dB")
    except Exception as e:
        # Alternative avec filtre gaussien
        sigma_blur = hf * 2
        denoised = cv2.GaussianBlur(img_gauss, (9, 9), sigma_blur)
        p = psnr(BASE_IMG, denoised, data_range=255)
        results_nlm.append((hf, denoised, p))
        print(f"  h = {hf:.1f} -> Gaussian sigma={sigma_blur:.1f} -> PSNR = {p:.2f} dB (fallback)")

# Afficher les 6 résultats + courbe PSNR vs h
fig, axes = plt.subplots(2, 6, figsize=(24, 8))
for i, (hf, img_d, p) in enumerate(results_nlm):
    axes[0, i].imshow(img_d); axes[0, i].set_title("h=%.1f*s | PSNR=%.1fdB" % (hf, p), fontsize=9)
    axes[0, i].axis("off")
axes[1, 0].plot([r[0] for r in results_nlm], [r[2] for r in results_nlm],
                "o-", color=BLUE, linewidth=2, markersize=8)
axes[1, 0].set_xlabel("Facteur h / sigma_est")
axes[1, 0].set_ylabel("PSNR (dB)")
axes[1, 0].set_title("PSNR vs force de débruitage NLM")
axes[1, 0].grid(True, alpha=0.3)
for ax in axes[1, 1:]: ax.set_visible(False)
plt.suptitle("Exercice 5 — Non-Local Means", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.show()

# ============================================================
# RÉSUMÉ DES SOLUTIONS
# ============================================================
print("=" * 60)
print("RÉSUMÉ DES SOLUTIONS")
print("=" * 60)
print("""
Exercice 1 — Sélection HSV :
  - Conversion en HSV avec cv2.cvtColor
  - Masque rouge avec deux plages (H~0 et H~179)
  - Application du masque sur l'image

Exercice 2 — Égalisation manuelle :
  - Calcul histogramme avec np.histogram
  - CDF avec cumsum()
  - Normalisation et application via mapping

Exercice 3 — CLAHE :
  - Test grid avec clip_limit et tile_size
  - Meilleur compromis : clip=2.0, tile=(8,8)

Exercice 4 — Débruitage :
  -Gaussien : Bilatéral ou Gaussien
  -Sel & Poivre : Médian
  -Speckle : Bilatéral

Exercice 5 — NLM :
  - Facteur h optimal autour de 1.0 × sigma_est
  - Trop fort = perte de détails
  - Trop faible = bruit résiduel
""")
