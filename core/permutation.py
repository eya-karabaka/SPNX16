"""
permutation.py — Table de Permutation de SPNX-16
=================================================
La permutation réorganise les 8 bits du bloc sans modifier leurs valeurs.
Son rôle : la DIFFUSION — après permutation, chaque nibble de sortie
contient des bits issus des deux nibbles d'entrée.
Sans elle, les deux nibbles resteraient indépendants d'un round à l'autre.

Appliquée uniquement aux rounds 1, 2 et 3 (pas au round final).
"""

# ─── Table de permutation ─────────────────────────────────────────────────────
# Lecture : le bit à la position X en entrée va à la position Y en sortie
# Exemple : bit[1] → position 2, bit[2] → position 7, etc.
#
# Position entrée = indice : 0  1  2  3  4  5  6  7
# Position sortie = valeur : 6  2  7  1  3  0  4  5
# Exemple : Le bit qui est à la position 0 , va aller à la position 6.

PERM = [6, 2, 7, 1, 3, 0, 4, 5]

# ─── Table inverse (générée automatiquement) ─────────────────────────────────
# Si PERM[x] = y, alors INV_PERM[y] = x
# Utilisée au déchiffrement pour inverser la permutation
# enumerate() renvoie un itérateur qui produit des couples : (index, valeur)

INV_PERM = [0] * 8
for i, v in enumerate(PERM):
    INV_PERM[v] = i



def permuter(bloc: int, inverse: bool = False) -> int:
    """
    Applique la permutation (ou son inverse) sur un bloc de 8 bits.
    On peut écrire : permuter(120,True) pour demander la permutation inverse

    Args:
        bloc    : entier entre 0 et 255 (8 bits)
        inverse : si True, utilise INV_PERM (pour le déchiffrement)

    Returns:
        entier entre 0 et 255 — le bloc après permutation
    """
    table = INV_PERM if inverse else PERM
    # On prépare un entier vide (00000000) Puis on va y placer les bits
    resultat = 0


    for pos_entree in range(8):
        # Extraire le bit à la position pos_entree
        # Les bits sont numérotés de gauche à droite : pos 0 = bit le plus à gauche
        # Exemple : 
        #          10110110
        #         &
        #          00000001
        #         ----------
        #          00000000

        bit = (bloc >> (7 - pos_entree)) & 1

        # Placer ce bit à sa nouvelle position
        pos_sortie = table[pos_entree]
        resultat |= (bit << (7 - pos_sortie))

    return resultat


def verifier_permutation() -> bool:
    """
    Vérifie que la permutation est bijective :
    toutes les positions de sortie sont distinctes (0 à 7, une seule fois chacune).
    """
    return sorted(PERM) == list(range(8))


def rapport_permutation() -> None:
    """
    Affiche un rapport sur la table de permutation et son inverse.
    """
    print("=" * 45)
    print("     RAPPORT PERMUTATION — SPNX-16")
    print("=" * 45)

    print("\nTable PERM :")
    print("Entrée : " + " ".join(str(i) for i in range(8)))
    print("Sortie : " + " ".join(str(PERM[i]) for i in range(8)))

    print("\nTable INV_PERM :")
    print("Entrée : " + " ".join(str(i) for i in range(8)))
    print("Sortie : " + " ".join(str(INV_PERM[i]) for i in range(8)))

    print("\nVérifications :")
    print(f"   Bijective          : {verifier_permutation()}")

    coherent = all(permuter(permuter(b), inverse=True) == b for b in range(256))
    print(f"   Réversibilité OK   : {coherent}")

    # all(...) returns : True if every value is True.
    #                    False if at least one value is False. 
    print("=" * 45)


# ─── Test rapide si lancé directement ────────────────────────────────────────
# __name__ : a special built-in variable , Its value depends on how the file is executed.

if __name__ == "__main__":
    rapport_permutation()

    print("\nExemple concret :")
    bloc = 0b00000110        # = 0x06 
    # 0b tells Python This number is written in binary (base 2)
    permute  = permuter(bloc)
    retrouve = permuter(permute, inverse=True)

    # {bloc:08b} : displays 00000110 instead of 110
    print(f"  Bloc original  : {bloc:08b}")
    print(f"  Après PERM     : {permute:08b}")
    print(f"  Après INV_PERM : {retrouve:08b}")
    print(f"  Réversibilité  : {'✅ OK' if retrouve == bloc else '❌ ERREUR'}")