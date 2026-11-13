# Journal d'utilisation de l'IA

Outil utilisé : Claude (Anthropic), en conversation et dans l'éditeur (VS Code).
Principe suivi : l'IA explique et propose ; j'écris ou je relis le code, je le vérifie (exécution,
`df.describe()`, tests pytest) et je décide de garder, modifier ou rejeter.

| Date | Outil | Demande | Réponse reçue | Vérification | Décision |
|---|---|---|---|---|---|
| 30/10/2026 | Claude | Comparer deux jeux de données (Ford, Student Performance) | Avantages / inconvénients de chacun | Lecture des colonnes des deux CSV | Ford retenu (sujet concret, 8 variables) |
| 30/10/2026 | Claude | Comment explorer le CSV (taille, types, valeurs manquantes) | `shape`, `dtypes`, `isna().sum()`, `describe()` | Exécution de `exploration.py` : 17 965 lignes, aucune valeur manquante | Gardé |
| 30/10/2026 | Claude | Repérer les valeurs aberrantes | Lire min/max de `describe()` | `describe()` : année max 2060, cylindrée min 0 | Suppression de ces lignes (52 au total) |
| 30/10/2026 | Claude | Les `mpg` très élevés sont-ils des erreurs ? | Afficher les lignes `mpg > 100` | 5 Kuga Hybrid à 201,8 : valeur plausible pour une hybride | Gardées (non supprimées) |
| 30/10/2026 | Claude | Histogramme des prix | Code matplotlib (`hist`, titres, axes) | Image `exploration_prix.png` générée et lue | Gardé |
| 06/11/2026 | Claude | Structurer les classes de `donnees.py` (classe abstraite, héritage) | Squelette `Variable` / `VariableNumerique` / `VariableCategorielle` avec parties « à toi » | J'ai complété les méthodes, tests `test_donnees.py` passent | Gardé, complété moi-même |
| 06/11/2026 | Claude | Quel modèle et quelle métrique ? | Régression linéaire vs forêt aléatoire ; RMSE, R² | RMSE forêt 1 270 £ contre 4 754 £ pour la référence (prix moyen) | Forêt + RMSE seule |
| 06/11/2026 | Claude | Écrire la fonction `rmse` et un décorateur de chronométrage | Code avec `np.sqrt(np.mean(...))` et `@wraps` | Test : même résultat que `np.sqrt(mean_squared_error(...))` de scikit-learn | Gardé |
| 06/11/2026 | Claude | Sauvegarder / recharger le modèle | `joblib` + métadonnées JSON (colonnes encodées, RMSE) | Rechargement et prédiction testés dans l'application | Gardé |
| 06/11/2026 | Claude | Expliquer des lignes de code (`get_dummies`, `train_test_split`, `np.full`, `reindex`) | Commentaires ligne par ligne | Compris, commentaires ajoutés dans le code | Gardé |
| 06/11/2026 | Claude | Choisir l'interface | Tkinter vs Streamlit | Comparaison du code nécessaire | Streamlit (champs et graphique simples) |
| 06/11/2026 | Claude | Interface : saisies optionnelles et intervalles min/max | Valeurs typiques par modèle + combinaisons (`itertools.product`) donnant une fourchette | Essais dans l'application avec saisies vides, invalides, min > max | Gardé, messages d'erreur ajustés |
| 13/11/2026 | Claude | Compléter le README et ce journal | Rédaction à partir du code et des résultats | Relecture, commandes du README testées | Gardé après relecture |

## Ce que j'ai appris / limites de l'IA
- L'IA donne du code qui fonctionne souvent, mais il faut le relancer et le tester : les chiffres
  (RMSE, nombre de lignes supprimées) viennent de mes exécutions, pas de l'IA.
- Pour les valeurs aberrantes, l'IA propose des pistes ; la décision de garder ou supprimer dépend
  du sens des données (ex. `mpg` élevé plausible pour une hybride).
- J'ai demandé des explications plutôt que du code complet pour les parties à comprendre
  (classes, encodage, séparation train/test).
