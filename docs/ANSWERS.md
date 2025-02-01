# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_

### Étape 1:
Mon choix d’environnement virtuel était entre venv (built-in de Python) ou conda. Dans ce projet spécifique, puisque nous n’avons pas besoin de librairies deep learning (TensorFlow ou PyTorch), venv est un choix plus simple et efficace, et ne nécessite pas d'installation de dépendances. Ça évite la surcharge d’outils supplémentaires.

Si l'implémentation du système de recommendation était nécessaire dans ce projet, conda aurait été un choix plus optimal pour ses capacités de gestion d'installation de bibliothèque plus lourdes comme TensorFlow et Pytorch.

### Étape 2:
#### retrieve_data.py
Les fonctions data_tracks(), data_users() et data_listen_history() sont responsables de l'extraction des 3 différentes sources de données de l'API (Tracks, Users, Listen History). Elles utilisent la bibliothèque requests pour faire des requêtes HTTP et chercher les données en format JSON. J'ai choisi la bibliothèque requests pour sa simplicité d'utilisation.

La fonction data_types_check() est une fonction pour valider les types de données reçues, une fois transformer en dataframe. Elle contient un dictionnaire des types attendus et vérifie ques les types des données respectent ces formats.

La fonction retrieve_data() gère, à l'aide de la bibliothèque Pandas, la transformation des données JSON en dataframe. Les dataframes sont ensuite nettoyés et fusionnés ensemble afin d'obtenir une seule table. Une fois combinées et traitées, les données sont stockées localement dans un fichier CSV.

#### main.py
Pour la portion d'automatisation du flux de données quotidienne, j'ai opté pour un simple scheduler à l'aide de datetime. J'ai fait ce choix afin d'éviter l'installation de dépendances supplémentaires
**Je n'étais pas certain si l'installation de dépendances était une contrainte ou non, donc j'ai choisi une option qui ne la nécessite pas. Sinon, j'aurais potentiellement utilisé la bibliothèque schedule. 

La fonction run_data_retrieval(), quand appelée, sert à exécuter retrieve_data.py. 

La fonction schedule() est une fonction qui, en utilisant datetime, appelle la fonction run_data_retrieval() chaque jour à midi. Elle est executée dans un thread parallèle afin de ne pas interrompre l'API.

### Étape 3
Les tests unitaires rajoutés englobent en général les erreurs potentiels dans le fichier retrieve_data.py. Il est possible de rajouter d'autres tests comme un API request qui prend trop longtemps (timeout), un URL invalide, etc. Par contre, avec la limite de temps (3 à 5 heures), j'ai opté pour des cas plus critiques.

1. Le test test_listen_history_status_code_200 sert à vérifier si la fonction data_lsiten_history retourne correctement les données lorsque le statut de la réponse HTTP est un succès, donc 200.

2. le test test_listen_history_status_code_400 vérifie si la gestion d'erreur quand le statut de la réponse HTTP est un échec, donc 400.

3. Le test test_retrieve_data sert à vérifier si la fonction retrieve_data crée un fichier CSV avec les données attendues. Il simule les réponses de tracks, users et listen_history et vérifie si les données sont bien écrites dans le CSV.

4. Le test test_retrieve_data_handle_duplicates vérifie que retrieve_data gère correctement les duplicates.

5. Le test_invalid_types vérifie que retrieve_data gère les types de données invalides. Il simule des réponses avec des types incorrrects pour les données afin d'assurer que le retour est une exception TypeError.

6. Le test test_retrieve_data_empty vérifie la gestion de la fonction retrieve_data lorsque les données retournées sont vides mais la structure est correcte. Il vérifie si le CSV généré est vide.

7. Le test test_API_failure vérifie que la gestion dans le cas où le API échoue. Il vérifie qu'une exception est levée.


## Questions (étapes 4 à 7)

### Étape 4

Le choix idéal serait PostgreSQL. Les données des trois sources représent une relation plusieurs à plusieurs car Users est lié à Listen_History par les colonnes user_id (Users) et id (Listen_History), et Tracks ets lié à Listen_History par les colonnes id (Tracks) et track_id (Listen_History). C'est-à-dire que nous avons besoin d'un système relationnel SQL afin de bien gérer ces relations.

