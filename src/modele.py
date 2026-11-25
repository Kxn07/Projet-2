import json                                   # écrire les métadonnées
import os                                     # chemins de fichiers
import time                                   # chronométrer l'entraînement
from functools import wraps                   # pour écrire le décorateur proprement
import itertools
import joblib                                 # sauvegarder le modèle
import numpy as np                            # calcul vectorisé du RMSE
import pandas as pd                           # données
from sklearn.ensemble import RandomForestRegressor   # la forêt aléatoire
from sklearn.model_selection import train_test_split # séparation train/test

from exceptions import DonneeInvalideError

def rmse(reels: np.ndarray, predits: np.ndarray) -> float:
    """Retourne le RMSE entre valeurs réelles et prédites.

    Lève DonneeInvalideError si les tailles diffèrent.
    """
    if len(reels) != len(predits):
        raise DonneeInvalideError("Les deux tableaux doivent avoir la même taille.")
    erreurs = reels - predits        
    return float(np.sqrt(np.mean(erreurs ** 2)))

def chronometre(fonction):
    """Décorateur : affiche la durée d'exécution de la fonction."""
    @wraps(fonction)                         # garde le nom et la docstring d'origine
    def enveloppe(*args, **kwargs):
        debut = time.perf_counter()
        resultat = fonction(*args, **kwargs)   
        duree = time.perf_counter() - debut
        print(f"{fonction.__name__} : {duree:.2f} s")
        return resultat
    return enveloppe

class Modele:
    """Forêt aléatoire qui prédit le prix d'une voiture."""

    def __init__(self, graine: int = 42) -> None:
        self._graine = graine                 # graine fixe = résultats reproductibles
        self._foret = RandomForestRegressor(n_estimators=100, random_state=graine)
        self._colonnes: list[str] = []        # colonnes après encodage (pour prédire plus tard)

    def preparer(self, df: pd.DataFrame, cible: str) -> tuple[pd.DataFrame, pd.Series]:
        """Sépare X (entrées encodées) et y (cible)."""
        X = pd.get_dummies(df.drop(columns=[cible]))   #(retire la cible, encode le texte)

        """"X = les entrées (année, km, carburant…) : ce que le modèle reçoit.
          Majuscule car c’est un tableau (plusieurs colonnes).
          y = la cible (price) : ce que le modèle doit deviner. Minuscule car c’est une seule colonne."""
        y = df[cible]
        self._colonnes = list(X.columns)
        return X, y
    
    @chronometre                              # affiche la durée d'entraînement
    def entrainer(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Entraîne la forêt et retourne les RMSE (modèle et référence) sur le test."""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=self._graine)
        #test_size=0.2 : 20 % des données gardées pour le test, jamais vues à l’entraînement.

        self._foret.fit(X_train, y_train)            #(apprentissage)
        predits = self._foret.predict(X_test)
        reference = np.full(len(y_test), y_train.mean())   #(prédit toujours la moyenne)

        #np.full(n, v) : tableau de n cases contenant toutes v.

        return {"rmse_modele": rmse(y_test.to_numpy(), predits),
                "rmse_reference": rmse(y_test.to_numpy(), reference)}


    def sauvegarder(self, dossier: str, metadonnees: dict) -> None:
        """Enregistre la forêt (joblib) et les métadonnées (JSON) dans dossier."""
        os.makedirs(dossier, exist_ok=True)               
        joblib.dump(self._foret, os.path.join(dossier, "modele.joblib"))
        metadonnees["colonnes_encodees"] = self._colonnes   #(utile pour prédire)
        with open(os.path.join(dossier, "metadonnees.json"), "w", encoding="utf-8") as fichier:
            json.dump(metadonnees, fichier, ensure_ascii=False, indent=2)

    @classmethod
    def charger(cls, dossier: str) -> "Modele":
        """Recharge le modèle et ses colonnes. Lève DonneeInvalideError s'ils manquent."""
        chemin_modele = os.path.join(dossier, "modele.joblib")
        chemin_meta = os.path.join(dossier, "metadonnees.json")
        if not os.path.exists(chemin_modele) or not os.path.exists(chemin_meta):
            raise DonneeInvalideError("Modèle introuvable : lancez python src/entrainement.py")
        modele = cls()                                   # crée un Modele vide
        modele._foret = joblib.load(chemin_modele)       # remplace sa forêt par la sauvegardée
        with open(chemin_meta, encoding="utf-8") as fichier:
            modele._colonnes = json.load(fichier)["colonnes_encodees"]  # colonnes vues à l'entraînement
        return modele

    def predire(self, lignes: pd.DataFrame) -> np.ndarray:
        """Retourne un prix prédit par ligne. Lève DonneeInvalideError si non chargé."""
        if not self._colonnes:
            raise DonneeInvalideError("Modèle non entraîné ou non chargé.")
        X = pd.get_dummies(lignes)                                # encode le texte comme à l'entraînement
        X = X.reindex(columns=self._colonnes, fill_value=0)       # mêmes colonnes, dans le même ordre
        return self._foret.predict(X)

def valeurs_typiques(df: pd.DataFrame, modele_voiture: str, cible: str) -> dict:
    """Valeur typique de chaque colonne pour un modèle de voiture (médiane ou plus fréquente).

    Lève DonneeInvalideError si le modèle de voiture est inconnu.
    """
    sous_df = df[df["model"] == modele_voiture]                   # annonces de ce modèle seulement
    if sous_df.empty:
        raise DonneeInvalideError(f"Modèle de voiture inconnu : {modele_voiture}")
    typiques = {}
    for nom in sous_df.columns:
        if nom == cible:
            continue                                              # on ne remplit pas le prix
        colonne = sous_df[nom]
        if pd.api.types.is_numeric_dtype(colonne):
            typiques[nom] = float(colonne.median())               # nombre : médiane
        else:
            typiques[nom] = colonne.mode()[0]                     # texte : valeur la plus fréquente
    return typiques


def generer_combinaisons(choix: dict, nb_points: int = 5) -> pd.DataFrame:
    """Crée une ligne par combinaison. choix : colonne -> valeur ou tuple (min, max).

    Lève DonneeInvalideError si un minimum dépasse son maximum.
    """
    listes = {}
    for nom, valeur in choix.items():
        if isinstance(valeur, tuple):                             # bornes min/max
            minimum, maximum = valeur
            if minimum > maximum:
                raise DonneeInvalideError(f"{nom} : le minimum dépasse le maximum.")
            listes[nom] = list(np.unique(np.linspace(minimum, maximum, nb_points)))  # 5 valeurs réparties
        else:
            listes[nom] = [valeur]                                # valeur unique
    combinaisons = itertools.product(*listes.values())            # toutes les combinaisons
    return pd.DataFrame(combinaisons, columns=list(listes.keys()))


def fourchette(prix: np.ndarray) -> dict:
    """Retourne le prix minimum, médian et maximum."""
    return {"min": float(np.min(prix)), "mediane": float(np.median(prix)), "max": float(np.max(prix))}


def nb_annonces_similaires(df: pd.DataFrame, choix: dict) -> int:
    """Compte les annonces qui respectent les catégories et les bornes choisies."""
    masque = np.ones(len(df), dtype=bool)                         # au départ : toutes les annonces
    for nom, valeur in choix.items():
        if isinstance(valeur, tuple):                             # bornes : entre min et max
            masque &= df[nom].between(valeur[0], valeur[1]).to_numpy()
        elif isinstance(valeur, str):                             # catégorie : égalité exacte
            masque &= (df[nom] == valeur).to_numpy()
    return int(masque.sum())