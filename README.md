# Kabuda-Backend

## Development

### Prerequisites

- [pdm](https://pdm-project.org/latest/#other-installation-methods)

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

4. Run the development server

```bash
make dev
```

5. Access the Swagger UI at http://localhost:3000/docs

### Formatting

To format the code run `make format`.
