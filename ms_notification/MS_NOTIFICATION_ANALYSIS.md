# MS Notification — Documentation & Guide de démarrage

## Vue d'ensemble

| Propriété | Valeur |
|-----------|--------|
| Framework | Django 4.2 |
| Langage | Python 3.11 |
| Base de données | PostgreSQL |
| Port | 8086 |
| Protocole | HTTP (REST) + WebSocket |
| Enregistrement | Eureka Server |

---

## Architecture

```
MS Métiers (Spring Boot)
gestion_revenue │ depense │ objectifs │ reclamations │ forum
                        │
                   RabbitMQ :5672
                   Exchange: notification.exchange
                   Queue: notification.queue
                        │
              MS Notification (Django)
              ┌─────────────────────┐
              │  rabbit_consumer.py │ ← écoute RabbitMQ
              │  Daphne (ASGI)      │ ← WebSocket + REST
              │  PostgreSQL         │ ← stockage
              │  Redis :6379        │ ← channel layer WebSocket
              └─────────────────────┘
```

---

## Prérequis

### Services obligatoires à lancer AVANT le MS

| Service | Port | Rôle |
|---------|------|------|
| **Eureka Server** | 8761 | Registre des services |
| **RabbitMQ** | 5672 / 15672 | Broker de messages |
| **Redis** | 6379 | Channel layer WebSocket |
| **PostgreSQL** | 5432 | Base de données |

### Vérifications avant démarrage

```bash
# RabbitMQ
netstat -an | findstr 5672
# → doit afficher LISTENING

# Redis
netstat -an | findstr 6379
# → doit afficher LISTENING

# PostgreSQL
netstat -an | findstr 5432
# → doit afficher LISTENING
```

---

## Installation (première fois uniquement)

### 1. Créer l'environnement virtuel

```bash
cd "C:\...\ms_notification"
python -m venv myenv
myenv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Créer la base de données PostgreSQL

Via pgAdmin :
- Clic droit sur Databases → Create → Database
- Nom : `ms_notification_db`

Ou via psql :
```sql
CREATE DATABASE ms_notification_db;
```

### 4. Appliquer les migrations

```bash
cd ms_notification
python manage.py makemigrations notifications
python manage.py migrate
```

---

## Démarrage (usage quotidien)

### Terminal 1 — Activer l'environnement virtuel

```powershell
cd "C:\Users\ousse\OneDrive\Desktop\Money Minder MS\ms_notification"
myenv\Scripts\Activate.ps1
cd ms_notification
```

### Terminal 2 — Lancer Daphne (serveur HTTP + WebSocket)

```powershell
$env:PYTHONPATH = "C:\Users\ousse\OneDrive\Desktop\Money Minder MS\ms_notification\ms_notification"
daphne -p 8086 ms_notification.asgi:application
```

Résultat attendu :
```
Starting server at tcp:port=8086
```

### Terminal 3 — Lancer le consommateur RabbitMQ

```powershell
$env:PYTHONPATH = "C:\Users\ousse\OneDrive\Desktop\Money Minder MS\ms_notification\ms_notification"
python notifications/rabbit_consumer.py
```

Résultat attendu :
```
[✓] Enregistré sur Eureka : ms-notification:8086
[*] MS Notification en écoute sur RabbitMQ...
```

---

## Ordre de lancement global

| Ordre | Service | Port | Comment |
|-------|---------|------|---------|
| 1 | Eureka Server | 8761 | IntelliJ |
| 2 | Config Server | 8888 | IntelliJ |
| 3 | RabbitMQ | 5672 | Déjà installé comme service Windows |
| 4 | Redis | 6379 | Déjà installé comme service Windows |
| 5 | PostgreSQL | 5432 | Déjà installé comme service Windows |
| 6 | MS métiers Spring Boot | 8081–8085 | IntelliJ |
| 7 | Daphne (Django) | 8086 | Terminal 2 |
| 8 | rabbit_consumer.py | — | Terminal 3 |
| 9 | API Gateway | 20000 | IntelliJ |

---

## Endpoints REST

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/notifications/` | Toutes les notifications |
| GET | `/api/notifications/?user_id=1` | Notifications d'un utilisateur |
| GET | `/api/notifications/unread-count/?user_id=1` | Nombre de non lues |
| PUT | `/api/notifications/1/read/` | Marquer une notif comme lue |
| PUT | `/api/notifications/read-all/?user_id=1` | Tout marquer comme lu |
| DELETE | `/api/notifications/1/` | Supprimer une notification |

---

## WebSocket

```
ws://localhost:8086/ws/notifications/{user_id}/
```

Exemple avec user_id = 1 :
```
ws://localhost:8086/ws/notifications/1/
```

Chaque fois qu'un MS publie un événement sur RabbitMQ, le client connecté reçoit en temps réel :
```json
{
  "id": 1,
  "message": "Nouveau revenu ajouté : Salaire (1500.0 DT)",
  "type": "notification.revenue.ajoute",
  "data": { "source": "Salaire", "montant": 1500.0 },
  "is_read": false,
  "timestamp": "2026-05-31T17:40:14.710868"
}
```

---

## Événements RabbitMQ supportés

| Routing Key | MS Source | Déclencheur |
|-------------|-----------|-------------|
| `notification.revenue.ajoute` | gestion_revenue | Ajout d'un revenu |
| `notification.depense.ajoutee` | depense | Ajout d'une dépense |
| `notification.objectif.atteint` | Gestion-Objectifs | Création d'un objectif |
| `notification.reclamation.creee` | Reclamations | Création d'une réclamation |
| `notification.post.cree` | gestion-forum | Publication d'un post |

---

## Structure du projet

```
ms_notification/
├── ms_notification/
│   ├── settings.py       ← configuration principale
│   ├── urls.py           ← routes HTTP
│   ├── asgi.py           ← config WebSocket
│   └── wsgi.py
├── notifications/
│   ├── models.py         ← modèle Notification (PostgreSQL)
│   ├── serializers.py    ← sérialisation JSON
│   ├── views.py          ← endpoints REST
│   ├── urls.py           ← routes notifications
│   ├── consumers.py      ← WebSocket consumer
│   ├── routing.py        ← routes WebSocket
│   ├── rabbit_consumer.py← écoute RabbitMQ
│   └── apps.py           ← enregistrement Eureka
├── manage.py
└── requirements.txt
```

---

## Dépendances clés (requirements.txt)

```
django==4.2
djangorestframework==3.14.0
channels==3.0.5
channels-redis==3.4.1
daphne==3.0.2
psycopg2-binary==2.9.9
pika==1.3.2
py-eureka-client==0.11.12
django-cors-headers==4.3.1
```

> **Important** : `channels==3.0.5` et `channels-redis==3.4.1` sont obligatoires
> pour la compatibilité avec Redis 3.x sur Windows.

---

## Problèmes connus et solutions

| Erreur | Cause | Solution |
|--------|-------|---------|
| `unknown command 'HELLO'` | Redis 3.x incompatible avec channels-redis 4.x | Utiliser `channels-redis==3.4.1` |
| `No module named 'ms_notification'` | PYTHONPATH incorrect | Définir `$env:PYTHONPATH` avant de lancer |
| `relation notifications_notification n'existe pas` | Migrations non appliquées | `python manage.py migrate` |
| Notifications en doublon | Messages accumulés dans RabbitMQ | Purger la queue via `http://localhost:15672` |
| `basic_nack` en boucle | `requeue=True` par défaut | Utiliser `requeue=False` dans `basic_nack` |
