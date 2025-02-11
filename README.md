# Kabuda-Backend

## Development

### Prerequisites

- [pdm](https://pdm-project.org/latest/#other-installation-methods)
- [taplo](https://taplo.tamasfe.dev/cli/installation/homebrew.html) (for formatting TOML files)

### Setup

1. Clone the repository

```bash
git clone https://github.com/Onexyq/Kabuda-Backend.git
```

2. Install dependencies

```bash
cd Kabuda-Backend
pdm install
```

3. Create an `.env` file

```
cp .env.example .env
```

4. Add client_id and client_secret to the `.env` file

```
echo "google_auth_client_id=YOUR_CLIENT_ID" >> .env
echo "google_auth_client_secret=YOUR_CLIENT_SECRET" >> .env
```

5. Launch the database container

```bash
docker-compose up -d
```

6. Run migrations for the database

```bash
alembic upgrade head
```

7. Run the development server

```bash
make dev
```

5. Access the Swagger UI at http://localhost:3000/docs

### Formatting

To format the code run `make format`.

### Database Schema Evolution

The database schema is managed using [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script). PDM will automatically install Alembic as a dependency so no additional setup is required.

```bash
alembic revision -m "MIGRATION_MESSAGE"
```

This will create a new migration script in the `alembic/versions` directory. You are responsible for implementing reversible changes in the `upgrade` and `downgrade` functions.

To apply the migration, run:

```bash
alembic upgrade head
```

To rollback the last migration, run:

```bash
alembic downgrade -1
```

To rollback all migrations, run:

```bash
alembic downgrade base
```
