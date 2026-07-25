"""
sbox.py — Boîte de Substitution (S-Box) de SPNX-16
====================================================
La S-Box est la primitive de non-linéarité de l'algorithme.
Elle remplace un nibble de 4 bits (valeur 0-15) par un autre nibble,
selon une table fixe et bijective.

Sans elle, tout l'algorithme serait linéaire (XOR + permutation),
attaquable par simple algèbre linéaire.
"""

# ─── S-Box principale ────────────────────────────────────────────────────────
# index = nibble entrant (0 à 15)
# valeur = nibble sortant (0 à 15)
SBOX = [0x6, 0xB, 0x9, 0x0, 0xC, 0xF, 0x5, 0xA,
        0x3, 0xE, 0x1, 0xD, 0x4, 0x7, 0x8, 0x2]

# ─── S-Box inverse (générée automatiquement) ─────────────────────────────────
# Si SBOX[x] = y, alors INV_SBOX[y] = x
# Utilisée au déchiffrement pour inverser la substitution
INV_SBOX = [0] * 16
for _i, _v in enumerate(SBOX):
    INV_SBOX[_v] = _i  # INV_SBOX[SBOX[x]] == x pour tout x


def substituer(nibble: int, inverse: bool = False) -> int:
    """
    Applique la S-Box (ou son inverse) à un nibble de 4 bits.

    Args:
        nibble  : entier entre 0 et 15 (4 bits)
        inverse : si True, utilise INV_SBOX (pour le déchiffrement)

    Returns:
        entier entre 0 et 15 — le nibble substitué
    """
    # Sécurité : on s'assure que l'entrée est bien un nibble valide
    if not (0 <= nibble <= 15):
        raise ValueError(f"Nibble invalide : {nibble}. Doit être entre 0 et 15.")

    if inverse:
        return INV_SBOX[nibble]
    return SBOX[nibble]


def substituer_bloc(bloc: int, inverse: bool = False) -> int:
    """
    Applique la S-Box en parallèle sur les deux nibbles d'un bloc de 8 bits.

    Le bloc est découpé en :
        - nibble HAUT : les 4 bits de gauche (bits 7 à 4)
        - nibble BAS  : les 4 bits de droite (bits 3 à 0)

    Chaque nibble est substitué indépendamment,
    puis les deux résultats sont réassemblés en un bloc de 8 bits.

    Args:
        bloc    : entier entre 0 et 255 (8 bits)
        inverse : si True, utilise INV_SBOX

    Returns:
        entier entre 0 et 255 — le bloc après substitution
    """
    # Extraction des deux nibbles
    nibble_haut = (bloc >> 4) & 0xF  # 4 bits de gauche
    nibble_bas  = bloc & 0xF          # 4 bits de droite

    # Substitution indépendante de chaque nibble
    haut_substitue = substituer(nibble_haut, inverse)
    bas_substitue  = substituer(nibble_bas,  inverse)

    # Réassemblage : nibble haut reprend sa place à gauche (décalage de 4)
    return (haut_substitue << 4) | bas_substitue


# ─── Fonctions de vérification ───────────────────────────────────────────────

def verifier_bijectivite() -> bool:
    """
    Vérifie que la S-Box est bijective :
    toutes les valeurs de sortie sont distinctes.
    Condition nécessaire pour que le déchiffrement soit possible.
    """
    return len(set(SBOX)) == 16


def verifier_absence_point_fixe() -> bool:
    """
    Vérifie qu'aucune entrée x ne satisfait SBOX[x] == x.
    Un point fixe est une faiblesse statistique : x reste inchangé.
    """
    return all(SBOX[x] != x for x in range(16))


def verifier_absence_point_fixe_oppose() -> bool:
    """
    Vérifie qu'aucune entrée x ne satisfait SBOX[x] == (~x & 0xF).
    (~x & 0xF) = complément à 1 sur 4 bits (tous les bits inversés).
    Cette propriété évite une corrélation directe entrée/sortie.
    """
    return all(SBOX[x] != (~x & 0xF) for x in range(16))


def rapport_sbox() -> None:
    """
    Affiche un rapport complet sur les propriétés de la S-Box.
    Utile pour vérifier rapidement que tout est correct.
    """
    print("=" * 45)
    print("        RAPPORT S-BOX — SPNX-16")
    print("=" * 45)

    # Affichage de la table
    print("\nTable S-Box :")
    print("Entrée  : " + " ".join(f"{i:2X}" for i in range(16)))
    print("Sortie  : " + " ".join(f"{SBOX[i]:2X}" for i in range(16)))

    print("\nTable S-Box Inverse :")
    print("Entrée  : " + " ".join(f"{i:2X}" for i in range(16)))
    print("Sortie  : " + " ".join(f"{INV_SBOX[i]:2X}" for i in range(16)))

    # Vérifications
    print("\nVérifications :")
    print(f"  ✅ Bijectivité          : {verifier_bijectivite()}")
    print(f"  ✅ Absence point fixe   : {verifier_absence_point_fixe()}")
    print(f"  ✅ Absence PF opposé    : {verifier_absence_point_fixe_oppose()}")

    # Test de cohérence INV_SBOX
    coherent = all(INV_SBOX[SBOX[x]] == x for x in range(16))
    print(f"  ✅ INV_SBOX cohérente   : {coherent}")

    print("=" * 45)


# ─── Test rapide si lancé directement ────────────────────────────────────────
if __name__ == "__main__":
    rapport_sbox()

    # Exemple concret
    print("\nExemple concret :")
    bloc_original = 0b11101010   # = 0xEA = 234
    bloc_chiffre  = substituer_bloc(bloc_original)
    bloc_retrouve = substituer_bloc(bloc_chiffre, inverse=True)

    print(f"  Bloc original  : {bloc_original:08b} (0x{bloc_original:02X})")
    print(f"  Après S-Box    : {bloc_chiffre:08b} (0x{bloc_chiffre:02X})")
    print(f"  Après INV_SBOX : {bloc_retrouve:08b} (0x{bloc_retrouve:02X})")
    print(f"  Réversibilité  : {'✅ OK' if bloc_retrouve == bloc_original else '❌ ERREUR'}")
