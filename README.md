# create-olyv-app

Quickly scaffold a new Django project with Olyv's opinionated setup and best practices.

## Usage

Create a new Django project:

```bash
uvx --from https://github.com/christianwhocodes/create-olyv-app.git create-olyv-app my-project
```

This will generate a new Django project with a Pre-configured settings structure.
<!-- - Django REST Framework setup
- CKEditor 5 integration
- Static file handling with django-compressor
- SASS processing
- Phone number field support
- Browser auto-reload for development -->

## Requirements

- Python 3.13+

## What's Included

Your new project comes with:
- Modern Django 5.2+ setup
- Split settings for different environments
- Common Django packages pre-installed
- Ready-to-use templates and static files
- Development tools configured (djlint, ruff)

## Next Steps

After creating your project:

```bash
cd my-project
uv sync
uv run python manage.py migrate
uv run python manage.py setup_groups
uv run python manage.py runserver
```

## License

MIT