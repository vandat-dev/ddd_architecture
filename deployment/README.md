# Deployment

This directory contains deployment configurations for different environments.

## Structure

```
deployment/
├── dev/              # Development environment
│   ├── Dockerfile
│   └── docker-compose.yml
└── prod/             # Production environment (future)
    ├── Dockerfile
    └── docker-compose.yml
```

## Development Environment

Located in `deployment/dev/`

### Available Commands

```bash
# Build Docker image for dev
make docker-build

# Run Docker container
make docker-run

# Build and run
make docker

# Docker Compose commands
make docker-compose-up
make docker-compose-down
```

## Production Environment

Will be added later in `deployment/prod/`

