# grumots

CLI tool to create Google Tasks reminders for communication around events.

## Requirements

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- A Google account with access to Google Tasks

## Setup

### 1. Install dependencies

```bash
poetry install
```

### 2. Add Google OAuth credentials

You have two options to get `credentials.json`:

1. Generate your own in Google Cloud Console:
   - Open **APIs & Services > Credentials**
   - Create an **OAuth client ID** of type **Desktop app**
   - Download the JSON file
2. Ask an admin to provide an existing `credentials.json`

In both cases, place `credentials.json` at the project root (next to `tasks.py`).

The first run will open your browser to authorize access and create `token.json` automatically.

## Usage

Run the script with Poetry:

```bash
poetry run python tasks.py
```

You will be prompted for:

- Event type: `spectacle` or `stage` (default: `spectacle`)
- Event name
- Event date (`YYYY-MM-DD`)
- Confirmation before creating reminders

Depending on the event type, the script will ask for one or more responsible people and then create multiple reminders with different due dates and target Google Tasks lists.
