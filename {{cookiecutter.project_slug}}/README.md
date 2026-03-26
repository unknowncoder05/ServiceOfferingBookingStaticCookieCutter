# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

Full-stack web application with a **Django REST + WebSocket backend**, a **React 19 + TypeScript frontend**, **Celery** for background tasks, **PostgreSQL**, and **Redis**.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python {{ cookiecutter.python_version }}, Django REST Framework, Django Channels, Celery |
| Frontend | React 19, TypeScript, Redux Toolkit, Tailwind CSS, React Router |
| Database | PostgreSQL 15 |
| Cache / Broker | Redis 7 |
| Container | Docker Compose (local + production) |
| Infrastructure | AWS ECS Fargate, RDS, ElastiCache, S3, CloudFront (Terraform) |

## Local Development

```bash
# 1. Copy env files and fill in values
cp -r BackEndApi/.envs.example/.local BackEndApi/.envs/.local

# 2. Build and start all services
cd BackEndApi
make build
make migrate
make up
```

Services:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1/
- **Django Admin**: http://localhost:8000/`$ADMIN_URL`/
- **Celery**: running in background (no port)

## Architecture

```
{{ cookiecutter.project_slug }}/
├── BackEndApi/          # Django backend
│   ├── src/
│   │   ├── api/
│   │   │   ├── items/  # Example CRUD module — copy this pattern for new modules
│   │   │   ├── users/  # Authentication, profiles, GitHub OAuth
│   │   │   ├── ws/     # WebSocket consumer
│   │   │   └── utils/  # Shared utilities (health check, keep-alive)
│   │   └── config/     # Django settings, URLs, Celery config
│   ├── compose/
│   │   ├── local/      # Local Docker config (Django, Celery, Nginx)
│   │   └── production/ # Production Docker config
│   └── requirements/   # base.txt · local.txt · production.txt
├── frontend/            # React frontend
│   └── src/
│       ├── components/ # Reusable UI components
│       ├── pages/      # Page components (one file per route)
│       ├── store/      # Redux slices and async thunks
│       ├── services/   # API client (Axios)
│       ├── context/    # React context providers (ThemeContext, etc.)
│       └── config/     # Environment config
├── terraform/          # Infrastructure as Code
└── projectmaker.yml    # ProjectMaker deployment config
```

## Frontend Routes

All routes are defined in `frontend/src/App.tsx`.

| Route | Auth required | Component |
|---|---|---|
| `/login` | No | `AuthPage` |
| `/signup` | No | `AuthPage` |
| `/verify` | No | `VerifyAccount` |
| `/verify-login` | No | `VerifyLogin` |
| `/dashboard` | Yes | `Dashboard` |
| `/items` | Yes | `ItemsPage` |
| `/items/:id` | Yes | `ItemsPage` |
| `/settings` | Yes | `SettingsPage` |
| `/server-down` | No | `ServerDown` |
| `/start-server` | No | `ServerStartPage` |

## Backend API Endpoints

Base path is configured by `DJANGO_API_URI` env var (default `/api/v1`).

| Endpoint | Module | Description |
|---|---|---|
| `GET <API>/health/` | utils | Health check (no auth) |
| `GET <API>/keep-alive/` | utils | Keep-alive ping (no auth) |
| `POST <API>/auth/login/` | users | Obtain JWT tokens |
| `POST <API>/auth/signup/` | users | Register new user |
| `POST <API>/auth/token/refresh/` | users | Refresh access token |
| `GET/PUT <API>/users/me/` | users | Current user profile |
| `GET/POST <API>/items/` | items | List / create items |
| `GET/PUT/PATCH/DELETE <API>/items/{id}/` | items | Item detail |

WebSocket endpoint: `ws://<host>/ws/` (JWT auth on connect).

## Adding a New Module

1. Create `BackEndApi/src/api/<module>/` following the `items/` module pattern
2. Add to `INSTALLED_APPS` in `BackEndApi/src/config/settings/base.py`
3. Add URL include in `BackEndApi/src/config/urls.py`
4. Add a Redux slice in `frontend/src/store/<module>Slice.ts`
5. Add page components in `frontend/src/pages/`
6. Register route in `frontend/src/App.tsx`

## Useful Commands

```bash
# From BackEndApi/
make build          # Build Docker images
make up             # Start all services
make down           # Stop all services
make migrate        # Run Django migrations
make makemigrations # Create new migration files
make test           # Run pytest
make shell          # Django shell
make logs           # Tail container logs

# ProjectMaker deployment commands (from UI or CLI)
migrate             # python manage.py migrate --noinput
collectstatic       # python manage.py collectstatic --noinput
createsuperuser     # python manage.py createsuperuser
test                # pytest
```

## Environment Variables

Environment variables are split into three files per environment:

```
BackEndApi/.envs/{env}/
├── .django   # Django settings (SECRET_KEY, DEBUG, ADMIN_URL, etc.)
├── .db       # PostgreSQL credentials
└── .cloud    # AWS / S3 / external service credentials
```

See `projectmaker.yml` for the full schema with labels and descriptions.

---

## Codebase Status

### Tech Stack
- **Backend**: Python {{ cookiecutter.python_version }}, Django REST Framework, Django Channels, Celery + Redis
- **Frontend**: React 19, TypeScript, Redux Toolkit, Tailwind CSS
- **Database**: PostgreSQL 15, Redis 7
- **Deployment**: Docker Compose, AWS ECS (Terraform)

### Implemented Features
- [x] JWT authentication (login, signup, token refresh) — `api/users/`
- [x] Account verification flow — `api/users/`
- [x] GitHub OAuth integration — `api/users/`
- [x] WebSocket consumer with JWT auth — `api/ws/consumers.py`
- [x] Background task processing (Celery + Redis) — `api/items/tasks.py`
- [x] Example CRUD module (`items`) with ViewSet, serializers, service layer, tests — `api/items/`
- [x] S3 file upload integration — `api/utils/`
- [x] Health check + keep-alive endpoints — `api/utils/views.py`
- [x] React auth flow (login/signup/verify) — `frontend/src/pages/AuthPage.tsx`
- [x] Redux auth state with JWT persistence — `frontend/src/store/authSlice.ts`
- [x] Dark mode toggle (ThemeContext) — `frontend/src/context/ThemeContext.tsx`
- [x] Backend health polling + server start page — `frontend/src/services/BackendManager.ts`
- [x] Items CRUD UI — `frontend/src/pages/ItemsPage.tsx`
- [x] User settings page — `frontend/src/pages/SettingsPage.tsx`
- [x] i18n support (EN/ES) — `frontend/src/i18n/`

### Architecture Notes
- New Django modules go in `BackEndApi/src/api/<module>/` — copy the `items/` module pattern
- New frontend pages go in `frontend/src/pages/` with a matching route in `App.tsx`
- All business logic belongs in `services.py` (backend) or Redux thunks (frontend) — keep views thin
- WebSocket messages use `channel_layer.group_send` from Celery tasks; consumer is in `api/ws/`

### API Endpoints
- See "Backend API Endpoints" table above

### Data Models
- `User` — extended Django user with profile fields (`api/users/models.py`)
- `Item` — example CRUD model with status and archive fields (`api/items/models.py`)

### Known Issues / TODOs
- (none — add items here as you work on the project)
