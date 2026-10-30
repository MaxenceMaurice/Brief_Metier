# CF-Tech — Gestion des formations

## 1. Présentation du projet

Ce projet consiste à développer une base de données relationnelle pour le centre de formation CF-Tech.

Il vise à centraliser la gestion des utilisateurs, des salles, des sessions de formation et des inscriptions, afin de remplacer les fichiers Excel et l'ancien système de gestion devenu obsolètes.

## 2. Objectifs

- Centraliser les données du centre de formation.
- Gérer les utilisateurs et leurs rôles.
- Gérer les salles, leurs capacités d'accueil et leur disponibilité.
- Organiser les sessions de formation en leur attribuant des formateurs.
- Gérer les inscriptions des apprenants.
- Valider les données à l'aide de Pydantic.
- Gérer les évolutions de la base avec Alembic.
- Faciliter le travail collaboratif avec Git et GitHub.

## 3. Installation et commandes utiles

### 2.1 Installation de l'environnement

cd ~/Brief_Metier
source .venv/bin/activate
pip install -r requierement.txt

### 2.2 Exécution des tests

python -m pytest -v --tb=short

### 2.3 Gestion des migrations avec Alembic

alembic history
alembic heads

### 2.4 Vérification de l'état du dépôt Git

git status

### 2.5 Lancement de l'interface Streamlit

streamlit run app_streamlit.py

## 4. Technologies utilisées

- **Python** : langage de programmation.
- **SQLite** : système de gestion de base de données.
- **SQLModel** : définition des modèles de données et interactions avec la base.
- **Pydantic** : validation des données.
- **Alembic** : gestion des migrations.
- **Git et GitHub** : gestion du code source et collaboration.
- **Mermaid** : création de diagrammes.

## 5. Modèle de données

Le projet repose sur quatre entités principales : les utilisateurs, les salles, les sessions et les inscriptions.

### 5.1 Utilisateurs

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

### 5.2 Salles

Chaque salle possède les attributs suivants :

- Identifiant.
- Nom unique et indexé.
- Capacité strictement positive.
- Localisation.
- Statut actif ou inactif.

### 5.3 Sessions de formation

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

### 5.4 Inscriptions

Chaque inscription associe un apprenant à une session au moyen de deux clés étrangères :

- `apprenant_id` : référence à l'apprenant.
- `session_id` : référence à la session.

Les autres attributs sont :

- Identifiant de l'inscription.
- Date d'inscription.
- Statut de l'inscription.

Les statuts possibles sont :

- `ENREGISTRE` : inscription enregistrée.
- `DESINSCRIT` : apprenant désinscrit.
- `EN_ATTENTE` : inscription en attente.

Le champ `presence` accepte une valeur booléenne ou `None`, permettant de représenter une présence renseignée ou encore indéterminée.

### 5.5 Diagramme

Le diagramme Mermaid définitif sera ajouté après vérification de l'ensemble des relations entre les tables.

## 6. Organisation du projet

```text
.
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── models/
│   ├── __init__.py
│   ├── inscription.py
│   ├── salle.py
│   ├── session.py
│   └── user.py
├── pages/
│   ├── 1_Users.py
│   ├── 2_Salles.py
│   ├── 3_Sessions.py
│   └── 4_Inscriptions.py
├── schemas/
│   ├── inscription_schemas.py
│   ├── session_schemas.py
│   └── user_schema.py
├── tests/
│   ├── test_inscription_service.py
│   ├── test_permissions.py
│   ├── test_salle_disponible.py
│   └── test_session_service.py
├── .gitignore
├── README.md
├── alembic.ini
├── app.py
├── database.py
├── demo.py
├── inscription_service.py
├── permissions.py
├── requierement.txt
├── salle_disponible.py
└── session_service.py
```

Les dossiers `__pycache__` et les fichiers `.pyc`, générés automatiquement par Python, ne sont pas représentés ici.

La base de données locale `database.db` n'est pas destinée à être partagée sur GitHub.

Git : création du `.gitignore` pour exclure les caches Python et la BDD locale.

### Rôle des principaux fichiers

| Fichier ou dossier | Description |
|---|---|
| `database.py` | Configuration de la connexion à la base de données. |
| `pages/` | Contient les différentes pages de l'application Streamlit. |
| `models/` | Définition des modèles de données. |
| `schemas/` | Définition des schémas de validation. |
| `alembic/` | Fichiers nécessaires à la gestion des migrations. |
| `tests/` | Contient des l'ensemble des scripts de tests. |
| `alembic.ini` | Configuration d'Alembic. |
| `requierement.txt` | Fichier de dépendances fourni par le formateur. |

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
- Contrôle des permissions et de la disponibilité des salles grâce à ces fonctions métier `check_permission()` et `is_salle_disponible()`, avec des exceptions personnalisées.

Les modèles définissent également plusieurs contraintes, notamment l'unicité des adresses e-mail et des noms de salles, les capacités strictement positives et le taux horaire non négatif.

L'ensemble des règles métier prévues par le cahier des charges, notamment les chevauchements de sessions et le respect de la capacité des salles, devra être vérifié dans les schémas et les tests avant d'être présenté comme entièrement implémenté.

## 8. Migrations de la base de données

Le projet utilise Alembic pour gérer les évolutions du schéma de la base de données.

 3 migrations créées et testées (upgrade/downgrade). Le champ de statut des sessions ayant été intégré dès la création de la table concernée, une migration supplémentaire n'avait pas été faite, résolu avec stamp et des tests sur une copie de la base de données.

Les fichiers de migration doivent encore être publiés sur le dépôt GitHub partagé. Cette section sera complétée après récupération et vérification des fichiers.

## 9. Installation et utilisation

Les instructions d'installation, de configuration de l'environnement Python et d'exécution du projet seront complétées après vérification des dépendances et des commandes utilisées par l'équipe.

La base SQLite locale n'est pas fournie sur le dépôt partagé.

## 10. Autres tests effectués et problèmes rencontrés

- 8 tests sur 8 réalisés et réussis dans le cadre du projet. Légère difficulté avec le fuseau horaire, corrigé avec UTC. Tests sur une BDD en mémoire pour protéger database.db.
- Streamlit : améliorations enregistrées, syntaxe vérifiée sans erreur (fonctionnement complet encore à tester).

## 11. Répartition du travail

### Maxence

- Mise en place de GitHub.
- Mise en place de la base de données.
- Réalisation des schémas et du diagramme de données.
- Utilisation et configuration d'Alembic pour les migrations.

### Benjamin

- Développement des classes relatives aux sessions, aux salles, aux utilisateurs et aux inscriptions.
- Utilisation de Pydantic pour la validation des données.

### Alexia

- Gestion de la création et des modifications du fichier README.md.
- Création du diaporama.

## 12. Installation et lancement des tests :

python -m pip install pytest
python -m pytest test_permissions.py test_salle_disponible.py -v

## 13. Évolutions possibles

- Développer une interface graphique ou web pour faciliter la gestion des données.
- Ajouter un tableau de bord pour visualiser les sessions, les inscriptions et l'occupation des salles.
- Compléter la documentation technique.
