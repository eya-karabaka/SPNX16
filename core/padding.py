"""
padding.py — Gestion du Padding de SPNX-16
===========================================
Notre algorithme traite le message octet par octet (blocs de 8 bits).
Le padding garantit que chaque bloc est complet.

La Norme utilisée est inspirée par PKCS#7 
Règle : on ajoute toujours exactement 1 octet de valeur 0x01
        à la fin du message avant chiffrement.
        Au déchiffrement, on retire ce dernier octet.

Pourquoi toujours ajouter même si le message est "complet" ?
→ Sans ça, un message se terminant par l'octet 0x01 serait
  ambigu au déchiffrement (padding ou données réelles ?).
  En ajoutant systématiquement, l'ambiguïté disparaît.
"""

TAILLE_BLOC = 1  # 8 bits = 1 octet par bloc 
# Donc l'algorithme SPNX-16 travaille sur des octets, pas sur des caractères
# Exemple : 
#       "Café" n'est pas vu comme : C - a - f - é
#        mais comme : 43 (bloc1) 61 (bloc2) 66 (bloc3) C3 (bloc4) A9 (bloc5)
                
def ajouter_padding(message: bytes) -> bytes:
    """
    Ajoute le padding à un message avant chiffrement.

    Règle : ajoute toujours 1 octet de valeur 0x01 à la fin.

    Args:
        message : bytes — le message original en octets

    Returns:
        bytes — le message avec padding
    """
    return message + b'\x01'


def retirer_padding(message: bytes) -> bytes:
    """
    Retire le padding après déchiffrement.

    Règle : retire le dernier octet (qui doit être 0x01).
    Lève une erreur si le padding est invalide.

    Args:
        message : bytes — le message déchiffré avec padding

    Returns:
        bytes — le message original sans padding
    """
    if len(message) == 0:
        raise ValueError("Message vide : impossible de retirer le padding.")

    if message[-1] != 0x01:
        raise ValueError(
            f"Padding invalide : dernier octet = 0x{message[-1]:02X}, "
            f"attendu 0x01. Clé incorrecte ou message corrompu."
        )

    return message[:-1]


def message_vers_octets(message: str) -> bytes:
    """
    Convertit un message texte en séquence d'octets UTF-8.

    Args:
        message : str — le texte à chiffrer

    Returns:
        bytes — les octets correspondants
    """
    return message.encode('utf-8')


def octets_vers_message(octets: bytes) -> str:
    """
    Convertit une séquence d'octets en texte UTF-8.

    Args:
        octets : bytes — les octets à décoder

    Returns:
        str — le texte décodé
    """
    return octets.decode('utf-8')


def rapport_padding() -> None:
    """
    Affiche des exemples de padding sur différents messages.
    """
    print("=" * 45)
    print("      RAPPORT PADDING — SPNX-16")
    print("=" * 45)

    exemples = ["A", "AB", "Hello", "", "test\x01"]

    for msg in exemples:
        octets  = message_vers_octets(msg)
        padded  = ajouter_padding(octets)
        depadde = retirer_padding(padded)

        print(f"\n  Message    : {repr(msg)}")
        print(f"  Octets     : {list(octets)}")
        print(f"  Avec pad   : {list(padded)}")
        print(f"  Sans pad   : {list(depadde)}")
        ok = depadde == octets
        print(f"  Réversible : {'OK' if ok else 'ERREUR'}")

    print("\n" + "=" * 45)


# ─── Test rapide si lancé directement ────────────────────────────────────────
if __name__ == "__main__":
    rapport_padding()