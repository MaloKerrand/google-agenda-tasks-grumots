import datetime
from enum import Enum

from googleapiclient.discovery import Resource


class EventType(Enum):
    SHOW = "spectacle"
    STAGE = "stage"


def prompt_event_type() -> EventType:
    while True:
        raw: str = input("Type d'événement (spectacle/stage) [spectacle]: ").strip().lower()
        if not raw:
            return EventType.SHOW
        try:
            return EventType(raw)
        except ValueError:
            print("Invalid event type. Use spectacle/stage.")


def prompt_event_name() -> str:
    while True:
        raw: str = input("Nom de l'événement: ").strip()
        if raw:
            return raw
        print("Invalid event name. Use a valid name.")


def prompt_date() -> datetime.date:
    while True:
        raw: str = input("Date (YYYY-MM-DD): ").strip()
        try:
            return datetime.datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD (e.g. 2026-03-28).")


def prompt_responsible(what: str, default: str | None = None) -> str:
    while True:
        message: str = f"Qui est responsable {what} ? "
        if default is not None:
            message = f"{message}[{default}] "
        raw: str = input(message).strip().capitalize()
        if raw:
            return raw
        if default is not None:
            return default


def prompt_start_creation(nb_dates: int) -> bool:
    print(f"Demarrer la création de {nb_dates} rappel(s) ?")
    while True:
        raw: str = input("o/n: [O]").strip().lower()
        if not raw or raw == "o":
            return True
        if raw == "n":
            return False
        print("Invalid input. Use o/n.")


def all_dates(
    event_type: EventType,
    event_name: str,
    event_date: datetime.date,
) -> list[tuple[str, datetime.date, str]]:
    match event_type:
        case EventType.SHOW:
            return all_dates_show(event_type=event_type, event_name=event_name, event_date=event_date)
        case EventType.STAGE:
            return all_dates_stage(event_type=event_type, event_name=event_name, event_date=event_date)
        case _:
            raise ValueError(f"Invalid event type: {event_type}")


def all_dates_show(
    event_type: EventType,
    event_name: str,
    event_date: datetime.date,
) -> list[tuple[str, datetime.date, str]]:
    stories_show_title: str = title_event(
        main_message="Faire une story",
        event_type=event_type,
        event_name=event_name,
        event_date=event_date,
        responsible=prompt_responsible(what="des stories du spectacle"),
    )
    stories_ps_title: str = title_event(
        main_message="Faire une story places suspendues",
        event_type=event_type,
        event_name=event_name,
        event_date=event_date,
        responsible=prompt_responsible(what="des stories pour les places suspendues", default="Maxime"),
    )
    online_agenda_title: str = title_event(
        main_message="Mettre à jour les agendas en ligne",
        event_type=event_type,
        event_name=event_name,
        event_date=event_date,
        responsible=prompt_responsible(what="des agendas en ligne", default="Leandra"),
    )
    whatsapp_title: str = title_event(
        main_message="Envoyer un message dans whatsapp",
        event_type=event_type,
        event_name=event_name,
        event_date=event_date,
        responsible=prompt_responsible(what="du message whatsapp", default="Leandra"),
    )
    photo_sort_title: str = title_event(
        main_message="Faire tri photo",
        event_type=event_type,
        event_name=event_name,
        event_date=event_date,
        responsible=prompt_responsible(what="du tri des photo"),
    )
    story_photo_title: str = title_event(
        main_message="Faire un post insta",
        event_type=event_type,
        event_name=event_name,
        event_date=event_date,
        responsible=prompt_responsible(what="du post insta post-spectacle"),
    )
    return [
        (online_agenda_title, event_date - datetime.timedelta(days=14), "Comm Autre"),
        (stories_show_title, event_date - datetime.timedelta(days=14), "Stories spectacles"),
        (stories_show_title, event_date - datetime.timedelta(days=10), "Stories spectacles"),
        (stories_show_title, event_date - datetime.timedelta(days=7), "Stories spectacles"),
        (stories_ps_title, event_date - datetime.timedelta(days=7), "Story/Post autre"),
        (whatsapp_title, event_date - datetime.timedelta(days=7), "Comm Autre"),
        (stories_show_title, event_date - datetime.timedelta(days=5), "Stories spectacles"),
        (stories_show_title, event_date - datetime.timedelta(days=3), "Stories spectacles"),
        (stories_show_title, event_date - datetime.timedelta(days=1), "Stories spectacles"),
        (stories_ps_title, event_date + datetime.timedelta(days=1), "Story/Post autre"),
        (photo_sort_title, event_date + datetime.timedelta(days=2), "Story/Post autre"),
        (story_photo_title, event_date + datetime.timedelta(days=3), "Insta post-spectacle"),
    ]


def all_dates_stage(
    event_type: EventType,
    event_name: str,
    event_date: datetime.date,
) -> list[tuple[str, datetime.date, str]]:
    stage_title: str = title_event(
        main_message="Faire une story",
        event_type=event_type,
        event_name=event_name,
        event_date=event_date,
        responsible=prompt_responsible(what="du stage"),
    )
    return [
        (stage_title, event_date - datetime.timedelta(days=14), "Stage"),
        (stage_title, event_date - datetime.timedelta(days=10), "Stage"),
        (stage_title, event_date - datetime.timedelta(days=7), "Stage"),
        (stage_title, event_date - datetime.timedelta(days=5), "Stage"),
        (stage_title, event_date - datetime.timedelta(days=3), "Stage"),
        (stage_title, event_date - datetime.timedelta(days=1), "Stage"),
        (stage_title, event_date + datetime.timedelta(days=2), "Stage"),
    ]


def title_event(
    main_message: str,
    event_type: EventType,
    event_name: str,
    event_date: datetime.date,
    responsible: str,
) -> str:
    return f"[{responsible}][{event_name}] {main_message} pour le {event_type.value} du {event_date.strftime('%d/%m')}"


def get_tasks_list_name_to_id(service: Resource) -> dict[str, str]:
    tasklists: list[dict[str, str]] = service.tasklists().list().execute().get("items", [])
    return {tasklist["title"]: tasklist["id"] for tasklist in tasklists}
