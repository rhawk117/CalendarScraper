from dotenv import load_dotenv
import os

from api.parser import CalendarParser
from api.parser.event_mngr import EventInterface
from pathlib import Path

load_dotenv()


class Config:
    WEBSITE_URL: str = os.getenv('WEBSITE_URL', '')


def fetch_event_int() -> EventInterface:
    parser = CalendarParser(Config.WEBSITE_URL)
    parser.set_context()
    success, events = parser.try_parse()
    if not success:
        raise Exception('Failed to parse events')
    return EventInterface(events)


def load_events() -> EventInterface:
    event_int = EventInterface()
    event_int.import_events(Path('output', 'events_20250108140338.json'))
    return event_int


def main() -> None:
    event_int = fetch_event_int()
    event_int.export_events('events')
    

if __name__ == '__main__':
    main()
