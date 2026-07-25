"""
avalanche.py — Mesure de l'Effet Avalanche SPNX-16
===================================================
Mesure statistiquement combien de bits changent dans
le chiffré quand on modifie 1 seul bit du message clair.

Critère de succès : moyenne proche de 50% (entre 40% et 60%).
"""

import sys, os, random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.cipher import chiffrer


def compter_bits_differents(b1: bytes, b2: bytes) -> int:
    """
    Compte le nombre de bits différents entre deux séquences d'octets.
    Utilise XOR : les bits à 1 dans le résultat = bits différents.

    Args:
        b1, b2 : deux séquences d'octets de même longueur

    Returns:
        int — nombre de bits différents
    """
    total = 0
    for x, y in zip(b1, b2):
        diff = x ^ y
        while diff:
            total += diff & 1
            diff >>= 1
    return total


def mesurer_avalanche_complet(nb_essais: int = 2000,
                               seed: int = 42) -> dict:
    """
    Mesure l'effet avalanche sur nb_essais cas aléatoires.

    Pour chaque essai :
        1. Génère un message aléatoire et une clé aléatoire
        2. Modifie 1 bit aléatoire du premier octet du message
        3. Chiffre les deux versions
        4. Compte les bits différents dans les sorties

    Args:
        nb_essais : nombre de mesures à effectuer
        seed      : graine aléatoire pour reproductibilité

    Returns:
        dict avec les clés :
            - 'pourcentages'  : liste des pourcentages par essai
            - 'moyenne'       : moyenne globale
            - 'minimum'       : valeur minimale observée
            - 'maximum'       : valeur maximale observée
            - 'nb_essais'     : nombre d'essais effectués
    """
    random.seed(seed)
    pourcentages = []

    for _ in range(nb_essais):
        # Message d'un seul caractère pour mesurer précisément sur 1 bloc
        octet_original = random.randint(32, 126)
        msg_original   = chr(octet_original)
        cle            = random.randint(0, 0xFFFF)

        # Modifier 1 bit aléatoire
        bit            = random.randint(0, 7)
        octet_modifie  = octet_original ^ (1 << bit)
        msg_modifie    = chr(octet_modifie)

        # Chiffrer et comparer
        c1         = chiffrer(msg_original, cle)
        c2         = chiffrer(msg_modifie,  cle)
        bits_diff  = compter_bits_differents(c1, c2)
        total_bits = len(c1) * 8

        pourcentages.append((bits_diff / total_bits) * 100)

    return {
        'pourcentages' : pourcentages,
        'moyenne'      : sum(pourcentages) / len(pourcentages),
        'minimum'      : min(pourcentages),
        'maximum'      : max(pourcentages),
        'nb_essais'    : nb_essais,
    }


def mesurer_avalanche_par_bit(message: str,
                               cle: int) -> list:
    """
    Mesure l'effet avalanche pour chaque bit du premier octet du message.

    Utile pour visualiser bit par bit l'impact d'une modification.

    Args:
        message : str — message de référence
        cle     : int — clé de 16 bits

    Returns:
        liste de 8 dicts avec 'bit', 'bits_differents', 'pourcentage'
    """
    resultats = []
    c_original = chiffrer(message, cle)

    for bit in range(8):
        # Modifier le bit dans le premier caractère du message
        octet_modifie = ord(message[0]) ^ (1 << bit)
        msg_modifie   = chr(octet_modifie) + message[1:]

        c_modifie  = chiffrer(msg_modifie, cle)
        bits_diff  = compter_bits_differents(c_original, c_modifie)
        total_bits = len(c_original) * 8

        resultats.append({
            'bit'             : bit,
            'bits_differents' : bits_diff,
            'total_bits'      : total_bits,
            'pourcentage'     : (bits_diff / total_bits) * 100,
        })

    return resultats


# ─── Affichage si lancé directement ──────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("   ANALYSE AVALANCHE — SPNX-16")
    print("=" * 50)

    print("\nMesure en cours sur 2000 essais...")
    stats = mesurer_avalanche_complet(2000)

    print(f"\n  Nombre d'essais : {stats['nb_essais']}")
    print(f"  Moyenne         : {stats['moyenne']:.2f}%")
    print(f"  Minimum         : {stats['minimum']:.2f}%")
    print(f"  Maximum         : {stats['maximum']:.2f}%")
    print(f"  Cible           : 40% — 60%")

    ok = 40.0 <= stats['moyenne'] <= 60.0
    print(f"\n  Critère 50%     : {'✅ RESPECTÉ' if ok else '❌ NON RESPECTÉ'}")

    print("\n─── Analyse bit par bit (message='A', clé=0xABCD) ───")
    resultats = mesurer_avalanche_par_bit("A", 0xABCD)
    for r in resultats:
        barre = "█" * int(r['pourcentage'] / 10)
        print(f"  Bit {r['bit']} : {r['pourcentage']:5.1f}%  {barre}")

    print("=" * 50)