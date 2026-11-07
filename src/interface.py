"""Interface Streamlit : saisie des caractéristiques, prédiction, graphique et historique."""

import csv
import json
import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from donnees import CIBLE, JeuDeDonnees, VariableCategorielle, VariableNumerique
from exceptions import DonneeInvalideError
from modele import (Modele, fourchette, generer_combinaisons,
                    nb_annonces_similaires, valeurs_typiques)

SEUIL_FIABILITE = 10                     # moins d'annonces similaires -> avertissement
INDIFFERENT = "Indifférent"              # choix "pas de préférence" des listes
CHOISIR = "-- Choisir --"                # valeur vide du modèle obligatoire

LIBELLES = {                             # noms affichés à l'utilisateur
    "model": "Modèle",
    "year": "Année",
    "transmission": "Transmission",
    "mileage": "Kilométrage (miles)",
    "fuelType": "Carburant",
    "tax": "Taxe routière (£)",
    "mpg": "Consommation (mpg)",
    "engineSize": "Cylindrée (L)",
}


class Application:
    """Contient le jeu de données, le modèle et les variables (composition)."""

    def __init__(self, chemin_donnees: str, dossier_modele: str, chemin_historique: str) -> None:
        self._jeu = JeuDeDonnees(chemin_donnees)          # données (graphique, valeurs typiques)
        self._jeu.charger()
        self._jeu.nettoyer()
        self._modele = Modele.charger(dossier_modele)     # forêt déjà entraînée
        self._variables = self._jeu.variables()           # une Variable par colonne d'entrée
        self._historique = chemin_historique
        with open(os.path.join(dossier_modele, "metadonnees.json"), encoding="utf-8") as fichier:
            self._rmse = json.load(fichier)["rmse"]["rmse_modele"]

    @property
    def variables(self) -> list:
        """Variables d'entrée (copie de la liste)."""
        return list(self._variables)

    @property
    def rmse(self) -> float:
        """Erreur typique du modèle sur le test (£)."""
        return self._rmse

    def estimer(self, modele_voiture: str, saisies: dict) -> dict:
        """Prédit une fourchette de prix.

        saisies : colonne -> valeur ou tuple (min, max) ; les colonnes absentes
        prennent la valeur typique du modèle de voiture.
        Lève DonneeInvalideError si une saisie est incohérente.
        """
        df = self._jeu.df
        choix = valeurs_typiques(df, modele_voiture, CIBLE)       # valeurs par défaut
        choix.update(saisies)                                     # remplacées par les saisies
        choix["model"] = modele_voiture
        prix = self._modele.predire(generer_combinaisons(choix))  # un prix par combinaison
        resultat = fourchette(prix)
        resultat["nb_similaires"] = nb_annonces_similaires(df, {"model": modele_voiture, **saisies})
        self.enregistrer(modele_voiture, saisies, resultat)
        return resultat

    def enregistrer(self, modele_voiture: str, saisies: dict, resultat: dict) -> None:
        """Ajoute une prédiction à la fin du fichier d'historique (CSV)."""
        existe = os.path.exists(self._historique)
        with open(self._historique, "a", newline="", encoding="utf-8") as fichier:
            ecrivain = csv.writer(fichier)
            if not existe:                                        # en-tête la première fois
                ecrivain.writerow(["date", "modele", "saisies", "min", "mediane", "max"])
            ecrivain.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                modele_voiture.strip(),
                "; ".join(f"{nom}={valeur}" for nom, valeur in saisies.items()) or "aucune",
                round(resultat["min"]), round(resultat["mediane"]), round(resultat["max"]),
            ])

    def lire_historique(self) -> pd.DataFrame:
        """Retourne l'historique (tableau vide s'il n'existe pas encore)."""
        if not os.path.exists(self._historique):
            return pd.DataFrame()
        with open(self._historique, encoding="utf-8") as fichier:
            return pd.read_csv(fichier)

    def graphique(self, resultat: dict) -> plt.Figure:
        """Histogramme des prix avec la fourchette prédite."""
        fig, ax = plt.subplots(figsize=(7, 3.5))
        ax.hist(self._jeu.df[CIBLE], bins=40, color="#9aa5b1", label="Annonces du jeu de données")
        ax.axvspan(resultat["min"], resultat["max"], color="#1D9E75", alpha=0.3, label="Fourchette prédite")
        ax.axvline(resultat["mediane"], color="#0F6E56", linewidth=2, label="Prix médian prédit")
        ax.set_title("Votre estimation parmi les prix des Ford d'occasion")
        ax.set_xlabel("Prix (£)")
        ax.set_ylabel("Nombre d'annonces")
        ax.legend()
        fig.tight_layout()
        return fig


