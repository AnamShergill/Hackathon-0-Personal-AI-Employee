# Odoo Docker Setup for AI Employee

## Overview

This directory contains the Docker Compose configuration for running Odoo Community Edition v19.0 locally for the AI Employee system.

## Components

- **Odoo**: Community Edition v19.0 (web interface on port 8069)
- **PostgreSQL**: Version 16 (database backend)

## Quick Start

### 1. Start Odoo

```bash
cd Gold-Tier/odoo-docker
docker compose up -d
```

### 2. Wait for Initialization

Wait 1-2 minutes for Odoo to fully start. Check logs:

```bash
docker compose logs -f odoo
```

Look for: "odoo.service.server: HTTP service (werkzeug) running on"

### 3. Access Odoo

Open browser: http://localhost:8069

### 4. Initial Setup

On first access, you'll see the database creation screen:

1. **Master Password**: Use the one from `.env` file (`master_password_2026`)
2. **Database Name**: `ai_employee_db`
3. **Email**: Your email (e.g., `pinkyshergill1986@gmail.com`)
4. **Password**: `admin_password_2026` (from `.env`)
5. **Language**: English
6. **Country**: Pakistan (or your country)
7. **Demo Data**: Uncheck (we don't need demo data)

Click "Create Database"

### 5. Install Accounting Module

After database creation:

1. Go to **Apps** menu
2. Search for "Accounting" or "Invoicing"
3. Click **Install** on "Accounting" app
4. Wait for installation to complete

## Management Commands

### Start Odoo
```bash
docker compose up -d
```

### Stop Odoo
```bash
docker compose down
```

### View Logs
```bash
docker compose logs -f odoo
```

### Restart Odoo
```bash
docker compose restart odoo
```

### Stop and Remove Everything (including data)
```bash
docker compose down -v
```

⚠️ **Warning**: The `-v` flag will delete all data!

## Configuration

### Environment Variables

Edit `.env` file to change:
- `ODOO_DB_PASSWORD` - PostgreSQL password
- `ODOO_URL` - Odoo URL (default: http://localhost:8069)
- `ODOO_DB_NAME` - Database name
- `ODOO_USERNAME` - Admin username
- `ODOO_PASSWORD` - Admin password
- `ODOO_MASTER_PASSWORD` - Master password for database management

### Custom Addons

Place custom Odoo modules in `./addons/` directory. They will be available in Odoo's Apps menu.

## Volumes

Data is persisted in Docker volumes:
- `ai_employee_odoo_data` - Odoo filestore (attachments, etc.)
- `ai_employee_postgres_data` - PostgreSQL database

## Networking

All services are on the `ai_employee_network` bridge network.

## Ports

- **8069** - Odoo web interface
- **5432** - PostgreSQL (not exposed by default)

## Troubleshooting

### Odoo won't start

Check logs:
```bash
docker compose logs odoo
```

### Port already in use

Check if another service is using port 8069:
```bash
netstat -ano | findstr :8069
```

### Reset everything

```bash
docker compose down -v
docker compose up -d
```

### Database connection issues

Ensure PostgreSQL is running:
```bash
docker compose ps
```

Both `ai_employee_odoo` and `ai_employee_postgres` should show "Up"

## Integration with AI Employee

The AI Employee system connects to Odoo via JSON-RPC API:
- Script: `../actions/odoo_rpc.py`
- Skill: `../Skills/11_ODOO_ACCOUNTING.md`
- Configuration: Uses `.env` file for credentials

## Security Notes

⚠️ **Important**:
- Change default passwords in `.env` before production use
- Don't commit `.env` file to git (already in .gitignore)
- Use strong passwords for master password and admin account
- Consider using Odoo's API keys instead of passwords for JSON-RPC

## Resources

- [Odoo Documentation](https://www.odoo.com/documentation/19.0/)
- [Odoo Docker Hub](https://hub.docker.com/_/odoo)
- [Odoo JSON-RPC API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
