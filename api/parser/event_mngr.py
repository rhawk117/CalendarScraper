from datetime import datetime
from typing import Generator, List, Optional, Dict, Callable
import json
import hashlib
from pathlib import Path
import os
from .event_data import Event


    
    
class EventInterface:
    def __init__(self, events: Optional[List[Event]] = None) -> None:
        self._events: List[Event] = []
        if events:
            self.set_events(events)
        self._hash = None

    def __iter__(self) -> Generator:
        for event in self._events:
            yield event

    def __len__(self) -> int:
        return len(self._events)

    def filter_events_by(self, predicate: Callable[[Event], bool]) -> List[Event]:
        return [event for event in self if predicate(event)]

    def set_events(self, events: List[Event]) -> None:
        self._events = events

    def events_to_dict(self) -> List[dict]:
        return [event.serialize() for event in self]

    def get_events_hash(self, event_dump: List[dict]) -> str:
        if not self._events:
            raise Exception('No events to hash')
        serialized = json.dumps(
            sorted(event_dump, key=lambda d: json.dumps(d, sort_keys=True)),
            sort_keys=True
        )
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    def set_event_hash(self) -> None:
        if not self._events:
            raise Exception('No events to hash')
        self._hash = self.get_events_hash(self.events_to_dict())

    def export_events(self, output_dir: str) -> None:
        if not self._events:
            raise Exception('No events to export')

        time_stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f'events_{time_stamp}.json'

        file_path = Path(output_dir) / file_name
        os.makedirs(output_dir, exist_ok=True)
        self._export_contents(file_path)

    def _export_contents(self, file_path: Path) -> None:
        serialized = self.events_to_dict()
        with file_path.open(mode='w', encoding='utf-8') as f:
            json.dump(serialized, f, indent=4)

    def import_events(self, file_path: Path) -> None:
        event_dump = self._get_event_dump(file_path)
        for event in event_dump:
            event_obj = self._json_to_obj(event)
            self._events.append(event_obj)

    def _json_to_obj(self, event_dict: Dict) -> Event:
        date_value = None
        formatted_date = event_dict.get('formatted_date')

        if formatted_date and formatted_date != Event.INVALID_DATE:
            try:
                date_value = datetime.fromisoformat(formatted_date)
            except ValueError:
                raise ValueError(f"Invalid date format: {formatted_date}")

        event_dict['formatted_date'] = date_value
        return Event(**event_dict)

    def _get_event_dump(self, path_obj: Path) -> List[dict]:
        if not path_obj.exists() or not path_obj.is_file():
            raise Exception('cannot import events from non-existent file')
        with path_obj.open(mode='r', encoding='utf-8') as f:
            event_dump = json.load(f)
            
        if not event_dump:
            raise Exception('event data is empty')
        
        return event_dump

    def __str__(self) -> str:
        return '\n'.join([str(event) for event in self])
