# CF-Tech — Gestion des formations

## 1. Présentation du projet

Ce projet consiste à développer une base de données relationnelle pour le centre de formation CF-Tech.

Il vise à centraliser la gestion des utilisateurs, des salles, des sessions de formation et des inscriptions, afin de remplacer les fichiers Excel et l'ancien système de gestion.

## 2. Objectifs

- Centraliser les données du centre de formation.
- Gérer les utilisateurs et leurs rôles.
- Gérer les salles, leurs capacités et leur disponibilité.
- Organiser les sessions de formation et leurs formateurs.
- Gérer les inscriptions et le suivi des présences.
- Valider les données à l'aide de Pydantic.
- Gérer les évolutions de la base avec Alembic.
- Faciliter le travail collaboratif avec Git et GitHub.

## 3. Technologies utilisées

- **Python** : langage de programmation.
- **SQLite** : système de gestion de base de données.
- **SQLModel** : définition des modèles de données et interactions avec la base.
- **Pydantic** : validation des données.
- **Alembic** : gestion des migrations.
- **Git et GitHub** : gestion du code source et collaboration.
- **Mermaid** : création de diagrammes.

## 4. Modèle de données

Le projet repose sur quatre entités principales : les utilisateurs, les salles, les sessions et les inscriptions.

### 4.1 Utilisateurs

Le modèle utilisateur comprend des informations communes :

- Identifiant.
- Nom et prénom.
- Adresse e-mail unique.
- Date de création.
- Statut actif ou inactif.
- Rôle.

Quatre catégories d'utilisateurs sont définies :

- **Apprenant** : date de naissance, niveau d'études, téléphone, date d'inscription sur la plateforme et certification éventuelle.
- **Formateur** : spécialité, date d'embauche, taux horaire et biographie éventuelle.
- **Staff pédagogique** : poste, date de prise de fonction et responsabilités.
- **Administrateur** : niveau d'accès et date de promotion.

Les rôles possibles sont `apprenant`, `formateur`, `staff` et `admin`.

Les niveaux d'accès administrateur prévus sont `SUPERADMIN` et `ADMIN_STANDARD`.

Les responsabilités du staff pédagogique peuvent être enregistrées sous forme de données JSON.

### 4.2 Salles

Chaque salle possède les attributs suivants :

- Identifiant.
- Nom unique et indexé.
- Capacité strictement positive.
- Localisation.
- Statut actif ou inactif.

### 4.3 Sessions de formation

Chaque session comprend :

- Un titre.
- Une description facultative.
- Une date de début et une date de fin.
- Une capacité maximale strictement positive.
- Un statut.
- Une référence à la salle utilisée.
- Une référence au formateur responsable.

Les statuts définis dans le modèle sont :

- `OPEN` : session ouverte.
- `CLOSED` : session fermée.
- `ARCHIVED` : session archivée.

Les champs `salle_id` et `formateur_id` sont des clés étrangères qui relient chaque session à une salle et à un formateur.

Le schéma de création prévoit également un champ `prerequis`. Sa prise en charge dans le modèle de base de données reste à vérifier.

### 4.4 Inscriptions

Chaque inscription associe un apprenant à une session au moyen de deux clés étrangères :

- `apprenant_id` : référence à l'apprenant.
- `session_id` : référence à la session.

Les autres attributs sont :

- Identifiant de l'inscription.
- Date d'inscription.
- Statut de l'inscription.
- Présence éventuelle de l'apprenant.

Les statuts possibles sont :

- `ENREGISTRE` : inscription enregistrée.
- `DESINSCRIT` : apprenant désinscrit.
- `EN_ATTENTE` : inscription en attente.

Le champ `presence` accepte une valeur booléenne ou `None`, permettant de représenter une présence renseignée ou encore indéterminée.

### 4.5 Diagramme

Le diagramme Mermaid définitif sera ajouté après vérification de l'ensemble des relations entre les tables.

## 5. Organisation du projet

```text
.
├── alembic.ini
├── database.py
├── seed.py
├── README.md
├── requierement.txt
├── .vscode/
│   └── settings.json
├── alembic/
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── models/
│   ├── inscription.py
│   ├── salle.py
│   ├── session.py
│   ├── user.py
│   └── __init__.py
└── schemas/
    ├── inscription_schemas.py
    ├── session_schemas.py
    └── user_schema.py
```

