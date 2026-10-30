30/10/2026

| Choix | Options envisagées | Choix retenu et justification | Validé (date) |
|---|---|---|---|
| Jeu de données | Ford, Student Performance | Ford : 8 variables, sujet concret | |


| Nettoyage : années | Garder tout / supprimer année > 2026 | Suppression des années > 2026 (ex. 2060) : impossible pour une voiture d'occasion | |
| Nettoyage : cylindrée | Garder / supprimer engineSize = 0 | Suppression des cylindrées à 0 : valeur invalide (une voiture a un moteur) | |

| Cible et métrique | RMSE, R² | Prix, RMSE seule : erreur en £ plus simple que proportions entre 0 et 1 | |
| Modèle | Linéaire, forêt | Forêt aléatoire : relations non linéaires | |
| Référence | Moyenne, médiane | Prix moyen | |
| Entrées | Tout obligatoire ou non | Seul le modèle de voiture obligatoire | |

| mpg élevé (201,8) | Garder ou retirer | Gardé : 5 Kuga Hybrid, valeur plausible | |