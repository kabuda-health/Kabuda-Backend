# Kabuda-Backend

## Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/#homebrew)

### Setup

1. Clone the repository

```bash
git clone https://github.com/kabuda-health/Kabuda-Backend.git
```

2. Install dependencies

```bash
cd Kabuda-Backend
uv sync
```

_This will install all the dependencies and create a virtual environment for the project. `uv` commands will automatically execute in the context of the virtual environment, so most of the times, its unnecessary to actually activate the virtual environment. However, if you need to activate the virtual environment manually, you can do so by running:_

```bash
source .venv/bin/activate
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
make migrate
```

7. Run the development server

```bash
make dev
```

5. Access the Swagger UI at http://localhost:3000/docs

### Formatting

To format the code run `make format`.

### Database Schema Evolution

The database schema is managed using [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script). `uv` will automatically install Alembic as a dependency so no additional setup is required.

_The following commands should be run in the context of the virtual environment._

To create a new migration, run:

```bash
uv run -- alembic revision -m "MIGRATION_MESSAGE"
```

This will create a new migration script in the `alembic/versions` directory. You are responsible for implementing reversible changes in the `upgrade` and `downgrade` functions.

To apply the migration, run:

```bash
uv run -- alembic upgrade head
```

To rollback the last migration, run:

```bash
uv run -- alembic downgrade -1
```

To rollback all migrations, run:

```bash
uv run -- alembic downgrade base
```