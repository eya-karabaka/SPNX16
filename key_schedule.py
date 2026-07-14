"""
key_schedule.py — Générateur de Sous-Clés de SPNX-16
=====================================================
Produit 5 sous-clés de 8 bits (K1 à K5) à partir
de la clé principale de 16 bits, par rotations
circulaires gauches (RoL) successives.

Décalages utilisés :
    K1 : bits[0:8]  de la clé (pas de rotation)
    K2 : bits[8:16] de la clé (pas de rotation)
    K3 : RoL(clé, 3) → bits[0:8]
    K4 : RoL(clé, 6) → bits[0:8]
    K5 : RoL(clé, 9) → bits[0:8]
"""

# ─── Décalages de rotation pour chaque sous-clé ──────────────────────────────
DECALAGES = [0, 0, 3, 6, 9]
# K1 et K2 utilisent le même décalage (0) mais des moitiés différentes
# K3, K4, K5 : décalages non multiples → chaque sous-clé capture
# une fenêtre différente de la clé principale


def rol16(valeur: int, n: int) -> int:
    """
    Rotation circulaire gauche sur 16 bits.

    Les bits qui "sortent" à gauche réapparaissent à droite.
    Exemple avec n=3 : 1010 1011 1100 1101
                    →  0101 1110 0110 1101 (les 3 premiers bits passent à la fin)

    Args:
        valeur : entier 16 bits (0 à 65535)
        n      : nombre de positions à décaler vers la gauche

    Returns:
        entier 16 bits après rotation
    """
    n = n % 16  # Une rotation de 16 = aucun changement
    return ((valeur << n) | (valeur >> (16 - n))) & 0xFFFF

# valeur << n : Cela décale n bits vers la gauche Les nouvelles cases
# de droite sont remplies par des 0 ( ce n'est pas encore une rotation )
# valeur >> (16 - n) : récupération des n premiers bits ( en comptant à partir de la gauche)
# à travers 16-n bits décalages à droite . Les nouvelles cases
# de gauche sont remplies par des 0
# Le OU logique : pour fusionner les deux résultats issus des deux decalages
# Le masque : & 0xFFFF : un entier n'est pas limité à 16 bits , donc
# après un décalage à gauche, on peut obtenir plus de 16 bits. Ainsi on fait 
# ET logique entre le résultat fusionné et la valeur binaire 1111 1111 1111 1111
# Pourque tous les bits au-delà des 16 premiers sont supprimés (remplacés par des 0) 

def key_schedule(cle: int) -> list:
    """
    Génère les 5 sous-clés K1 à K5 depuis la clé principale.

    Args:
        cle : entier 16 bits (0 à 65535) — la clé principale

    Returns:
        liste de 5 entiers 8 bits [K1, K2, K3, K4, K5]
    """
    if not (0 <= cle <= 0xFFFF):
        raise ValueError(f"Clé invalide : {cle}. Doit être entre 0 et 65535 (16 bits).")

    sous_cles = []

    # K1 : 8 premiers bits de la clé originale (bits 15 à 8)
    sous_cles.append((cle >> 8) & 0xFF)
    # & 0xFF (vaut 1111 1111) : pour garder uniquement les 8 bits à droite

    # K2 : 8 derniers bits de la clé originale (bits 7 à 0)
    sous_cles.append(cle & 0xFF)

    # K3, K4, K5 : rotation puis extraction des 8 premiers bits
    for decalage in DECALAGES[2:]:       # c-à-d uniquement [3, 6, 9]
        cle_tournee = rol16(cle, decalage)
        sous_cles.append((cle_tournee >> 8) & 0xFF)
        # Car on ne veut récupérer que les 8 premiers bits

    return sous_cles  # [K1, K2, K3, K4, K5]


def rapport_key_schedule(cle: int) -> None:
    """
    Affiche le détail de la dérivation des sous-clés pour une clé donnée.

    Args:
        cle : entier 16 bits
    """
    print("=" * 50)
    print("     RAPPORT KEY SCHEDULE — SPNX-16")
    print("=" * 50)
    print(f"\nClé principale : {cle:016b} (0x{cle:04X})\n")

    # b → afficher en binaire , 016 → compléter avec des 0 pour avoir 16 caractères
    # X → hexadécimal majuscule, 04 → afficher 4 caractères

    sous_cles = key_schedule(cle) # exemple :  [171,205,94,230,177]
    noms      = ["K1", "K2", "K3", "K4", "K5"]
    details   = [
        "bits[0:8]  de la clé principale",
        "bits[8:16] de la clé principale",
        "RoL(clé, 3) -> bits[0:8]",
        "RoL(clé, 6) -> bits[0:8]",
        "RoL(clé, 9) -> bits[0:8]",
    ]

    for nom, sk, detail in zip(noms, sous_cles, details):
        print(f"  {nom} = {sk:08b}  (0x{sk:02X})  <- {detail}")

    print("\nVérifications :")
    # Déterminisme : deux appels donnent le même résultat
    coherent = key_schedule(cle) == key_schedule(cle)
    print(f"   Déterminisme        : {coherent}")
    # Toutes les sous-clés sont sur 8 bits
    valides = all(0 <= sk <= 0xFF for sk in sous_cles)
    print(f"   Sous-clés sur 8 bits: {valides}")
    print("=" * 50)


# ─── Test rapide si lancé directement ────────────────────────────────────────
if __name__ == "__main__":
    # Clé de l'exemple du briefing : 1010 1011 1100 1101
    cle_test = 0b1010101111001101   # = 0xABCD
    rapport_key_schedule(cle_test)