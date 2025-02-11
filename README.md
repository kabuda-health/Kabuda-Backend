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

4. Run the development server

```bash
make dev
```

5. Access the Swagger UI at http://localhost:3000/docs

### Formatting

To format the code run `make format`.