Mon choix s'est arrêté sur PostgreSQL car ça permet une meilleure gestion que MySQL pour les données en format JSON. PostgreSQL a une fonctionnalité JSONB qui offre une indexation des données plus efficace que MySQL.

De plus, en considérant l'évolutivité du projet, PostgreSQL a une meilleure capacité plus grande que MySQL pour des environnements de grandes entreprises qui nécessites des fonctionnalités plus complexes dans la gestion de données. 

Donc, PostgreSQL est le meilleur choix car elle offre une gestion plus simple et efficace, elle fonctionne bien avec des requêtes SQL complexes, et elle a une plus grande flexibilité pour la manipulation de données JSON que MySQL.

### Étape 5

Les tests unitaires sont un bon départ afin d'identifier des problèmes dans la logique du code et du flux des données. Par contre, il serait pertinent de rajouter des tests d'intégration qui vérifient que toutes les étapes du pipeline fonctionnent ensemble correctement. Nous pouvons créer des tests avec des données de test similaires au données de production, en simulant un scénario réel du début à la fin, afin de détecter des bugs dans le workflow de l'application. Nous pouvons aussi vérifier que l'API fournit les bonnes données, que la transformation se fasse correctement, et que le stockage n'ait aucun bug. Nous pouvons ensuite automatiser le tout avec un framework CI/CD pour assurer que le pipeline fonctionne correctement avant chaque mis-à-jour.

Une autre option pertinente serait d'implémenter du monitoring et logging afin de détecter d'autres types de problèmes comme les ralentissements et les comportements inattendus. Chaque étape du pipeline (Ex.: requêtes API, temps d'exécution, taux de succès, etc.) serait enregistrer afin de détecter des problèmes potentiels. Une fois un problème détecté ou un seuil critique (Ex.: temps d'exécution trop long) est atteint, une alerte peut être déclenché. Il serait pertinent d'avoir toutes ces données dans un dashboard afin de visualiser le tout.


### Étape 6

L'automatisation du calcul des recommandations contient plusieurs étapes. La première est dans l'automatisation du flux de données que nous avons précédemment complété, avec l'ajout d'un stockage dans une base de données idéale (PostgreSQL pour ce projet). Ensuite, avec un script similaire à lui du scheduler (ou une option plus idéale avec d'autres bibliothèques), nous pouvons automatiser l'ingestion des données traités dans un modèle de recommandation quelconque qui serait idéal pour résultats conclusifs de recommandation. Similaire à spotify, des algorithmes que nous pourrions utiliser serait matrix factorization qui transforme les intéractions user-item en features,ou KNN qui trouve des utilisateurs avec des intéractions similaires. Une fois les recommandations faites, les résultats devraient être stockés dans PostgreSQL afin de les analyser et/ou réutiliser pour d'autres recommandations (Ex.: Pour KNN). Une fois le pipeline completé, il serait très pertinent d'appliquer les solutions de l'étape 5 pour assurer un bon fonctionnement du pipeline. La performance du modèle doit toujours être surveillée afin de savoir quand le réentrainer.

### Étape 7

Idéallement, on réentraine un modèle quand sa performance diminue, ou après une certaine période de temps afin d'assurer que le modèle soit mis à jour avec les nouvelles données. Il faut mettre en place des seuils (Ex.: 2 semaines, performance passe sous un certain seuil de réussite) pour déclencher automatiquement le réentrainement (soit un scheduler, soit une variable de performance qui atteint un seuil spécifique). Pour réentrainer un modèle, nous suivons le même processus que l'entrainement initial d'un modèle. Nous commencons dabord avec les données mis à jour quotidiennement que nous utilisons pour réentrainer le modèle en question afin d'obtenir des nouveaux résultats de recommendation. Nous pouvons ensuite comparer les résultats entre les anciennces recommendations et les nouvelles pour s'assurer qu'il y a eu une amélioration. La prochaine étape serait de stocker les nouvelles recommendations dans PostgreSQL.