Les dossiers `__pycache__` et les fichiers `.pyc`, générés automatiquement par Python, ne sont pas représentés ici.

La base de données locale `database.db` n'est pas destinée à être partagée sur GitHub.

### Rôle des principaux fichiers

| Fichier ou dossier | Description |
|---|---|
| `database.py` | Configuration de la connexion à la base de données. |
| `seed.py` | Génération de données de démonstration. |
| `models/` | Définition des modèles de données. |
| `schemas/` | Définition des schémas de validation. |
| `alembic/` | Fichiers nécessaires à la gestion des migrations. |
| `alembic.ini` | Configuration d'Alembic. |
| `requierement.txt` | Fichier de dépendances fourni par le formateur. |

## 6. Données de démonstration

Le fichier `seed.py` permet de peupler la base avec des données de démonstration.

Le jeu de données généré comprend :

- 4 salles.
- 3 formateurs.
- 10 apprenants.
- 1 membre du staff pédagogique.
- 1 administrateur de niveau `SUPERADMIN`.
- 4 sessions de formation.
- Des inscriptions associant les apprenants à certaines sessions.

Certaines valeurs sont générées aléatoirement, notamment les noms et prénoms des apprenants, les capacités des salles et le choix des sessions pour les inscriptions.

Les dates des sessions sont calculées à partir de la date et de l'heure d'exécution du script.

Le script vérifie si une inscription existe déjà pour le couple apprenant-session choisi avant de l'ajouter. En revanche, il ne vérifie pas l'existence préalable des salles, utilisateurs ou sessions avant de les créer.

Ce script est destiné à préparer des données de démonstration ; il ne remplace pas les validations métier.

## 7. Validation des données

Les schémas du dossier `schemas/` utilisent Pydantic pour définir les données attendues lors de la création ou de la mise à jour de certaines entités.

Les contrôles prévus dans les extraits fournis comprennent :

- La validation du format des adresses e-mail avec `EmailStr`.
- Des contraintes de longueur pour les noms et prénoms, à confirmer après correction du schéma.
- Un contrôle de l'âge minimal des apprenants.
- Un contrôle du format des numéros de téléphone.
- Un contrôle empêchant une date d'embauche future.
- Un contrôle imposant une date de fin postérieure à la date de début d'une session.
- Des contraintes sur les identifiants d'inscription.

Les modèles définissent également plusieurs contraintes, notamment l'unicité des adresses e-mail et des noms de salles, les capacités strictement positives et le taux horaire non négatif.

L'ensemble des règles métier prévues par le cahier des charges, notamment les chevauchements de sessions et le respect de la capacité des salles, devra être vérifié dans les schémas et les tests avant d'être présenté comme entièrement implémenté.

## 8. Migrations de la base de données

Le projet utilise Alembic pour gérer les évolutions du schéma de la base de données.

Trois migrations ont été préparées par Maxence. Le champ de statut des sessions ayant été intégré dès la création initiale de la table concernée, une migration supplémentaire n'a pas été nécessaire pour cet ajout.

Les fichiers de migration doivent encore être publiés sur le dépôt GitHub partagé. Cette section sera complétée après récupération et vérification des fichiers.

## 9. Installation et utilisation

Les instructions d'installation, de configuration de l'environnement Python et d'exécution du projet seront complétées après vérification des dépendances et des commandes utilisées par l'équipe.

La base SQLite locale n'est pas fournie sur le dépôt partagé.

## 10. Tests

Des tests ont été réalisés dans le cadre du projet. Les fichiers concernés, les scénarios couverts et les commandes d'exécution restent à préciser.

## 11. Répartition du travail

### Maxence

- Mise en place de GitHub.
- Mise en place de la base de données.
- Réalisation des schémas et du diagramme de données.
- Utilisation et configuration d'Alembic pour les migrations.

### Benjamin

- Développement des classes relatives aux sessions, aux salles, aux utilisateurs et aux inscriptions.
- Utilisation de Pydantic pour la validation des données.

### Autre contribution

À compléter avec les tâches réalisées par le troisième membre de l'équipe.

## 12. Évolutions possibles

- Développer une interface graphique ou web pour faciliter la gestion des données.
- Ajouter un tableau de bord pour visualiser les sessions, les inscriptions et l'occupation des salles.
- Compléter la documentation technique et les procédures de test.
