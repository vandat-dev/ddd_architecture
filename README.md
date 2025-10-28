# DDD Architecture Project

A Domain-Driven Design (DDD) implementation built with FastAPI, demonstrating clean architecture principles and modern Python development practices.

## 🏗️ Architecture Overview

This project follows **Domain-Driven Design (DDD)** principles with a layered architecture that promotes separation of concerns, maintainability, and scalability.

### Architecture Layers

```
📁 app/
├── 🎯 modules/           # Domain Modules
│   └── auth/             # Authentication Domain
│       ├── controller.py # Presentation Layer (HTTP handlers)
│       ├── service.py    # Application Layer (business logic)
│       ├── repository.py # Infrastructure Layer (data access)
│       ├── model.py      # Domain Models
│       ├── schemas.py    # Data Transfer Objects
│       └── security.py   # Security utilities
├── 🧱 infra/            # Infrastructure Layer
│   ├── database.py      # Database configuration
│   ├── models.py        # SQLAlchemy models
│   └── websocket.py     # WebSocket configuration
├── ⚙️ core/             # Application Core
│   ├── setting.py       # Configuration settings
│   └── app_status.py    # Status codes
├── 🔧 utils/            # Shared utilities
└── 📝 constant/         # Application constants
```

## 🎯 DDD Principles Implemented

### 1. **Domain-Centric Design**
- **Modules** represent bounded contexts (e.g., `auth` module)
- **Domain models** encapsulate business logic and rules
- **Clear boundaries** between different domains

### 2. **Layered Architecture**
- **Presentation Layer**: Controllers handle HTTP requests/responses
- **Application Layer**: Services orchestrate business workflows  
- **Domain Layer**: Models contain business logic and invariants
- **Infrastructure Layer**: Repositories handle data persistence

### 3. **Dependency Inversion**
- **High-level modules** don't depend on low-level modules
- **Abstractions** define contracts between layers
- **Dependency injection** via FastAPI's dependency system

### 4. **Clean Code Practices**
- **Single Responsibility** - each class has one reason to change
- **Interface Segregation** - focused, cohesive interfaces
- **Open/Closed Principle** - extensible without modification

## 🚀 Features

### Authentication & Authorization
- 🔐 **JWT-based authentication** with access/refresh tokens
- 👤 **User management** (CRUD operations)
- 🛡️ **Role-based access control** (ADMIN, USER, CHECKER, ENTRY)
- 🍪 **Secure cookie handling** with CORS support
- ⚡ **Token refresh** mechanism

### Technical Features
- 📊 **PostgreSQL** with async SQLAlchemy
- 🔄 **Database migrations** support
- 🐳 **Docker containerization**
- 📝 **Comprehensive logging**
- 🧪 **Unit testing** setup
- 🔒 **Security middleware**

## 🛠️ Technology Stack

- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL with AsyncPG
- **ORM**: SQLAlchemy (Async)
- **Authentication**: JWT with PyJWT
- **Containerization**: Docker & Docker Compose
- **Object Storage**: MinIO
- **Testing**: Pytest

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Poetry (recommended)

### 1. Clone Repository
```bash
git clone <repository-url>
cd ddd_architecture
```

### 2. Environment Configuration
Create a `.env` file in the project root:
```env
# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ddd_app
POSTGRES_PORT=5432

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_IN_MINUTES=60
REFRESH_TOKEN_EXPIRES_IN_DAYS=7

# API Configuration
API_PREFIX=/api
VERSION=0.1
DEBUG=true
ALLOW_ORIGINS=*

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_PUBLIC_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=ddd-app-bucket
MINIO_SECURE=false
MINIO_PUBLIC_SECURE=false
```

### 3. Start Infrastructure Services
```bash
cd deployment/dev
docker-compose up -d
```

### 4. Install Dependencies
```bash
# Using Poetry (recommended)
poetry install
poetry shell

# Or using pip
pip install -r requirements.txt
```

### 5. Run Application
```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### Authentication
```http
POST   /api/auth/register    # Register new user (Admin only)
POST   /api/auth/login       # User login
GET    /api/auth/me          # Get current user info
POST   /api/auth/logout      # User logout
```

### User Management  
```http
GET    /api/users            # Get all users (Admin only)
PUT    /api/users/{user_id}  # Update user (Admin only)  
DELETE /api/users/{user_id}  # Delete user (Admin only)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/user/test_auth_repository.py
```

## 📁 Project Structure Details

### Domain Module Structure (`modules/auth/`)
```
auth/
├── controller.py     # HTTP request handlers
├── service.py        # Business logic orchestration
├── repository.py     # Data access layer
├── model.py          # Domain entities
├── schemas.py        # Request/Response DTOs
├── security.py       # JWT & security utilities
├── middleware.py     # Authentication middleware
└── dependencies.py   # Dependency injection setup
```

### Core Infrastructure (`infra/`)
```
infra/
├── database.py       # Database configuration & session management
├── models.py         # SQLAlchemy ORM models
└── websocket.py      # WebSocket connection handling
```

## 🔐 Security Features

- **JWT Authentication** with secure token generation
- **Password hashing** using bcrypt
- **Role-based authorization** middleware
- **CORS protection** with origin validation
- **Secure cookie** handling (HttpOnly, Secure, SameSite)
- **SQL injection protection** via parameterized queries

## 🌐 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    fullname VARCHAR(100),
    phone_number VARCHAR(20),
    gender VARCHAR(10),
    address VARCHAR(128),
    role VARCHAR(128) NOT NULL DEFAULT 'USER',
    is_active BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

## 🚀 Deployment

### Development
```bash
cd deployment/dev
docker-compose up -d
```

### Production
```bash
cd deployment/production  
docker-compose up -d
```

## 📈 Performance Considerations

- **Async/await** throughout for non-blocking I/O
- **Connection pooling** for database efficiency
- **Query optimization** with proper indexing
- **Caching strategy** ready for implementation
- **Horizontal scaling** support via stateless design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏗️ DDD Benefits Realized

- **Maintainability**: Clear separation of concerns
- **Testability**: Isolated layers with dependency injection  
- **Scalability**: Modular architecture supports team growth
- **Flexibility**: Easy to add new domains/features
- **Business Alignment**: Code structure mirrors business domains

---

Built with ❤️ using Domain-Driven Design principles and modern Python practices.
