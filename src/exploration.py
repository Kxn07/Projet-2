import os                              # gestion des chemins
import pandas as pd                    # manipulation des données
import matplotlib.pyplot as plt        # graphiques

chemin = os.path.join("donnees", "ford.csv") # Chemin du fichier (compatible Windows/Mac/Linux)

df = pd.read_csv(chemin) # Lecture du CSV dans un tableau (DataFrame)

print(df.shape)         # (nb lignes, nb colonnes)
print(df.dtypes)        # type de chaque colonne
print(df.isna().sum())  # nb de valeurs manquantes par colonne
print(df.describe())    # stats : min, max, moyenne... (repère les aberrations)

# Nettoyage : on garde seulement les lignes valides
df = df[df["year"] <= 2026]      # supprime les années impossibles (ex. 2060)
df = df[df["engineSize"] > 0]    # supprime les cylindrées à 0
print(df.shape)                  # nb de lignes restantes

# print(df[df["mpg"] > 100])                      # lignes avec mpg suspect
# print(df.sort_values("mpg", ascending=False).head(10))  # les 10 plus hauts

# Histogramme des prix en 40 intervalles
plt.hist(df["price"], bins=40)
plt.title("Distribution des prix des Ford d'occasion")  # titre
plt.xlabel("Prix (£)")                                  # axe x
plt.ylabel("Nombre d'annonces")                         # axe y
plt.savefig("exploration_prix.png")                     # enregistre l'image
plt.show()                                              # affiche le graphique