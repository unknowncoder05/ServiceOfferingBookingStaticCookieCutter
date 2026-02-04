# Full-Stack Web Application Cookiecutter Template

A production-ready Cookiecutter template for full-stack web applications featuring:

- **Backend**: Django REST Framework with WebSocket support (Channels)
- **Frontend**: React 19 with Redux Toolkit and TypeScript
- **Infrastructure**: AWS (Terraform) with ECS, RDS, S3, CloudFront
- **DevOps**: Docker, CI/CD scripts, automated deployments
- **Optional**: AI integration (OpenAI/Anthropic)

## Quick Start

### Prerequisites

- Python 3.8+ with `cookiecutter` installed
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- AWS CLI (for deployment)
- Terraform (for infrastructure provisioning)

### Generate Your Project

```bash
# Install cookiecutter if you haven't already
pip install cookiecutter

# Generate project from this template
cookiecutter gh:unknowncoder05/BaseEphemeralProjectCookieCutter

# Or from a local directory
cookiecutter path/to/this/template
```

### Template Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `project_name` | My Project | Human-readable project name |
| `project_slug` | my_project | Python/directory-friendly name (auto-generated) |
| `project_slug_dashed` | my-project | URL/Docker-friendly name (auto-generated) |
| `description` | A full-stack web application | Project description |
| `author_name` | Your Name | Author's name |
| `author_email` | your@email.com | Author's email |
| `domain_name` | example.com | Production domain name |
| `aws_region` | us-east-1 | AWS region for deployment |
| `timezone` | America/New_York | Default timezone |
| `use_ai_integration` | y | Include AI SDK dependencies (y/n) |
| `python_version` | 3.11 | Python version for Docker |
| `node_version` | 20 | Node.js version for Docker |

## Generated Project Structure

```
{{cookiecutter.project_slug}}/
├── BackEndApi/              # Django REST backend
│   ├── src/
│   │   ├── api/            # API modules
│   │   │   ├── items/      # Example CRUD module
│   │   │   ├── users/      # Authentication
│   │   │   ├── ws/         # WebSocket handlers
│   │   │   └── utils/      # Shared utilities
│   │   └── config/         # Django settings
│   ├── compose/            # Docker configurations
│   ├── requirements/       # Python dependencies
│   └── local.yml          # Docker Compose (local)
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── store/         # Redux store
│   │   └── services/      # API services
│   └── package.json
├── terraform/             # Infrastructure as Code
│   ├── modules/          # Terraform modules
│   └── environments/     # Environment configs
├── scripts/              # Deployment scripts
├── Makefile             # Common commands
└── docs/                # Documentation
```

## After Generation

1. **Navigate to your project:**
   ```bash
   cd your_project_slug
   ```

2. **Configure environment variables:**
   ```bash
   # Copy example env files
   cp BackEndApi/.envs.example/.local/.django BackEndApi/.envs/.local/.django
   cp BackEndApi/.envs.example/.local/.db BackEndApi/.envs/.local/.db
   cp BackEndApi/.envs.example/.local/.cloud BackEndApi/.envs/.local/.cloud

   # Edit with your values
   vim BackEndApi/.envs/.local/.django
   ```

3. **Start development servers:**
   ```bash
   make dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/

## Features

### Backend (Django)
- JWT authentication with refresh tokens
- WebSocket support via Django Channels
- Celery for background tasks
- S3 integration for file uploads
- Comprehensive test setup with pytest
- Example CRUD module demonstrating best practices

### Frontend (React)
- React 19 with TypeScript
- Redux Toolkit for state management
- WebSocket integration
- Responsive layout components
- Authentication flow (login, signup, verification)
- Example components demonstrating patterns

### Infrastructure (Terraform)
- AWS ECS Fargate for containerized deployment
- RDS PostgreSQL for database
- ElastiCache Redis for caching/sessions
- S3 + CloudFront for static assets
- Application Load Balancer
- VPC with public/private subnets
- Secrets Manager for credentials

### DevOps
- Docker Compose for local development
- Production-ready Dockerfiles
- Deployment scripts for AWS
- Database sync utilities
- Makefile for common commands

## Documentation

See the `docs/` directory in your generated project for:
- `INFRASTRUCTURE.md` - AWS architecture details
- `DEPLOYMENT_QUICKSTART.md` - Deployment guide
- `CONFIGURATION.md` - Configuration reference
- `DATABASE_PERSISTENCE.md` - Database management
- `WEBSOCKET_USAGE.md` - WebSocket implementation guide

## License

This template is available under the MIT License.
