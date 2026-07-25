"""
main.py — Point d'entrée principal de SPNX-16
==============================================
Lance l'interface graphique Tkinter.
À exécuter depuis le dossier spnx16/ :
    python main.py

# Tkinter est la bibliothèque Python qui permet de créer
# l'interface graphique : fenêtres, boutons, zones de texte,
# onglets et barres de progression.
# Elle est incluse nativement dans Python — aucune installation requise
"""

import sys, os

# S'assurer que le dossier racine est dans le path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# __file__ contient le chemin du fichier actuellement exécuté.

from gui.app import SPNX16App


def main():
    print("=" * 50)
    print("     SPNX-16 — Démarrage")
    print("     Substitution–Permutation Network eXtended")
    print("=" * 50)

    # Vérification rapide des modules avant de lancer la GUI
    print("\n  Vérification des modules...")

    try:
        from core.sbox         import verifier_bijectivite
        from core.cipher       import chiffrer, dechiffrer

        # Test de réversibilité express
        test_msg = "SPNX16"
        test_cle = 0xABCD
        assert dechiffrer(chiffrer(test_msg, test_cle), test_cle) == test_msg
        assert verifier_bijectivite()

        print("  ✅ core/sbox.py        OK")
        print("  ✅ core/permutation.py OK")
        print("  ✅ core/key_schedule.py OK")
        print("  ✅ core/cipher.py      OK")
        print("  ✅ core/padding.py     OK")
        print("  ✅ Réversibilité       OK")

    except Exception as e:
        print(f"  ❌ Erreur dans les modules core : {e}")
        print("     Vérifiez vos fichiers avant de continuer.")
        sys.exit(1)

    try:
        import matplotlib
        print("  ✅ matplotlib          OK")
    except ImportError:
        print("  ⚠️  matplotlib absent  — graphiques désactivés")
        print("      Installez avec : pip install matplotlib numpy")

    print("\n  Lancement de l'interface graphique...\n")

    app = SPNX16App()
    app.mainloop()


if __name__ == "__main__":
    main()