"""
test_avalanche.py — Test d'effet avalanche SPNX-16
===================================================
Vérifie que modifier 1 bit du message en entrée
modifie environ 50% des bits du message chiffré.
Cible : entre 40% et 60% de bits modifiés en moyenne.
"""

import sys, os, random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.cipher import chiffrer

tests_ok = 0
tests_ko = 0

def check(nom: str, condition: bool) -> None:
    global tests_ok, tests_ko
    if condition:
        print(f"  ✅ {nom}")
        tests_ok += 1
    else:
        print(f"  ❌ {nom}")
        tests_ko += 1


def compter_bits_differents(b1: bytes, b2: bytes) -> int:
    """Compte le nombre de bits différents entre deux séquences d'octets."""
    total = 0
    for x, y in zip(b1, b2):
        diff = x ^ y          # XOR : bits à 1 = bits différents
        while diff:
            total += diff & 1  # compter les bits à 1
            diff >>= 1
    return total


def mesurer_avalanche(nb_essais: int = 1000) -> float:
    """
    Mesure l'effet avalanche sur nb_essais cas aléatoires.
    Pour chaque essai : chiffre M et M' (1 bit modifié), compare les sorties.

    Returns:
        float — pourcentage moyen de bits modifiés (0.0 à 100.0)
    """
    random.seed(42) # Pour avoir toujours les mêmes tests aléatoires.
    total_bits_modifies = 0
    total_bits          = 0

    for _ in range(nb_essais):
        # Message aléatoire d'un seul caractère (1 bloc = 8 bits)
        octet_original = random.randint(32, 126)
        msg_original   = chr(octet_original)
        cle            = random.randint(0, 0xFFFF)

        # Modifier 1 bit aléatoire dans l'octet
        bit_a_modifier = random.randint(0, 7)
        octet_modifie  = octet_original ^ (1 << bit_a_modifier)
        msg_modifie    = chr(octet_modifie)

        # Chiffrer les deux messages
        c1 = chiffrer(msg_original, cle)
        c2 = chiffrer(msg_modifie,  cle)

        # Compter les bits différents
        bits_diff      = compter_bits_differents(c1, c2)
        total_bits_modifies += bits_diff
        total_bits          += len(c1) * 8

    return (total_bits_modifies / total_bits) * 100


print("=" * 50)
print("   TESTS EFFET AVALANCHE — SPNX-16")
print("=" * 50)

print("\n[1] Mesure sur 1000 essais aléatoires")
pourcentage = mesurer_avalanche(1000)
print(f"\n  Pourcentage moyen de bits modifiés : {pourcentage:.2f}%")
print(f"  Cible : entre 40% et 60%")

check("Effet avalanche ≥ 40%", pourcentage >= 40.0)
check("Effet avalanche ≤ 60%", pourcentage <= 60.0)
check("Effet avalanche proche de 50% (±15%)", abs(pourcentage - 50.0) <= 15.0)

print("\n[2] Cas fixes — modifier chaque bit du message")
msg = "A"
cle = 0xABCD
print(f"\n  Message de référence : '{msg}' (0x{ord(msg):02X})")
for bit in range(8):
    msg_modifie = chr(ord(msg) ^ (1 << bit))
    c1 = chiffrer(msg, cle)
    c2 = chiffrer(msg_modifie, cle)
    bits_diff = compter_bits_differents(c1, c2)
    total     = len(c1) * 8
    pct       = (bits_diff / total) * 100
    check(f"Bit {bit} modifié → {bits_diff}/{total} bits changés ({pct:.0f}%)",
          bits_diff > 0)

print("\n" + "=" * 50)
print(f"  Résultat : {tests_ok} OK  |  {tests_ko} ÉCHEC")
if tests_ko == 0:
    print("  🎉 Tous les tests d'avalanche sont passés !")
else:
    print("  ⚠️  Des tests ont échoué — revoir la S-Box ou la permutation.")
print("=" * 50)