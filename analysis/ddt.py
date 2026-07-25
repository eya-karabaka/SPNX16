"""
ddt.py — Difference Distribution Table de la S-Box SPNX-16
===========================================================
La DDT mesure la non-linéarité de la S-Box en analysant
comment les différences en entrée se propagent en sortie.

Pour chaque paire de différences (delta_x, delta_y) :
    DDT[delta_x][delta_y] = nombre de valeurs x telles que
    SBOX[x] XOR SBOX[x XOR delta_x] == delta_y

Une S-Box parfaite : toutes les valeurs de la DDT (hors DDT[0][0])
sont faibles et uniformément distribuées.
Valeur maximale idéale pour une S-Box 4 bits : 4 (sur 16 possibilités).
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.sbox import SBOX


def calculer_ddt() -> list:
    """
    Calcule la Difference Distribution Table (DDT) de la S-Box et la construit.

    Returns:
        liste 16x16 — DDT[delta_x][delta_y] = nombre de solutions
    """
    # Initialiser la table 16x16 à zéro
    ddt = [[0] * 16 for _ in range(16)]

    for delta_x in range(16):
        for x in range(16):
            # x' = x XOR delta_x
            x_prime   = x ^ delta_x
            # différence en sortie
            delta_y   = SBOX[x] ^ SBOX[x_prime]
            ddt[delta_x][delta_y] += 1

    return ddt


def valeur_max_ddt(ddt: list) -> int:
    """
    Retourne la valeur maximale de la DDT (hors DDT[0][0]).
    Plus cette valeur est basse, meilleure est la S-Box.

    Args:
        ddt : liste 16x16 — la DDT calculée

    Returns:
        int — valeur maximale hors case (0,0)
    """
    maximum = 0
    for delta_x in range(16):
        for delta_y in range(16):
            if delta_x == 0 and delta_y == 0:
                continue  # case triviale ignorée
            if ddt[delta_x][delta_y] > maximum:
                maximum = ddt[delta_x][delta_y]
    return maximum


def afficher_ddt(ddt: list) -> None:
    """
    Affiche la DDT sous forme de tableau lisible dans le terminal.

    Args:
        ddt : liste 16x16 — la DDT calculée
    """
    print("\n  DDT (lignes = delta_x, colonnes = delta_y) :")
    print("       " + "  ".join(f"{j:2X}" for j in range(16)))
    print("     " + "─" * 50)
    for i in range(16):
        ligne = f"  {i:2X} │ "
        for j in range(16):
            val = ddt[i][j]
            # Mettre en évidence les valeurs élevées
            if i == 0 and j == 0:
                ligne += " *"   # case triviale
            elif val == 0:
                ligne += "  "
            elif val >= 8:
                ligne += f"!{val}"  # valeur élevée = faiblesse
            else:
                ligne += f" {val}"
        print(ligne)


def rapport_ddt() -> None:
    """
    Affiche un rapport complet sur la DDT de la S-Box SPNX-16.
    """
    print("=" * 55)
    print("     RAPPORT DDT (S-Box) — SPNX-16")
    print("=" * 55)

    ddt    = calculer_ddt()
    valmax = valeur_max_ddt(ddt)

    print(f"\n  S-Box analysée : {[hex(x) for x in SBOX]}")
    print(f"\n  Valeur max DDT (hors [0][0]) : {valmax}")
    print(f"  Valeur idéale pour 4 bits    : 4")

    if valmax <= 4:
        print("  Évaluation : ✅ Excellente non-linéarité")
    elif valmax <= 6:
        print("  Évaluation : ⚠️  Non-linéarité acceptable")
    else:
        print("  Évaluation : ❌ S-Box faible — à revoir")

    afficher_ddt(ddt)

    # Vérification que DDT[0][0] == 16 (propriété mathématique garantie)
    print(f"\n  DDT[0][0] = {ddt[0][0]} (doit toujours valoir 16) : "
          f"{'✅' if ddt[0][0] == 16 else '❌'}")
    print("=" * 55)


if __name__ == "__main__":
    rapport_ddt()