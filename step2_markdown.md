# Appels aux modèles (TD 1, étape 2)

Les 5 modèles ont reçu les 20 questions le 21/10/2026, via `skeleton-multi-llm-en.py --run`. Les lignes brutes sont fusionnées dans `traces-td1.csv` par `merge_traces.py`, sans aucune modification. Les fichiers sources (`state-*.jsonl` et `traces-*.csv`) sont conservés.

## Paramètres

- Prompt identique pour les 5 modèles. Chaque question a une seule empreinte (`prompt_sha256`), commune aux 5 modèles.
- Température 0, sortie plafonnée, délai d'attente de 45 s.
- Une seule requête à la fois pour le sous-groupe, avec au moins 3 s entre deux requêtes.
- Au plus une relance par cellule, uniquement pour une erreur temporaire (429, délai dépassé, erreur 5xx). La relance est gérée par le fichier `--state`.
- Références : `reference-td1.csv` (voir `references-td1.md`).

## Répartition et résultats

| Lettre | Modèle (identifiant exact) | Accès | Opérateur | Fichiers | Correct | Remarques |
|---|---|---|---|---|---:|---|
| A | `openai/gpt-oss-120b` | Groq | Axel | `state-A.jsonl`, `traces-A.csv` | 20/20 | Aucune relance |
| B | `openai/gpt-oss-20b` | Groq | Axel | `state-B.jsonl`, `traces-B.csv` | 18/20 | C02 et C11 incorrects. C20 : HTTP 429, puis relance réussie |
| C | `cohere/north-mini-code:free` | OpenRouter (compte d'Axel) | Axel | `state-C.jsonl`, `traces-C.csv` | 12/20 | 6 incorrects, 2 SQL invalides. `--pause 4` |
| D | `qwen/qwen3.8-27b` | Groq | Axel | `state-D.jsonl`, `traces-D.csv` | 15/20 | C10, C15, C16, C17 et C19 incorrects. `--pause 8` |
| E | `dots-studio/dots-3-note-preview:free` | OpenRouter (compte de Léo) | Léo | `state-E.jsonl`, `traces-E.csv` | _à compléter_ | `--pause 4` |

Le détail de chaque erreur se trouve dans `model-question-comparison-en.csv`.

## Décompte des appels

| Type | Groq | OpenRouter |
|---|---:|---:|
| Appels initiaux (base de 100) | 60 | 40 |
| Relances | 1 (B, C20) | _à compléter (E)_ |
| Vérifications d'accès (`check_access.py`, avant la séance) | 3 par membre l'ayant lancé | 2 par membre l'ayant lancé |

## Écarts par rapport au protocole

- A, B, C et D ont été lancés par le même membre, alors que le protocole prévoit un opérateur par modèle. C et E sont bien passés par deux comptes OpenRouter distincts.
- La pause entre requêtes a été allongée, ce que le protocole autorise puisqu'il impose seulement un minimum de 3 s :
  - pour D, `--pause 8`, après le 429 de B (limite Groq de 8 000 tokens par minute ; le message d'erreur indiquait 7 190 tokens utilisés pour 1 052 demandés) ;
  - pour C et E, `--pause 4`, pour rester sous la limite d'environ 20 requêtes par minute des modèles gratuits d'OpenRouter.
- Ces pauses ne changent ni le prompt ni les paramètres du modèle. Elles n'affectent que l'espacement des appels.

## Événement à signaler

B, question C20 : la première tentative a reçu un **HTTP 429** (limite de débit), sans valeur produite. Le script a relancé automatiquement, et la seconde tentative est correcte. Les deux tentatives figurent dans les traces : il s'agit d'un échec d'accès, pas d'une mauvaise réponse.
