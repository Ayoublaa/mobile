<div align="center">

<img src="https://img.shields.io/badge/Security-Platform-0A2342?style=for-the-badge&logoColor=white" />

# 🛡️ Mobile API Misuse Detector

**Plateforme de sécurité active pour la détection en temps réel des abus d'API mobiles, propulsée par le Machine Learning non supervisé.**

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-0A2342?style=flat-square)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square&logo=React&logoColor=black)](https://reactjs.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)

</div>

---

## 🎯 Points d'Évaluation (Pour le Professeur)

Afin de faciliter l'évaluation, voici les accès rapides aux 4 exigences principales du projet :
1. **[🎥 Vidéo de Démonstration](#-démonstration-vidéo)** : Scénario complet d'attaque, analyse et alertes.
2. **[🐳 Docker Compose](#-docker-compose--installation--lancement)** : Fichier `docker-compose.yml` prêt à l'emploi pour lancer le Backend et le Frontend.
3. **[📱 Analyse du Manifest Android](#-moteur-ia--analyse-du-manifest)** : Parsing dynamique des fichiers `AndroidManifest.xml` (permissions, composants exportés).
4. **[📊 Métriques des Modèles IA](#-métriques-des-modèles-ia--benchmark)** : Évaluation de la Précision, du Recall et du F1-Score via notre moteur de benchmark interne.

---

## 📋 Table des matières

- [📁 Structure du projet](#-structure-du-projet)
- [⚙️ Prérequis](#️-prérequis)
- [🚀 Installation & Lancement](#-installation--lancement)
- [✨ Fonctionnalités](#-fonctionnalités)
- [🤖 Moteur IA & Analyse du Manifest](#-moteur-ia--analyse-du-manifest)
- [📊 Métriques des Modèles IA & Benchmark](#-métriques-des-modèles-ia--benchmark)
- [🎥 Démonstration Vidéo](#-démonstration-vidéo)
- [📸 Interface Dashboard](#-interface-dashboard)
- [🛑 Arrêt propre](#-arrêt-propre)
- [👥 Auteurs](#-auteurs)

---

## 📁 Structure du projet

```text
mobile-api-misuse-detector/
├── backend/
│   ├── main.py                 # API FastAPI (Ingestion, WebSockets)
│   ├── advanced_analytics.py   # Isolation Forest & Profilage
│   ├── clustering.py           # Clustering comportemental
│   ├── benchmark.py            # Moteur de benchmark vs Fail2ban
│   └── parser.py               # Parsers pour logs Nginx, Express, Spring
├── frontend/
│   └── src/                    # Dashboard React temps réel
├── docker-compose.yml          # Déploiement multi-conteneurs
├── report.tex                  # Rapport académique (SoftwareX)
└── README.md                   # Documentation du projet
```

---

## ⚙️ Prérequis

- **Docker** et **Docker Compose** installés sur votre machine (méthode recommandée).
- Ou environnement local avec **Python 3.9+** et **Node.js 18+**.
- Ports `8000` (Backend) et `5173` (Frontend) disponibles.

---

## 🚀 Docker Compose : Installation & Lancement

Le projet est entièrement conteneurisé via Docker pour une mise en route rapide et reproductible.

### 1. Cloner le projet
```bash
git clone https://github.com/Ayoublaa/mobile.git
cd mobile
```

### 2. Configurer les variables d'environnement (Optionnel)
Pour activer les alertes de sécurité par email, créez un fichier `.env` dans le dossier `backend/` :
```env
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app
EMAIL_FROM=votre-email@gmail.com
EMAIL_TO=admin@example.com
```

### 3. Lancer avec Docker Compose
À la racine du projet, exécutez :
```bash
docker compose up --build -d
```

- **Dashboard UI :** [http://localhost:5173](http://localhost:5173)
- **API Swagger :** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| **Ingestion Multi-Format** | Support natif des logs Nginx, Express, et Spring via upload drag-and-drop. |
| **Détection Zéro-Jour** | Utilisation d'Isolation Forest pour repérer les anomalies hors-normes sans règles prédéfinies. |
| **Alertes Actives** | Envoi automatique d'emails en cas de détection critique (configurable via le dashboard). |
| **Clustering Comportemental**| Regroupement des IPs suspectes pour identifier les types d'attaques (Scanners, Brute-force). |
| **Recommandations IA** | Propositions d'actions de remédiation générées dynamiquement selon le profil de l'attaque. |

---

## 🤖 Moteur IA & Analyse du Manifest

Le moteur d'intelligence artificielle de notre plateforme repose sur une architecture hybride :

| Composant | Rôle |
|------------|------|
| **Isolation Forest** | Algorithme de Machine Learning non supervisé qui isole les anomalies (outliers) pour repérer les pics de requêtes et les comportements furtifs. |
| **Clustering Comportemental** | Segmentation des attaquants en profils comportementaux basés sur le taux d'erreur 401, les endpoints touchés, le volume, et l'usage mobile. |
| **Analyse Heuristique** | Analyse ciblée pour la détection formelle de spikes et d'énumération de routes d'API. |
| **📱 Analyse du Manifest Android** | Module backend exclusif (`/analyze-manifest`) pour parser les fichiers `AndroidManifest.xml`, détecter les composants exportés, et évaluer le score de risque des permissions dangereuses (ex: `READ_CONTACTS`, `SEND_SMS`). |

---

## 📊 Métriques des Modèles IA & Benchmark

Le projet intègre un moteur d'évaluation (accessible via l'endpoint `GET /benchmark`) qui simule divers scénarios d'attaques (Bruteforce, Énumération, Flood 500, trafic légitime) et compare les performances de notre système d'IA à une approche classique par seuils statiques (de type Fail2ban).

**Métriques d'IA Obtenues :**
- **Precision nettement supérieure** (réduction quasi-totale des faux positifs sur les adresses IP partagées/NAT).
- **Meilleur Recall** (détection efficace des attaques "Low-and-Slow" ou furtives qui passent sous le radar des limites de requêtes standards).
- **F1-Score optimisé** grâce à la flexibilité de l'apprentissage automatique qui s'adapte à l'évolution de la distribution du trafic.

---

## 🎥 Démonstration Vidéo

Voici la vidéo de démonstration complète de la plateforme (du lancement via Docker jusqu'à l'analyse IA et la réception des alertes) :

> ⚠️ *(Placez votre fichier `demo.mp4` ou le lien YouTube ici)*
<div align="center">
  <video src="https://github.com/user-attachments/assets/votre-video-demo.mp4" width="800" controls="controls"></video>
</div>

---

## 📸 Interface Dashboard

**1. Dashboard Principal**  
*Vue d'ensemble en temps réel de la sécurité et des métriques du système.*
<img src="scrennshot/dashboard.png" width="100%" alt="Dashboard Overview" />

<br/>

**2. Analyse Visuelle (Heatmaps & Timeline)**  
*Visualisation approfondie des comportements suspects.*
<img src="scrennshot/graphs.png" width="100%" alt="Anomaly Analytics" />

<br/>

**3. Journal des Alertes et Emails**  
*Traçabilité complète et notifications instantanées pour les menaces critiques.*
<br/>
<img src="scrennshot/jouranldaletre.png" width="49%" alt="Alert Journal" /> <img src="scrennshot/email.png" width="49%" alt="Email Notifications" />

---

## 🛑 Arrêt propre

Pour arrêter proprement les services Docker :

```bash
# Arrêter les conteneurs
docker compose down

# Arrêter les conteneurs et supprimer les volumes (historique)
docker compose down -v
```

---

## 👥 Auteurs

Ce projet a été développé en tant que solution complète et moderne de cybersécurité.

- **Kaoutar Menacera**
- **Ayoub Laafar**

📄 *Un rapport de recherche académique complet de 14 pages (format SoftwareX) détaillant l'approche méthodologique et l'implémentation est disponible dans le fichier `report.tex`.*
