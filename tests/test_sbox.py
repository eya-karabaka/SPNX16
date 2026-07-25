"""
test_sbox.py — Tests unitaires de la S-Box SPNX-16
===================================================
Vérifie toutes les propriétés cryptographiques
attendues de la S-Box avant de continuer.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.sbox import (SBOX, INV_SBOX, substituer, substituer_bloc,
                        verifier_bijectivite, verifier_absence_point_fixe,
                        verifier_absence_point_fixe_oppose)

# ─── Compteurs ────────────────────────────────────────────────────────────────
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

# ─── Tests ───────────────────────────────────────────────────────────────────
print("=" * 50)
print("     TESTS S-BOX — SPNX-16")
print("=" * 50)

print("\n[1] Propriétés structurelles")
check("SBOX contient 16 éléments",     len(SBOX) == 16)
check("INV_SBOX contient 16 éléments", len(INV_SBOX) == 16)
check("Bijectivité",                    verifier_bijectivite())
check("Absence de point fixe",         verifier_absence_point_fixe())
check("Absence de point fixe opposé",  verifier_absence_point_fixe_oppose())

print("\n[2] Cohérence INV_SBOX")
check("INV_SBOX[SBOX[x]] == x pour tout x",
      all(INV_SBOX[SBOX[x]] == x for x in range(16)))
check("SBOX[INV_SBOX[x]] == x pour tout x",
      all(SBOX[INV_SBOX[x]] == x for x in range(16)))

print("\n[3] Toutes les valeurs sont des nibbles valides (0-15)")
check("SBOX     : toutes valeurs entre 0 et 15",
      all(0 <= v <= 15 for v in SBOX))
check("INV_SBOX : toutes valeurs entre 0 et 15",
      all(0 <= v <= 15 for v in INV_SBOX))

print("\n[4] Réversibilité sur les 256 octets possibles")
check("substituer_bloc(substituer_bloc(b), inverse=True) == b pour tout b",
      all(substituer_bloc(substituer_bloc(b), inverse=True) == b
          for b in range(256)))

print("\n[5] Cas particuliers")
check("substituer(0)  != 0",          substituer(0)  != 0)
check("substituer(15) != 15",         substituer(15) != 15)
check("substituer_bloc(0x00) != 0x00", substituer_bloc(0x00) != 0x00)
check("substituer_bloc(0xFF) != 0xFF", substituer_bloc(0xFF) != 0xFF)

# ─── Résumé ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print(f"  Résultat : {tests_ok} OK  |  {tests_ko} ÉCHEC")
if tests_ko == 0:
    print("  🎉 Tous les tests S-Box sont passés !")
else:
    print("  ⚠️  Des tests ont échoué — vérifiez la S-Box.")
print("=" * 50)