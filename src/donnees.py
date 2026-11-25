import os                                  
from abc import ABC, abstractmethod        # pour faire une classe parente abstraite
import pandas as pd                        
from exceptions import DonneeInvalideError 

CIBLE = "price"                            # colonne à prédire
ANNEE_MAX = 2026                           # année maximale valide


class Variable(ABC):                       # ABC = classe abstraite (on ne l'utilise pas directement)
    def __init__(self, nom: str) -> None:
        self._nom=nom                                

    @abstractmethod                        # les classes enfants DOIVENT redéfinir cette méthode
    def valider(self, valeur):
        """Valide une saisie et la retourne convertie.
        Lève DonneeInvalideError si la saisie est invalide.
        """
        pass                                # reste vide ici
    @property
    def nom(self) -> str:
        """Nom de la colonne."""
        return self._nom

class VariableNumerique(Variable):         # hérite de Variable
    def __init__(self, nom: str, minimum: float, maximum: float) -> None:
        super().__init__(nom)              # appelle le __init__ du parent (stocke le nom)
        self._minimum=minimum                         # à toi : stocker minimum dans self._minimum
        self._maximum=maximum                                # à toi : stocker maximum dans self._maximum

    def __str__(self) -> str:
        return f"{self._nom} (numérique, {self._minimum} à {self._maximum})"
        
    @property
    def minimum(self) -> float:
        return self._minimum

    @property
    def maximum(self) -> float:
        return self._maximum
    
    def valider(self, valeur) -> float:
        """Retourne la valeur en float, ou lève DonneeInvalideError."""
        if valeur is None or str(valeur).strip() == "":
            raise DonneeInvalideError("champ vide")
        
        try: nombre=float(valeur)
        except ValueError:
            raise DonneeInvalideError("saisir un nombre")

        if nombre< self._minimum or nombre> self._maximum :
            raise DonneeInvalideError(f"Valeur entre {self._minimum} et {self._maximum}")
        return nombre

class VariableCategorielle(Variable):

    @property
    def valeurs(self) -> list[str]:
        return list(self._valeurs)
    
    def __init__(self, nom: str, valeurs: list[str]) -> None:
        super().__init__(nom)
        self._valeurs=list(valeurs) #stocker une copie 

    def valider(self, valeur) -> str:
        """Retourne la valeur si elle est dans la liste, sinon lève DonneeInvalideError."""
        if valeur not in self._valeurs:   
            raise DonneeInvalideError(f"{self._nom} : choisir une valeur de la liste")
        return valeur

class JeuDeDonnees:
    """Jeu de données : chargement et nettoyage du CSV."""

    def __init__(self, chemin: str) -> None:
        self._chemin=chemin   
        self._df=None  

    @property
    def df(self) -> pd.DataFrame:
        """Tableau de données (lecture seule)."""
        if self._df is None:
            raise DonneeInvalideError("Données non chargées.")
        return self._df

    def charger(self) -> None:
        """Lit le CSV. Lève DonneeInvalideError si le fichier n'existe pas."""
        if not os.path.exists(self._chemin):
            raise DonneeInvalideError(f"Fichier introuvable : {self._chemin}")
        with open (self._chemin, encoding="utf-8") as fichier:
            self._df=pd.read_csv(fichier)

    def nettoyer(self) -> int:
        """Retire les années impossibles et les cylindrées nulles.Retourne le nombre de lignes supprimées.
        """
        if self._df is None:
            raise DonneeInvalideError("Données non chargées.")
        avant=len(self._df) 
        self._df=self._df[self._df["year"]<=ANNEE_MAX]
        self._df=self._df[self._df["engineSize"]>0]
        return avant - len(self._df)
        
    def variables(self) -> list[Variable]:
        """Construit une Variable par colonne d'entrée (cible exclue)."""
        if self._df is None:                          # protection : données non chargées
            raise DonneeInvalideError("Données non chargées.")
        resultat: list[Variable] = []                 # liste des variables à retourner
        for nom in self._df.columns:                  # parcourt chaque colonne
            if nom == CIBLE:
                continue                              # saute la colonne à prédire
            colonne = self._df[nom]
            if pd.api.types.is_numeric_dtype(colonne):    # colonne numérique ?
                resultat.append(VariableNumerique(nom, float(colonne.min()), float(colonne.max())))
            else:                                         # sinon : texte
                resultat.append(VariableCategorielle(nom, sorted(colonne.unique())))
        return resultat

    def metadonnees(self) -> dict:
        """Décrit les colonnes (intervalles, valeurs possibles) pour le JSON."""
        infos: dict = {"cible": CIBLE, "colonnes": {}}
        for variable in self.variables():
            if isinstance(variable, VariableNumerique):
                infos["colonnes"][variable.nom] = {
                    "type": "numerique",
                    "min": variable.minimum,
                    "max": variable.maximum,
                }
            elif isinstance(variable, VariableCategorielle):
                infos["colonnes"][variable.nom] = {
                    "type": "categorielle", 
                    "valeurs": variable.valeurs
                }
        return infos

