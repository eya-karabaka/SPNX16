"""
plots.py — Visualisations Graphiques SPNX-16
============================================
Génère les graphiques d'analyse de sécurité :
    - Histogramme de l'effet avalanche
    - Heatmap de la DDT de la S-Box
    - Graphique bit par bit de l'avalanche
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False
    print("⚠️  matplotlib non installé. Lancez : pip install matplotlib")

from analysis.avalanche import (mesurer_avalanche_complet,
                                 mesurer_avalanche_par_bit)
from analysis.ddt       import calculer_ddt
from analysis.lat import calculer_lat, valeur_max_lat


def graphique_avalanche(nb_essais: int = 2000) -> None:
    """
    Affiche un histogramme de la distribution de l'effet avalanche.

    Args:
        nb_essais : nombre de mesures pour la statistique
    """
    if not MATPLOTLIB_OK:
        return

    print(f"Calcul de l'avalanche sur {nb_essais} essais...")
    stats = mesurer_avalanche_complet(nb_essais)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Histogramme des pourcentages
    ax.hist(stats['pourcentages'],
            bins=20,
            color='#2E75B6',
            edgecolor='white',
            alpha=0.85,
            label='Distribution des essais')

    # Ligne de référence à 50%
    ax.axvline(x=50, color='#C0392B', linewidth=2,
               linestyle='--', label='Cible : 50%')

    # Ligne de la moyenne observée
    ax.axvline(x=stats['moyenne'], color='#1E8449', linewidth=2,
               linestyle='-', label=f"Moyenne : {stats['moyenne']:.1f}%")

    # Zone acceptable (40%-60%)
    ax.axvspan(40, 60, alpha=0.1, color='green', label='Zone acceptable (40%-60%)')

    ax.set_title("SPNX-16 — Distribution de l'Effet Avalanche",
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("% de bits modifiés dans le chiffré", fontsize=12)
    ax.set_ylabel("Nombre d'essais", fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    # Annotation statistiques
    info = (f"Essais : {stats['nb_essais']}\n"
            f"Moyenne : {stats['moyenne']:.1f}%\n"
            f"Min : {stats['minimum']:.1f}%\n"
            f"Max : {stats['maximum']:.1f}%")
    ax.text(0.02, 0.97, info,
            transform=ax.transAxes,
            verticalalignment='top',
            fontsize=9,
            bbox=dict(boxstyle='round', facecolor='#D5E8F0', alpha=0.8))

    plt.tight_layout()
    plt.savefig("rapport/avalanche_histogram.png", dpi=150)
    print("✅ Graphique sauvegardé : rapport/avalanche_histogram.png")
    plt.show()


def graphique_avalanche_par_bit(message: str = "A",
                                 cle: int = 0xABCD) -> None:
    """
    Affiche un graphique en barres de l'effet avalanche bit par bit.

    Args:
        message : message de référence (1 caractère recommandé)
        cle     : clé de 16 bits
    """
    if not MATPLOTLIB_OK:
        return

    resultats = mesurer_avalanche_par_bit(message, cle)
    bits      = [r['bit'] for r in resultats]
    pcts      = [r['pourcentage'] for r in resultats]

    fig, ax = plt.subplots(figsize=(9, 5))

    couleurs = ['#2E75B6' if 40 <= p <= 60 else '#C0392B' for p in pcts]
    barres   = ax.bar(bits, pcts, color=couleurs,
                      edgecolor='white', width=0.6)

    # Ligne de référence 50%
    ax.axhline(y=50, color='#C0392B', linewidth=1.5,
               linestyle='--', label='Cible : 50%')
    ax.axhspan(40, 60, alpha=0.1, color='green',
               label='Zone acceptable')

    # Valeurs au-dessus des barres
    for barre, pct in zip(barres, pcts):
        ax.text(barre.get_x() + barre.get_width() / 2,
                barre.get_height() + 1,
                f"{pct:.0f}%",
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_title(f"SPNX-16 — Avalanche bit par bit\n"
                 f"Message='{message}' | Clé=0x{cle:04X}",
                 fontsize=13, fontweight='bold')
    ax.set_xlabel("Bit modifié dans le message", fontsize=11)
    ax.set_ylabel("% de bits modifiés dans le chiffré", fontsize=11)
    ax.set_xticks(bits)
    ax.set_ylim(0, 110)
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig("rapport/avalanche_par_bit.png", dpi=150)
    print("✅ Graphique sauvegardé : rapport/avalanche_par_bit.png")
    plt.show()


def graphique_ddt() -> None:
    """
    Affiche une heatmap de la DDT de la S-Box SPNX-16.
    """
    if not MATPLOTLIB_OK:
        return

    ddt = calculer_ddt()

    # Convertir en liste 2D pour matplotlib
    import numpy as np
    data = np.array(ddt, dtype=float)
    # Masquer la case (0,0) pour ne pas écraser l'échelle
    data[0][0] = 0

    fig, ax = plt.subplots(figsize=(9, 7))

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "ddt", ["#FFFFFF", "#D5E8F0", "#2E75B6", "#C0392B"])
    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=8)

    # Annotations dans chaque cellule
    for i in range(16):
        for j in range(16):
            val = ddt[i][j]
            couleur_texte = "white" if val >= 6 else "black"
            ax.text(j, i, str(val) if val > 0 else "",
                    ha='center', va='center',
                    fontsize=8, color=couleur_texte)

    plt.colorbar(im, ax=ax, label="Nombre de solutions")
    ax.set_title("SPNX-16 — DDT de la S-Box\n"
                 "(Difference Distribution Table)",
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Différence de sortie (Δy)", fontsize=11)
    ax.set_ylabel("Différence d'entrée (Δx)", fontsize=11)
    ax.set_xticks(range(16))
    ax.set_yticks(range(16))
    ax.set_xticklabels([hex(i) for i in range(16)], fontsize=8)
    ax.set_yticklabels([hex(i) for i in range(16)], fontsize=8)

    plt.tight_layout()
    plt.savefig("rapport/ddt_heatmap.png", dpi=150)
    print("✅ Graphique sauvegardé : rapport/ddt_heatmap.png")
    plt.show()

def graphique_lat() -> None:
    """
    Affiche une heatmap de la LAT de la S-Box SPNX-16.
    """
    if not MATPLOTLIB_OK:
        return

    lat = calculer_lat()

    import numpy as np
    data = np.array(lat, dtype=float)
    data[0][0] = 0  # masquer la case triviale pour ne pas écraser l'échelle

    fig, ax = plt.subplots(figsize=(9, 7))
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "lat", ["#C0392B", "#D5E8F0", "#FFFFFF", "#D5E8F0", "#2E75B6"])
    im = ax.imshow(data, cmap=cmap, vmin=-8, vmax=8)

    for i in range(16):
        for j in range(16):
            val = lat[i][j]
            couleur_texte = "white" if abs(val) >= 6 else "black"
            ax.text(j, i, f"{val:+d}" if not (i == 0 and j == 0) else "",
                    ha='center', va='center',
                    fontsize=7, color=couleur_texte)

    plt.colorbar(im, ax=ax, label="Biais (parité entrée/sortie)")
    ax.set_title("SPNX-16 — LAT de la S-Box\n"
                  "(Linear Approximation Table)",
                  fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Masque de sortie (b)", fontsize=11)
    ax.set_ylabel("Masque d'entrée (a)", fontsize=11)
    ax.set_xticks(range(16))
    ax.set_yticks(range(16))
    ax.set_xticklabels([hex(i) for i in range(16)], fontsize=8)
    ax.set_yticklabels([hex(i) for i in range(16)], fontsize=8)

    plt.tight_layout()
    plt.savefig("rapport/lat_heatmap.png", dpi=150)
    print("✅ Graphique sauvegardé : rapport/lat_heatmap.png")
    plt.show()


def generer_tous_les_graphiques() -> None:
    """
    Génère et sauvegarde tous les graphiques d'analyse en une seule fois.
    """
    print("=" * 50)
    print("  GÉNÉRATION DES GRAPHIQUES — SPNX-16")
    print("=" * 50)

    print("\n[1] Histogramme effet avalanche...")
    graphique_avalanche(2000)

    print("\n[2] Avalanche bit par bit...")
    graphique_avalanche_par_bit("A", 0xABCD)

    print("\n[3] Heatmap DDT S-Box...")
    graphique_ddt()

    print("\n[4] Heatmap LAT S-Box...")
    graphique_lat()

    print("\n✅ Tous les graphiques ont été générés dans rapport/")


if __name__ == "__main__":
    generer_tous_les_graphiques()