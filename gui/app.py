"""
app.py — Interface Graphique SPNX-16
=====================================
Interface Tkinter avec 4 onglets :
    1. Chiffrer / Déchiffrer
    2. Analyse (effet avalanche + graphiques)
    3. Attaque (force brute + extrapolation)
    4. À propos
"""

import sys, os, threading, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from core.cipher          import chiffrer, dechiffrer
from analysis.avalanche   import mesurer_avalanche_complet, mesurer_avalanche_par_bit
from analysis.ddt         import calculer_ddt, valeur_max_ddt
from analysis.lat import calculer_lat, valeur_max_lat
from attack.bruteforce    import attaque_force_brute, extrapoler

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False


# ─── Palette de couleurs ──────────────────────────────────────────────────────
BG_DARK    = "#0A1628"
BG_MID     = "#1A3A6B"
BG_CARD    = "#1E2A3A"
ACCENT     = "#2E75B6"
CYAN       = "#00B4D8"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY  = "#A0B0C0"
GREEN      = "#1E8449"
RED        = "#C0392B"
ORANGE     = "#E67E22"


# ─── Classe principale ────────────────────────────────────────────────────────

class SPNX16App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("SPNX-16 — Substitution–Permutation Network eXtended")
        self.geometry("950x700")
        self.minsize(800, 600)
        self.configure(bg=BG_DARK)
        self._construire_ui()

    def _construire_ui(self):
        # ── En-tête ──────────────────────────────────────────────────────────
        entete = tk.Frame(self, bg=BG_MID, pady=10)
        entete.pack(fill=tk.X)

        tk.Label(entete, text="SPNX-16",
                 font=("Courier New", 24, "bold"),
                 fg=CYAN, bg=BG_MID).pack()
        tk.Label(entete, text="Substitution–Permutation Network eXtended  |  Clé 16 bits  |  4 Rounds",
                 font=("Calibri", 10),
                 fg=TEXT_GRAY, bg=BG_MID).pack()

        # ── Onglets ───────────────────────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",
                         background=BG_DARK,
                         borderwidth=0)
        style.configure("TNotebook.Tab",
                         background=BG_MID,
                         foreground=TEXT_WHITE,
                         padding=[16, 8],
                         font=("Calibri", 11, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", TEXT_WHITE)])

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Créer les 4 onglets
        self._onglet_chiffrement()
        self._onglet_analyse()
        self._onglet_attaque()
        self._onglet_apropos()


# ─── ONGLET 1 : Chiffrement / Déchiffrement ──────────────────────────────────

    def _onglet_chiffrement(self):
        frame = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(frame, text="🔐  Chiffrer / Déchiffrer")

        # Titre
        tk.Label(frame, text="Chiffrement & Déchiffrement",
                 font=("Calibri", 14, "bold"),
                 fg=CYAN, bg=BG_DARK).pack(pady=(15, 5))

        # ── Clé ──────────────────────────────────────────────────────────────
        frame_cle = tk.Frame(frame, bg=BG_CARD, padx=15, pady=10)
        frame_cle.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(frame_cle, text="Clé secrète (valeur décimale 0–65535) :",
                 font=("Calibri", 11), fg=TEXT_GRAY, bg=BG_CARD).pack(anchor=tk.W)

        self.var_cle = tk.StringVar(value="43981")
        frame_cle_input = tk.Frame(frame_cle, bg=BG_CARD)
        frame_cle_input.pack(fill=tk.X, pady=5)

        self.entry_cle = tk.Entry(frame_cle_input,
                                   textvariable=self.var_cle,
                                   font=("Courier New", 13),
                                   bg="#0D2137", fg=CYAN,
                                   insertbackground=CYAN,
                                   width=12, relief=tk.FLAT)
        self.entry_cle.pack(side=tk.LEFT)

        self.label_cle_info = tk.Label(frame_cle_input,
                                        text="= 0xABCD = 1010101111001101",
                                        font=("Courier New", 10),
                                        fg=TEXT_GRAY, bg=BG_CARD)
        self.label_cle_info.pack(side=tk.LEFT, padx=10)
        self.var_cle.trace("w", self._maj_info_cle)

        # ── Message ───────────────────────────────────────────────────────────
        frame_msg = tk.Frame(frame, bg=BG_CARD, padx=15, pady=10)
        frame_msg.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        tk.Label(frame_msg, text="Message clair :",
                 font=("Calibri", 11), fg=TEXT_GRAY, bg=BG_CARD).pack(anchor=tk.W)

        self.text_message = scrolledtext.ScrolledText(
            frame_msg, height=4,
            font=("Calibri", 12),
            bg="#0D2137", fg=TEXT_WHITE,
            insertbackground=TEXT_WHITE,
            relief=tk.FLAT)
        self.text_message.pack(fill=tk.BOTH, expand=True, pady=5)
        self.text_message.insert(tk.END, "Hello SPNX-16 !")

        # ── Boutons ───────────────────────────────────────────────────────────
        frame_btns = tk.Frame(frame, bg=BG_DARK)
        frame_btns.pack(pady=8)

        self._bouton(frame_btns, "🔒  CHIFFRER",
                     ACCENT, self._action_chiffrer).pack(side=tk.LEFT, padx=8)
        self._bouton(frame_btns, "🔓  DÉCHIFFRER",
                     GREEN, self._action_dechiffrer).pack(side=tk.LEFT, padx=8)
        self._bouton(frame_btns, "🗑  EFFACER",
                     "#555", self._action_effacer_chiffrement).pack(side=tk.LEFT, padx=8)

        # ── Résultat ──────────────────────────────────────────────────────────
        frame_res = tk.Frame(frame, bg=BG_CARD, padx=15, pady=10)
        frame_res.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        tk.Label(frame_res, text="Résultat :",
                 font=("Calibri", 11), fg=TEXT_GRAY, bg=BG_CARD).pack(anchor=tk.W)

        self.text_resultat = scrolledtext.ScrolledText(
            frame_res, height=5,
            font=("Courier New", 11),
            bg="#0D2137", fg=GREEN,
            insertbackground=GREEN,
            relief=tk.FLAT, state=tk.DISABLED)
        self.text_resultat.pack(fill=tk.BOTH, expand=True, pady=5)

    def _maj_info_cle(self, *args):
        try:
            val = int(self.var_cle.get())
            if 0 <= val <= 65535:
                self.label_cle_info.config(
                    fg=CYAN,
                    text=f"= 0x{val:04X} = {val:016b}")
            else:
                self.label_cle_info.config(fg=RED, text="⚠️ Valeur hors limites (0–65535)")
        except ValueError:
            self.label_cle_info.config(fg=RED, text="⚠️ Entrez un nombre entier")

    def _action_chiffrer(self):
        try:
            cle = int(self.var_cle.get())
            if not (0 <= cle <= 65535):
                raise ValueError("Clé hors limites")
            msg     = self.text_message.get("1.0", tk.END).rstrip("\n")
            chiffre = chiffrer(msg, cle)
            hex_str = chiffre.hex()
            bin_str = ' '.join(f"{b:08b}" for b in chiffre)
            self._afficher_resultat(
                f"✅ CHIFFREMENT RÉUSSI\n\n"
                f"Hexadécimal : {hex_str}\n\n"
                f"Binaire     : {bin_str}\n\n"
                f"Octets bruts: {list(chiffre)}"
            )
            # Sauvegarder pour déchiffrement
            self._dernier_chiffre = chiffre
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _action_dechiffrer(self):
        try:
            cle = int(self.var_cle.get())
            if not (0 <= cle <= 65535):
                raise ValueError("Clé hors limites")

            # Utiliser le dernier chiffré si disponible
            if hasattr(self, '_dernier_chiffre'):
                msg_dechiffre = dechiffrer(self._dernier_chiffre, cle)
                self._afficher_resultat(
                    f"✅ DÉCHIFFREMENT RÉUSSI\n\n"
                    f"Message retrouvé : {repr(msg_dechiffre)}\n\n"
                    f"Réversibilité    : ✅ OK"
                )
            else:
                messagebox.showwarning("Attention",
                    "Chiffrez d'abord un message avant de déchiffrer.")
        except Exception as e:
            messagebox.showerror("Erreur de déchiffrement",
                f"Clé incorrecte ou message corrompu.\n\n{str(e)}")

    def _action_effacer_chiffrement(self):
        self.text_message.delete("1.0", tk.END)
        self._afficher_resultat("")
        if hasattr(self, '_dernier_chiffre'):
            del self._dernier_chiffre

    def _afficher_resultat(self, texte: str):
        self.text_resultat.config(state=tk.NORMAL)
        self.text_resultat.delete("1.0", tk.END)
        self.text_resultat.insert(tk.END, texte)
        self.text_resultat.config(state=tk.DISABLED)


# ─── ONGLET 2 : Analyse ───────────────────────────────────────────────────────

    def _onglet_analyse(self):
        frame = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(frame, text="📊  Analyse")

        tk.Label(frame, text="Analyse de Sécurité — Effet Avalanche & DDT",
                 font=("Calibri", 14, "bold"),
                 fg=CYAN, bg=BG_DARK).pack(pady=(15, 5))

        # ── Paramètres ────────────────────────────────────────────────────────
        frame_params = tk.Frame(frame, bg=BG_CARD, padx=15, pady=10)
        frame_params.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(frame_params, text="Nombre d'itérations :",
                 font=("Calibri", 11), fg=TEXT_GRAY, bg=BG_CARD).pack(side=tk.LEFT)

        self.var_iterations = tk.StringVar(value="2000")
        tk.Entry(frame_params,
                 textvariable=self.var_iterations,
                 font=("Courier New", 12),
                 bg="#0D2137", fg=CYAN,
                 width=8, relief=tk.FLAT).pack(side=tk.LEFT, padx=10)

        # ── Boutons ───────────────────────────────────────────────────────────
        frame_btns = tk.Frame(frame, bg=BG_DARK)
        frame_btns.pack(pady=8)

        self._bouton(frame_btns, "📈  Lancer Avalanche",
                     ACCENT, self._action_avalanche).pack(side=tk.LEFT, padx=5)
        self._bouton(frame_btns, "🔬  Avalanche par bit",
                     "#8E44AD", self._action_avalanche_bit).pack(side=tk.LEFT, padx=5)
        self._bouton(frame_btns, "🧮  Calculer DDT",
                     ORANGE, self._action_ddt).pack(side=tk.LEFT, padx=5)
        self._bouton(frame_btns, " 📐 Calculer LAT",
             "#8E44AD", self._action_lat).pack(side=tk.LEFT, padx=5)

        # ── Zone résultat texte ───────────────────────────────────────────────
        frame_res = tk.Frame(frame, bg=BG_CARD, padx=15, pady=10)
        frame_res.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.text_analyse = scrolledtext.ScrolledText(
            frame_res,
            font=("Courier New", 11),
            bg="#0D2137", fg=TEXT_WHITE,
            insertbackground=TEXT_WHITE,
            relief=tk.FLAT, state=tk.DISABLED)
        self.text_analyse.pack(fill=tk.BOTH, expand=True)

    def _ecrire_analyse(self, texte: str):
        self.text_analyse.config(state=tk.NORMAL)
        self.text_analyse.delete("1.0", tk.END)
        self.text_analyse.insert(tk.END, texte)
        self.text_analyse.config(state=tk.DISABLED)

    def _action_avalanche(self):
        def tache():
            try:
                n = int(self.var_iterations.get())
                self._ecrire_analyse(f"⏳ Calcul en cours sur {n} essais...")
                stats = mesurer_avalanche_complet(n)
                ok    = 40 <= stats['moyenne'] <= 60
                texte = (
                    f"✅ EFFET AVALANCHE — RÉSULTATS\n"
                    f"{'─' * 40}\n"
                    f"Essais          : {stats['nb_essais']}\n"
                    f"Moyenne         : {stats['moyenne']:.2f}%\n"
                    f"Minimum         : {stats['minimum']:.2f}%\n"
                    f"Maximum         : {stats['maximum']:.2f}%\n"
                    f"Cible           : 40% — 60%\n"
                    f"Critère 50%     : {'✅ RESPECTÉ' if ok else '❌ NON RESPECTÉ'}\n"
                )
                self._ecrire_analyse(texte)

                if MATPLOTLIB_OK:
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.hist(stats['pourcentages'], bins=20,
                            color=ACCENT, edgecolor='white', alpha=0.85)
                    ax.axvline(x=50, color=RED, linewidth=2,
                               linestyle='--', label='Cible 50%')
                    ax.axvline(x=stats['moyenne'], color='lime',
                               linewidth=2, label=f"Moyenne {stats['moyenne']:.1f}%")
                    ax.axvspan(40, 60, alpha=0.1, color='green')
                    ax.set_title("Distribution de l'Effet Avalanche — SPNX-16")
                    ax.set_xlabel("% bits modifiés")
                    ax.set_ylabel("Nombre d'essais")
                    ax.legend()
                    ax.set_facecolor("#0D2137")
                    fig.patch.set_facecolor(BG_CARD)
                    plt.tight_layout()
                    plt.savefig("rapport/avalanche_histogram.png", dpi=150)
                    plt.show()
            except Exception as e:
                self._ecrire_analyse(f"❌ Erreur : {str(e)}")

        threading.Thread(target=tache, daemon=True).start()

    def _action_avalanche_bit(self):
        try:
            resultats = mesurer_avalanche_par_bit("A", 0xABCD)
            lignes    = ["AVALANCHE BIT PAR BIT — message='A', clé=0xABCD\n" + "─" * 45]
            for r in resultats:
                barre = "█" * int(r['pourcentage'] / 10)
                ligne = (f"Bit {r['bit']} → "
                         f"{r['bits_differents']:2d}/{r['total_bits']} bits "
                         f"({r['pourcentage']:5.1f}%)  {barre}")
                lignes.append(ligne)
            self._ecrire_analyse("\n".join(lignes))
        except Exception as e:
            self._ecrire_analyse(f"❌ Erreur : {str(e)}")

    def _action_ddt(self):
        def tache():
            try:
                self._ecrire_analyse("⏳ Calcul de la DDT en cours...")
                ddt    = calculer_ddt()
                valmax = valeur_max_ddt(ddt)

                lignes = [
                    "DIFFERENCE DISTRIBUTION TABLE — S-Box SPNX-16",
                    "─" * 45,
                    f"Valeur max (hors [0][0]) : {valmax}",
                    f"Valeur idéale 4 bits     : 4",
                    f"Évaluation : {'✅ Bonne non-linéarité' if valmax <= 4 else '⚠️ Acceptable' if valmax <= 6 else '❌ Faible'}",
                    "",
                    "Table (lignes=Δx, colonnes=Δy) :",
                    "     " + "  ".join(f"{j:X}" for j in range(16)),
                ]
                for i in range(16):
                    ligne = f"  {i:X}  " + "  ".join(
                        " *" if (i == 0 and j == 0) else
                        f"{ddt[i][j]:2d}" for j in range(16))
                    lignes.append(ligne)

                self._ecrire_analyse("\n".join(lignes))

                if MATPLOTLIB_OK:
                    import numpy as np
                    data       = np.array(ddt, dtype=float)
                    data[0][0] = 0
                    fig, ax    = plt.subplots(figsize=(8, 6))
                    im = ax.imshow(data, cmap='Blues', vmin=0, vmax=8)
                    for i in range(16):
                        for j in range(16):
                            if ddt[i][j] > 0:
                                ax.text(j, i, str(ddt[i][j]),
                                        ha='center', va='center',
                                        fontsize=7,
                                        color='white' if ddt[i][j] >= 6 else 'black')
                    plt.colorbar(im, ax=ax)
                    ax.set_title("DDT — S-Box SPNX-16")
                    ax.set_xlabel("Δy (sortie)")
                    ax.set_ylabel("Δx (entrée)")
                    plt.tight_layout()
                    plt.savefig("rapport/ddt_heatmap.png", dpi=150)
                    plt.show()
            except Exception as e:
                self._ecrire_analyse(f"❌ Erreur : {str(e)}")

        threading.Thread(target=tache, daemon=True).start()

    def _action_lat(self):
        def tache():
            try:
                self._ecrire_analyse("⏳ Calcul de la LAT en cours...")
                lat = calculer_lat()
                valmax = valeur_max_lat(lat)

                lignes = [
                    "LINEAR APPROXIMATION TABLE — S-Box SPNX-16",
                    "─" * 45,
                    f"Biais max (hors [0][0]) : {valmax}",
                    f"Valeur idéale 4 bits    : 4",
                    f"Évaluation : {'✅ Bonne résistance linéaire' if valmax <= 4 else '⚠️ Acceptable' if valmax <= 6 else '❌ Faible'}",
                    "",
                    "Table (lignes=a, colonnes=b) :",
                    "      " + " ".join(f"{j:X}" for j in range(16)),
                ]
                for i in range(16):
                    ligne = f"  {i:X} " + " ".join(
                        "  *" if (i == 0 and j == 0) else
                        f"{lat[i][j]:+3d}" for j in range(16))
                    lignes.append(ligne)

                self._ecrire_analyse("\n".join(lignes))

                if MATPLOTLIB_OK:
                    import numpy as np
                    data = np.array(lat, dtype=float)
                    data[0][0] = 0
                    fig, ax = plt.subplots(figsize=(8, 6))
                    im = ax.imshow(data, cmap='RdBu', vmin=-8, vmax=8)
                    for i in range(16):
                        for j in range(16):
                            if not (i == 0 and j == 0):
                                ax.text(j, i, f"{lat[i][j]:+d}",ha='center', va='center',
                                    fontsize=7,
                                    color='white' if abs(lat[i][j]) >= 6 else 'black')
                    plt.colorbar(im, ax=ax)
                    ax.set_title("LAT — S-Box SPNX-16")
                    ax.set_xlabel("b (masque sortie)")
                    ax.set_ylabel("a (masque entrée)")
                    plt.tight_layout()
                    plt.savefig("rapport/lat_heatmap.png", dpi=150)
                    plt.show()
            except Exception as e: 
                self._ecrire_analyse(f"❌ Erreur : {str(e)}")  
        threading.Thread(target=tache, daemon=True).start()


# ─── ONGLET 3 : Attaque ───────────────────────────────────────────────────────

    def _onglet_attaque(self):
        frame = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(frame, text="⚔️  Attaque")

        tk.Label(frame, text="Attaque par Force Brute — 2¹⁶ = 65 536 clés",
                 font=("Calibri", 14, "bold"),
                 fg=CYAN, bg=BG_DARK).pack(pady=(15, 5))

        # ── Inputs ────────────────────────────────────────────────────────────
        frame_inputs = tk.Frame(frame, bg=BG_CARD, padx=15, pady=12)
        frame_inputs.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(frame_inputs, text="Message clair connu :",
                 font=("Calibri", 11), fg=TEXT_GRAY, bg=BG_CARD).grid(
                 row=0, column=0, sticky=tk.W, pady=4)

        self.var_clair_attaque = tk.StringVar(value="X")
        tk.Entry(frame_inputs,
                 textvariable=self.var_clair_attaque,
                 font=("Courier New", 12),
                 bg="#0D2137", fg=CYAN,
                 width=20, relief=tk.FLAT).grid(row=0, column=1, padx=10)

        tk.Label(frame_inputs, text="Clé réelle (simulation) :",
                 font=("Calibri", 11), fg=TEXT_GRAY, bg=BG_CARD).grid(
                 row=1, column=0, sticky=tk.W, pady=4)

        self.var_cle_reelle = tk.StringVar(value="6699")
        tk.Entry(frame_inputs,
                 textvariable=self.var_cle_reelle,
                 font=("Courier New", 12),
                 bg="#0D2137", fg=ORANGE,
                 width=10, relief=tk.FLAT).grid(row=1, column=1, padx=10, sticky=tk.W)

        # ── Barre de progression ──────────────────────────────────────────────
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            frame, variable=self.progress_var,
            maximum=100, mode='determinate',
            length=400)
        self.progress_bar.pack(pady=8)

        self.label_progression = tk.Label(
            frame, text="En attente...",
            font=("Calibri", 10), fg=TEXT_GRAY, bg=BG_DARK)
        self.label_progression.pack()

        # ── Bouton ────────────────────────────────────────────────────────────
        self._bouton(frame, "⚔️  LANCER L'ATTAQUE",
                     RED, self._action_attaque).pack(pady=8)

        # ── Résultat ──────────────────────────────────────────────────────────
        frame_res = tk.Frame(frame, bg=BG_CARD, padx=15, pady=10)
        frame_res.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.text_attaque = scrolledtext.ScrolledText(
            frame_res,
            font=("Courier New", 10),
            bg="#0D2137", fg=TEXT_WHITE,
            insertbackground=TEXT_WHITE,
            relief=tk.FLAT, state=tk.DISABLED)
        self.text_attaque.pack(fill=tk.BOTH, expand=True)

    def _ecrire_attaque(self, texte: str):
        self.text_attaque.config(state=tk.NORMAL)
        self.text_attaque.delete("1.0", tk.END)
        self.text_attaque.insert(tk.END, texte)
        self.text_attaque.config(state=tk.DISABLED)

    def _action_attaque(self):
        def tache():
            try:
                msg_clair  = self.var_clair_attaque.get()
                cle_reelle = int(self.var_cle_reelle.get())
                msg_chiffre = chiffrer(msg_clair, cle_reelle)

                self._ecrire_attaque(
                    f"🔍 Attaque lancée...\n"
                    f"Message clair   : {repr(msg_clair)}\n"
                    f"Message chiffré : {msg_chiffre.hex()}\n"
                    f"(Clé réelle cachée à l'attaquant)\n\n"
                    f"Test exhaustif des 65 536 clés...\n"
                )

                # Attaque avec mise à jour de la barre de progression
                cle_trouvee  = None
                cles_testees = 0
                debut        = time.perf_counter()

                for cle in range(0x10000):
                    cles_testees += 1

                    if cles_testees % 1000 == 0:
                        pct = (cles_testees / 65536) * 100
                        self.progress_var.set(pct)
                        self.label_progression.config(
                            text=f"{pct:.1f}%  —  {cles_testees}/65536 clés testées")

                    if chiffrer(msg_clair, cle) == msg_chiffre:
                        cle_trouvee = cle
                        break

                fin   = time.perf_counter()
                temps = fin - debut
                debit = cles_testees / temps

                self.progress_var.set(100)
                self.label_progression.config(text="✅ Terminé !")

                # Résultat
                espaces = [
                    (16,  "SPNX-16      "),
                    (32,  "32 bits      "),
                    (64,  "64 bits      "),
                    (128, "AES-128      "),
                    (256, "AES-256      "),
                ]
                extrapol = ""
                for bits, nom in espaces:
                    sec = (2 ** bits) / debit
                    if sec < 60:
                        affiche = f"{sec:.2f} sec"
                    elif sec < 3600:
                        affiche = f"{sec/60:.2f} min"
                    elif sec < 86400:
                        affiche = f"{sec/3600:.2f} h"
                    elif sec < 86400*365:
                        affiche = f"{sec/86400:.2f} jours"
                    else:
                        affiche = f"{sec/(86400*365):.2e} années"
                    extrapol += f"  {bits:3d} bits ({nom}) → {affiche}\n"

                self._ecrire_attaque(
                    f"✅ CLÉ TROUVÉE !\n"
                    f"{'─' * 45}\n"
                    f"Clé retrouvée   : {cle_trouvee} "
                    f"(0x{cle_trouvee:04X} | {cle_trouvee:016b})\n"
                    f"Clé réelle      : {cle_reelle} "
                    f"(0x{cle_reelle:04X})\n"
                    f"Correspondance  : {'✅ OUI' if cle_trouvee == cle_reelle else '❌ NON'}\n\n"
                    f"Clés testées    : {cles_testees:,}\n"
                    f"Temps écoulé    : {temps:.4f} secondes\n"
                    f"Débit           : {debit:,.0f} clés/seconde\n\n"
                    f"EXTRAPOLATION THÉORIQUE\n"
                    f"{'─' * 45}\n"
                    f"{extrapol}\n"
                    f"ℹ️  AES-128 est considéré incassable par force brute\n"
                    f"   avec la technologie actuelle."
                )
            except Exception as e:
                self._ecrire_attaque(f"❌ Erreur : {str(e)}")

        threading.Thread(target=tache, daemon=True).start()


# ─── ONGLET 4 : À propos ──────────────────────────────────────────────────────

    def _onglet_apropos(self):
        frame = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(frame, text="ℹ️  À propos")

        contenu = scrolledtext.ScrolledText(
            frame,
            font=("Calibri", 12),
            bg=BG_DARK, fg=TEXT_WHITE,
            insertbackground=TEXT_WHITE,
            relief=tk.FLAT, state=tk.NORMAL,
            wrap=tk.WORD)
        contenu.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        texte = """
  ███████╗██████╗ ███╗   ██╗██╗  ██╗    ██╗ ██████╗
  ██╔════╝██╔══██╗████╗  ██║╚██╗██╔╝   ███║██╔════╝
  ███████╗██████╔╝██╔██╗ ██║ ╚███╔╝    ╚██║███████╗
  ╚════██║██╔═══╝ ██║╚██╗██║ ██╔██╗     ██║██╔═══╝╝
  ███████║██║     ██║ ╚████║██╔╝ ██╗   ╚╝██║╚██████╗
  ╚══════╝╚═╝     ╚═╝  ╚═══╝╚═╝  ╚═╝      ╚═╝ ╚═════╝

  Substitution–Permutation Network eXtended — 16-bit Key
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ARCHITECTURE
  ─────────────────────────────────────────────
  Taille de bloc    : 8 bits (1 octet)
  Taille de clé     : 16 bits (65 536 clés)
  Nombre de rounds  : 4
  Sous-clés         : K1 à K5

  STRUCTURE DES ROUNDS
  ─────────────────────────────────────────────
  Round 1 à 3  :  XOR(Ki)  →  S-Box×2  →  Permutation
  Round 4      :  XOR(K4)  →  S-Box×2  →  XOR(K5) whitening

  MODULES
  ─────────────────────────────────────────────
  core/          →  S-Box, Permutation, Key Schedule, Cipher, Padding
  analysis/      →  Effet avalanche, DDT, Graphiques
  attack/        →  Force brute + extrapolation théorique
  gui/           →  Cette interface (Tkinter)
  tests/         →  Tests unitaires automatisés

  ⚠️  AVERTISSEMENT SÉCURITAIRE
  ─────────────────────────────────────────────
  SPNX-16 est un prototype académique UNIQUEMENT.
  Avec 2¹⁶ = 65 536 clés possibles, il est cassable
  en moins d'une seconde par n'importe quel ordinateur.

  NE PAS utiliser pour protéger des données réelles.
  Langage : Python 3.8+  |  Aucune lib crypto externe

  ─────────────────────────────────────────────
  Club       : SECURINETS FST
  Encadrant  : Chahine Ben Salah
  ─────────────────────────────────────────────
"""
        contenu.insert(tk.END, texte)
        contenu.config(state=tk.DISABLED)


# ─── Utilitaire bouton ────────────────────────────────────────────────────────

    def _bouton(self, parent, texte: str,
                couleur: str, commande) -> tk.Button:
        return tk.Button(
            parent, text=texte,
            font=("Calibri", 11, "bold"),
            bg=couleur, fg=TEXT_WHITE,
            activebackground=CYAN,
            activeforeground=BG_DARK,
            relief=tk.FLAT, padx=14, pady=7,
            cursor="hand2",
            command=commande)


# ─── Point d'entrée ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = SPNX16App()
    app.mainloop()