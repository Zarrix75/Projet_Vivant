# Projet_Vivant

# Readme


# Ecorps

**Ecorps** est un outil de monitoring de sites web développé en Python. Il permet de surveiller la disponibilité de services web internes et externes, de générer des alertes en cas d’indisponibilité et de conserver des journaux d’événements détaillés. L’outil est entièrement configurable et extensible.

---

## Fonctionnalités principales

- Vérification périodique de la disponibilité de sites web
- Envoi d’alertes (email ou via API) en cas d’indisponibilité
- Journalisation complète des événements (logs)
- Configuration des paramètres via un fichier YAML
- Vérification d’intégrité des pages (optionnelle)

---

## Prérequis

- Python 3.8 ou supérieur

## Installation

Clonez le dépôt puis installez les dépendances :

```bash
git clone https://github.com/ton-utilisateur/ecorps.git
cd ecorps
python -m pip install -r requirements.txt
```

## Utilisation

Lancez le script principal :

```bash
python src/main.py
```

---

## Arborescence du projet

Ecorps/
├── config/
│   └── config.yaml
├── src/
│   ├── main.py
│   ├── checker.py
│   ├── integrity.py
│   ├── notifier.py
│   ├── logger.py
│   └── utils.py
├── logs/
│   └── monitoring.log
├── tests/
│   ├── test_checker.py
│   └── test_integrity.py
├── docs/
│   ├── README.md
│   ├── cahier_des_charges.md
│   ├── recette.md
│   ├── architecture.md
│   ├── manuel_installation.md
│   ├── manuel_utilisateur.md
│   └── changelog.md
├── requirements.txt
└── LICENSE

---

## Contribution

Les contributions sont les bienvenues ! Merci de soumettre une pull request ou d’ouvrir une issue.


