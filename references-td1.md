# Références TD 1

Les 20 requêtes sont dans `refs/C01.sql` à `refs/C20.sql`. Elles sont exécutées en lecture seule sur `data/boutique.sqlite` et leurs résultats sont reportés dans `reference-td1.csv` par `fill_reference.py`.

## Conventions

- Montant : somme de `quantity_product * price`, en centimes HT (les prix de la base sont déjà HT). Pas de TVA, de remise ni de retour.
- Dates : la base est en UTC. Les bornes des questions sont comparées telles quelles, sans conversion : « minuit » signifie 00:00:00 UTC. Par exemple, le 2026-03-01 00:00:00 UTC correspond à 01:00 à Paris.
- Périodes : début inclus, fin exclue (`date >= début AND date < fin`).
- Âge : âge révolu, calculé avec le mois et le jour. On retire un an si l'anniversaire n'est pas encore passé à la date considérée, et le jour de l'anniversaire compte. Ainsi, au 2026-09-25, un client né le 2001-09-25 a 25 ans, alors qu'un client né le 2001-09-26 en a 24.
- Âge « à une date de référence » : l'âge est évalué à cette date, puis on compte toutes les commandes du client. Âge « à la commande » : l'âge est évalué à la date (UTC) de chaque commande.
- Aucun résultat : la requête renvoie 0 grâce à `COALESCE`, et non `NULL`.

## Explication par fichier

| Fichier | Ce que calcule la requête | Valeur (centimes) |
|---|---|---:|
| C01.sql | Toutes les commandes de mars à mai 2026 (du 2026-03-01 inclus au 2026-06-01 exclu). | 792 800 |
| C02.sql | Toutes les commandes des clients ayant exactement 25 ans le 2026-09-25 (nés du 2000-09-26 au 2001-09-25). | 590 320 |
| C03.sql | Produits a, b et c, commandes du premier semestre 2026. | 936 350 |
| C04.sql | Toutes les commandes de janvier à septembre 2026. Cette période couvre toute la base (du 06/01 au 20/09). | 2 826 250 |
| C05.sql | Commandes du 1er juin 2026 (du 2026-06-01 au 2026-06-02 exclu). | 38 480 |
| C06.sql | Commandes de l'année 2025. Il n'y en a aucune, donc 0. | 0 |
| C07.sql | Commandes du 31 mai 2026. | 13 970 |
| C08.sql | Comme C02, avec le 2026-09-24 comme date de référence (nés du 2000-09-25 au 2001-09-24). | 605 580 |
| C09.sql | Comme C02, avec le 2026-09-26 comme date de référence (nés du 2000-09-27 au 2001-09-26). | 487 980 |
| C10.sql | Lignes de commande passées alors que le client avait exactement 25 ans à la date de la commande. | 558 980 |
| C11.sql | Comme C02, avec le 2026-12-01 comme date de référence (nés du 2000-12-02 au 2001-12-01). | 446 690 |
| C12.sql | Produits a, b et c, sur toute la base. | 1 666 490 |
| C13.sql | Produits a et c seulement, commandes d'avril 2026. | 107 740 |
| C14.sql | Produits a, b et c, commandes d'octobre et novembre 2026. Il n'y en a aucune, donc 0. | 0 |
| C15.sql | Commandes de mars à mai 2026 des clients ayant 25 ans le 2026-09-25 (C01 et C02 combinés). | 168 680 |
| C16.sql | Produits a, b et c des clients ayant 25 ans le 2026-09-25, sans période. | 376 740 |
| C17.sql | Produits a, b et c, premier semestre 2026, clients ayant 25 ans le 2026-09-25. | 258 180 |
| C18.sql | Commandes de mai 2026 passées alors que le client avait 25 ans à la date de la commande. | 62 480 |
| C19.sql | Produit d, commandes de septembre 2026, clients ayant 25 ans le 2026-09-25. Une seule unité de d correspond. | 1 990 |
| C20.sql | Commandes de juin à août 2026. | 1 106 090 |

## Vérification

- Cohérence entre les questions : C04 est égal au CA total de la base. Chaque question combinée est inférieure ou égale aux questions simples qu'elle combine (C15 ≤ C01 et C02, C17 ≤ C16 et C03, C18 ≤ C10, etc.). C02, C08 et C09 donnent des valeurs différentes, ce qui confirme que le jour de naissance est bien pris en compte.
- Seconde méthode : `check_reference.py` recalcule les 20 valeurs en Python à partir des fichiers CSV, sans SQL. Il trouve 20 valeurs identiques sur 20 (sortie dans `verification-td1.txt`).
- Limite : les deux méthodes reposent sur les mêmes conventions (UTC, âge révolu, fin de période exclue). La comparaison avec les valeurs du professeur reste nécessaire.
- Les requêtes et les scripts ont été écrits avec l'aide d'une IA (Claude). Aucune valeur ne provient de la réponse d'un modèle.