def lire_numerique(variable: VariableNumerique) -> float | tuple | None:
    """Affiche deux champs min/max et retourne None, une valeur ou un tuple (min, max).

    Lève DonneeInvalideError si une saisie est non numérique ou hors intervalle.
    """
    libelle = LIBELLES.get(variable.nom, variable.nom)
    colonne_min, colonne_max = st.columns(2)
    texte_min = colonne_min.text_input(f"{libelle} min", key=f"{variable.nom}_min")
    texte_max = colonne_max.text_input(f"{libelle} max", key=f"{variable.nom}_max")
    st.caption(f"Entre {variable.minimum:g} et {variable.maximum:g} (optionnel)")
    remplis = [texte for texte in (texte_min, texte_max) if texte.strip()]
    if not remplis:
        return None                                    # champ laissé vide -> valeur typique
    if len(remplis) == 1:
        return variable.valider(remplis[0])            # une seule borne -> valeur exacte
    return (variable.valider(texte_min), variable.valider(texte_max))


@st.cache_resource                                     # charge le modèle une seule fois
def creer_application() -> Application:
    """Construit l'application à partir des fichiers du projet."""
    return Application(os.path.join("donnees", "ford.csv"), "modeles", "historique.csv")


def lancer() -> None:
    """Page Streamlit principale."""
    st.set_page_config(page_title="Prix d'une Ford d'occasion", layout="wide")
    st.title("Estimer le prix d'une Ford d'occasion")
    st.caption("Exercice pédagogique (INF1007) : estimation indicative, pas une aide à l'achat.")

    try:
        app = creer_application()
    except DonneeInvalideError as erreur:
        st.error(str(erreur))
        return

    gauche, droite = st.columns([1, 2])
    with gauche:
        st.subheader("Caractéristiques")
        variables = {variable.nom: variable for variable in app.variables}
        modele_voiture = st.selectbox(
            "Modèle (obligatoire)", [CHOISIR] + variables["model"].valeurs,
            format_func=str.strip)
        saisies: dict = {}
        erreurs: list[str] = []
        for nom, variable in variables.items():
            if nom == "model":
                continue
            if isinstance(variable, VariableCategorielle):
                choix = st.selectbox(LIBELLES.get(nom, nom), [INDIFFERENT] + variable.valeurs,
                                     format_func=str.strip)
                if choix != INDIFFERENT:
                    saisies[nom] = choix
            else:
                try:
                    valeur = lire_numerique(variable)
                    if valeur is not None:
                        saisies[nom] = valeur
                except DonneeInvalideError as erreur:
                    erreurs.append(f"{LIBELLES.get(nom, nom)} : {erreur}")
        bouton = st.button("Prédire", type="primary")

    with droite:
        if bouton:
            if modele_voiture == CHOISIR:
                st.error("Choisissez un modèle de voiture.")
            elif erreurs:
                for message in erreurs:
                    st.error(message)
            else:
                try:
                    resultat = app.estimer(modele_voiture, saisies)
                except DonneeInvalideError as erreur:
                    st.error(str(erreur))
                else:
                    st.subheader("Prix estimé")
                    if round(resultat["min"]) == round(resultat["max"]):
                        st.metric("Estimation", f"{resultat['mediane']:,.0f} £")
                    else:
                        st.metric("Fourchette",
                                  f"{resultat['min']:,.0f} £ à {resultat['max']:,.0f} £")
                        st.write(f"Prix médian : {resultat['mediane']:,.0f} £")
                    st.caption(f"Erreur typique du modèle : environ {app.rmse:,.0f} £")
                    if resultat["nb_similaires"] < SEUIL_FIABILITE:
                        st.warning(f"Seulement {resultat['nb_similaires']} annonces similaires "
                                   "dans les données : estimation peu fiable.")
                    st.pyplot(app.graphique(resultat))

        st.subheader("Historique des prédictions")
        historique = app.lire_historique()
        if historique.empty:
            st.write("Aucune prédiction pour l'instant.")
        else:
            st.dataframe(historique.iloc[::-1], hide_index=True)   # la plus récente en haut