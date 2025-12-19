# Database Setup Guide

## Overview

Behflow uses PostgreSQL as its database. The database schema includes tables for users, tasks, chat sessions, messages, and automated processes.

## Automatic Initialization (Docker)

When running Behflow with Docker Compose, the database is **automatically initialized** on first startup:

1. PostgreSQL container starts
2. Migration scripts in `infra/migrations/` are executed automatically
3. All tables, indexes, and default data are created

### Quick Start

```bash
# From the project root
cd infra
docker compose up -d
```

The database will be ready with all tables created!

## Database Connection

### From Host Machine
- **Host:** localhost
- **Port:** 15432
- **Database:** behflow_dev
- **Username:** behflow
- **Password:** admin

```bash
psql -h localhost -p 15432 -U behflow -d behflow_dev
```

### From Docker Network
- **Host:** infra-db (container name)
- **Port:** 5432
- **Database:** behflow_dev
- **Username:** behflow
- **Password:** admin

## Database Schema

### Tables Created

1. **users** - User accounts and authentication
2. **tasks** - User tasks with priorities and statuses
3. **chat_sessions** - Chat conversation sessions
4. **chat_messages** - Individual chat messages
5. **automated_processes** - Scheduled/automated processes configuration
6. **automated_process_executions** - Execution history and results

### Custom Types (ENUMs)

- `priority_enum`: low, medium, high
- `status_enum`: pending, in_progress, completed, cancelled
- `trigger_type_enum`: manual, time_based, event_based
- `process_status_enum`: pending, running, completed, failed, disabled

## Migration Files

Migration files are located in `infra/migrations/` and executed in alphabetical order:

1. **000_init_database.sql** - Creates all tables, types, and indexes
2. **001_add_automated_processes.sql** - Additional automated process configurations (legacy, now included in 000)

## Manual Database Operations

### Reset Database (Docker)

To completely reset the database and start fresh:

```bash
# Stop all services
docker compose down

# Remove the database volume
docker volume rm infra_db_data

# Start services (database will be recreated)
docker compose up -d
```

### Verify Database Setup

Connect to the database and verify tables:

```bash
# Connect to database
docker exec -it infra-db psql -U behflow -d behflow_dev

# List all tables
\dt

# List all types
\dT

# Check automated processes
SELECT process_id, name, trigger_type, is_enabled FROM automated_processes;

# Exit
\q
```

### Run Migrations Manually

If you need to run migrations manually:

```bash
# Copy migration file into container
docker cp infra/migrations/000_init_database.sql infra-db:/tmp/

# Execute migration
docker exec -it infra-db psql -U behflow -d behflow_dev -f /tmp/000_init_database.sql
```

## Local Development (Without Docker)

### Prerequisites

- PostgreSQL 15+ installed locally
- Database created: `behflow_dev`

### Setup Steps

1. **Create database:**
```bash
createdb -U postgres behflow_dev
```

2. **Run migrations:**
```bash
psql -U postgres -d behflow_dev -f infra/migrations/000_init_database.sql
```

3. **Update environment variable:**
```bash
export DATABASE_URL="postgresql://postgres:your_password@localhost:5432/behflow_dev"
```

4. **Run backend:**
```bash
cd src/backend
uvicorn app.main:app --reload
```

## Troubleshooting

### "relation does not exist" Error

This means tables haven't been created. Solutions:

1. **For Docker:** Reset the database volume (see above)
2. **For Local:** Run the migration files manually

### Database Connection Failed

Check:
- PostgreSQL is running: `docker ps` (for Docker) or `pg_isready` (for local)
- Correct credentials in `DATABASE_URL`
- Firewall/port settings

### Migration Failed

Check the PostgreSQL logs:
```bash
docker logs infra-db
```

## Default Data

The following default data is automatically created:

### Automated Processes

- **reschedule_remaining_tasks**: Reschedules incomplete tasks daily at 7:30 AM (Asia/Tehran timezone)

## Database Backup and Restore

### Backup

```bash
# Using Docker
docker exec infra-db pg_dump -U behflow behflow_dev > backup.sql

# Local
pg_dump -U postgres behflow_dev > backup.sql
```

### Restore

```bash
# Using Docker
docker exec -i infra-db psql -U behflow behflow_dev < backup.sql

# Local
psql -U postgres behflow_dev < backup.sql
```

## Schema Updates

When adding new tables or columns:

1. Create a new migration file: `infra/migrations/00X_description.sql`
2. Number it sequentially (002, 003, etc.)
3. For Docker: Restart the database container
4. For Local: Run the migration manually

## Security Notes

⚠️ **Production Deployment:**

- Change default passwords in `docker-compose.yml`
- Use environment variables for sensitive data
- Restrict database port exposure
- Enable SSL/TLS connections
- Regular backups

