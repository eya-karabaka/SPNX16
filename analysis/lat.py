"""
lat.py — Linear Approximation Table de la S-Box SPNX-16
=========================================================
La LAT mesure la non-linéarité de la S-Box en analysant
si des combinaisons linéaires de bits d'entrée corrèlent
avec des combinaisons linéaires de bits de sortie.

Pour chaque paire de masques (a, b) :
LAT[a][b] = (nombre de x tel que parité(a·x) == parité(b·SBOX[x])) - 8

Où parité(v) = XOR de tous les bits de v (popcount(v) % 2).
Le -8 centre le biais sur 0 : une S-Box parfaitement linéaire
donnerait un biais de +8 ou -8, une S-Box idéale reste proche de 0.

Une S-Box parfaite : tous les biais (hors LAT[0][0]) sont faibles
et uniformément répartis. Valeur maximale idéale pour une S-Box 4 bits : 4.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.sbox import SBOX


def parite(valeur: int) -> int:
    """
    Calcule la parité d'un entier : XOR de tous ses bits.
    Args:
        valeur : entier quelconque
    Returns:
        0 si le nombre de bits à 1 est pair, 1 sinon
    """
    return bin(valeur).count('1') % 2


def calculer_lat() -> list:
    """
    Calcule la Linear Approximation Table (LAT) de la S-Box.
    Returns:
        liste 16x16 — LAT[a][b] = biais centré sur 0 (entre -8 et +8)
    """
    lat = [[0] * 16 for _ in range(16)]

    for a in range(16):        # masque d'entrée
        for b in range(16):    # masque de sortie
            compteur = 0
            for x in range(16):
                y = SBOX[x]
                bit_entree = parite(a & x)
                bit_sortie = parite(b & y)
                if bit_entree == bit_sortie:
                    compteur += 1
            # Biais centré : 8 = équilibre parfait (aucune corrélation)
            lat[a][b] = compteur - 8

    return lat


def valeur_max_lat(lat: list) -> int:
    """
    Retourne le biais absolu maximal de la LAT (hors LAT[0][0]).
    Plus cette valeur est basse, meilleure est la S-Box.
    Args:
        lat : liste 16x16 — la LAT calculée
    Returns:
        int — biais absolu maximal hors case (0,0)
    """
    maximum = 0
    for a in range(16):
        for b in range(16):
            if a == 0 and b == 0:
                continue  # case triviale ignorée (biais toujours = 8)
            if abs(lat[a][b]) > maximum:
                maximum = abs(lat[a][b])
    return maximum


def afficher_lat(lat: list) -> None:
    """
    Affiche la LAT sous forme de tableau lisible dans le terminal.
    Args:
        lat : liste 16x16 — la LAT calculée
    """
    print("\n LAT (lignes = masque a, colonnes = masque b) :")
    print("      " + " ".join(f"{j:3X}" for j in range(16)))
    print("      " + "─" * 68)
    for i in range(16):
        ligne = f"  {i:2X} │ "
        for j in range(16):
            val = lat[i][j]
            if i == 0 and j == 0:
                ligne += "  * "
            elif val == 0:
                ligne += "  . "
            elif abs(val) >= 6:
                ligne += f"!{val:+d} "  # biais élevé = faiblesse
            else:
                ligne += f" {val:+d} "
        print(ligne)


def rapport_lat() -> None:
    """
    Affiche un rapport complet sur la LAT de la S-Box SPNX-16.
    """
    print("=" * 55)
    print(" RAPPORT LAT (S-Box) — SPNX-16")
    print("=" * 55)

    lat = calculer_lat()
    valmax = valeur_max_lat(lat)

    print(f"\n S-Box analysée : {[hex(x) for x in SBOX]}")
    print(f"\n Biais max LAT (hors [0][0]) : {valmax}")
    print(f" Valeur idéale pour 4 bits   : 4")

    if valmax <= 4:
        print(" Évaluation : ✅ Excellente résistance à la cryptanalyse linéaire")
    elif valmax <= 6:
        print(" Évaluation : ⚠️ Résistance acceptable")
    else:
        print(" Évaluation : ❌ S-Box vulnérable — à revoir")

    afficher_lat(lat)

    # Vérification que LAT[0][0] == 8 (propriété mathématique garantie)
    print(f"\n LAT[0][0] = {lat[0][0]} (doit toujours valoir 8) : "
          f"{'✅' if lat[0][0] == 8 else '❌'}")
    print("=" * 55)


if __name__ == "__main__":
    rapport_lat()