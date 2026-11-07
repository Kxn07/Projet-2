import os                                     # chemins

from donnees import JeuDeDonnees, CIBLE       # chargement et nettoyage
from modele import Modele                     # forêt aléatoire

jeu = JeuDeDonnees(os.path.join("donnees", "ford.csv"))
jeu.charger() 
jeu.nettoyer()
modele = Modele()
X, y = modele.preparer(jeu.df, CIBLE)
scores = modele.entrainer(X, y)
print(scores)
meta = jeu.metadonnees()
meta["rmse"] = scores           #(exigé : la métrique obtenue dans le JSON)
modele.sauvegarder("modeles", meta)