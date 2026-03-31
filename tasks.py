import datetime
import json
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from dates import (
    EventType,
    all_dates,
    get_tasks_list_name_to_id,
    prompt_date,
    prompt_event_name,
    prompt_event_type,
    prompt_responsible,
    prompt_start_creation,
    title_event,
)

# If modifying these scopes, delete the file token.json.
SCOPES: list[str] = ["https://www.googleapis.com/auth/tasks"]
_SCRIPT_DIR: Path = Path(__file__).resolve().parent
TOKEN_FILE: Path = _SCRIPT_DIR / "token.json"
CREDENTIALS_FILE: Path = _SCRIPT_DIR / "credentials.json"


def due_rfc3339(date: datetime.date) -> str:
    """Start of that calendar day in UTC (Tasks due field is RFC3339)."""
    dt: datetime.datetime = datetime.datetime.combine(date=date, time=datetime.time.min, tzinfo=datetime.timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def get_credentials() -> Credentials:
    creds: Credentials | None = None
    if TOKEN_FILE.exists():
        creds: Credentials = Credentials.from_authorized_user_file(filename=TOKEN_FILE, scopes=SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(request=Request())
        else:
            if not CREDENTIALS_FILE.is_file():
                print(
                    "Missing OAuth client file:\n"
                    f"  {CREDENTIALS_FILE}\n\n"
                    "Create a Desktop app OAuth client in Google Cloud Console (APIs & Services → "
                    "Credentials), download the JSON, and save it as credentials.json next to tasks.py.",
                    file=sys.stderr,
                )
                sys.exit(1)
            flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file=str(CREDENTIALS_FILE),
                scopes=SCOPES,
            )
            # Opens your default browser to Google’s sign-in / consent page; local server catches the redirect.
            try:
                creds: Credentials = flow.run_local_server(
                    port=0,
                    open_browser=True,
                    authorization_prompt_message=(
                        "Opening your browser to sign in with Google.\n"
                        "If nothing opens, open this URL manually:\n{url}\n"
                        "Complete sign-in in the browser; do not press Ctrl+C here while waiting.\n"
                    ),
                )
            except KeyboardInterrupt:
                print(
                    "\nSign-in cancelled (Ctrl+C). Run the script again and finish the browser step "
                    "without interrupting the terminal.",
                    file=sys.stderr,
                )
                raise SystemExit(130) from None
        with TOKEN_FILE.open(mode="w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return creds


def main() -> None:
    """Prompt for a date and task titles; create Google Tasks with that due date."""
    creds: Credentials = get_credentials()
    event_type: EventType = prompt_event_type()
    event_name: str = prompt_event_name()
    event_date: datetime.date = prompt_date()

    dates: list[tuple[str, datetime.date, str]] = all_dates(
        event_type=event_type,
        event_name=event_name,
        event_date=event_date,
    )

    service: Resource = build(serviceName="tasks", version="v1", credentials=creds)
    tasks_list_name_to_id: dict[str, str] = get_tasks_list_name_to_id(service=service)

    if not prompt_start_creation(nb_dates=len(dates)):
        print("Annulation.")
        return
    print("Création des rappels...")

    for title, date, tasks_list_name in dates:
        body: dict[str, str] = {"title": title, "due": due_rfc3339(date=date)}
        print(f"Création du rappel pour le {date}...")
        created: dict[str, str] = (
            service.tasks()
            .insert(
                tasklist=tasks_list_name_to_id[tasks_list_name],
                body=body,
            )
            .execute()
        )
        print(f"Created: {created.get('title')} (due {date})")


if __name__ == "__main__":
    main()
