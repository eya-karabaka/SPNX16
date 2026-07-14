"""
padding.py — Gestion du Padding de SPNX-16
===========================================
- Le texte est encodé en UTF-8, donc
un caractère peut occuper plus qu'un octet:
            A → 41 (1 octet)
            é → C3 A9 (2 octets)
           😊 → F0 9F 98 8A (4 octets)

- Le chiffrement ne voit plus des caractères,
mais uniquement une suite d'octets.

- Mon projet ne met pas en œuvre la norme PKCS#7 complète. 
Il en utilise une version simplifiée.
     |
     |---> on ajoute toujours un seul octet 01.

( C'est une simplification choisie par le concepteur du projet )

- le 0x01, est ajouté 👉 Juste à la fin du message.

- Notre algorithme traite le message octet par octet (= 1 bloc)
- UTF-8 produit une suite d'octets. 
- L'algorithme SPNX-16 traite ensuite ces octets un par un
indépendamment du nombre de caractères du message.
- Le padding classique garantit que chaque bloc est complet.Il sert à dire :

"Je vais ajouter des octets artificiels pour compléter le dernier bloc." 
car sinon le chiffrement ne saurait pas quoi faire.

Norme utilisée est inspirée par : PKCS#7 qui indique exactement quels octets ajouter.

Fonctionnement classique du PKCS#7 classique : Si un bloc n'est pas rempli, on ajoute 
autant d'octets qu'il manque.

exemple :
    Bloc = 8 octets
    Message : HELLO
    Longueur : 5 octets
    Il manque : 3 octets
    PKCS#7 ajoute : 03 03 03
    Chaque octet vaut : 3
    Le bloc devient : H E L L O 03 03 03

Autre exemple : Le message contient exactement 8 octets :
    Bloc = 8 octets
    Message : ABCDEFGH (Le bloc est déjà complet)

- ! Or notre algorithme fonctionne avec des blocs de 1 octet 
 |
 |--> Il n'y a jamais de bloc incomplet.

Donc la règle classique de PKCS#7 ("ajouter les octets manquants") 
ne sert plus à rien.C'est pourquoi notre implémentation a été simplifiée,
Au lieu de calculer combien d'octets manquent, elle dit simplement :

 "Toujours ajouter un octet 0x01" ( 1 en héxadécimal)

Ainsi, avant chiffrement : A   B   C
Après padding : A   B   C   01

Le 01 est un nouveau bloc, puisqu'un bloc vaut un octet.
 

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
    - Ajoute le padding à un message avant chiffrement.
    - Règle : ajoute toujours 1 octet de valeur 0x01 à la fin.
    - Args: message : bytes = le message original en octets
    - Returns: bytes = le message avec padding
    - Le préfixe b signifie que c'est une chaîne d'octets (bytes) 
      et non une chaîne de caractères
    - b'\x01' représente un seul octet dont la valeur hexadécimale est :01
      et En binaire : 00000001
    """
    return message + b'\x01'


def retirer_padding(message: bytes) -> bytes:
    """
    - Retire le padding après déchiffrement.
    - Règle : retire le dernier octet (qui doit être 0x01).
    Lève une erreur si le padding est invalide.
    Args: message : bytes = le message déchiffré avec padding
    - Returns: bytes = le message original sans padding
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
    - Convertit un message texte en séquence d'octets UTF-8.
    - Args: message = le texte à chiffrer
    - Returns: bytes — les octets correspondants
    """
    return message.encode('utf-8')


def octets_vers_message(octets: bytes) -> str:
    """
    - Convertit une séquence d'octets en texte UTF-8.
    - Son rôle est l'inverse de : message_vers_octets()
    - Args: octets : bytes = les octets à décoder
    - Returns: str = le texte décodé
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