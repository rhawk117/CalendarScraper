from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import json
from datetime import datetime
import re
from typing import Optional

load_dotenv()


class Config:
    WEBSITE_URL = os.getenv("WEBSITE_URL")


class Event:
    def __init__(self, event_name: str, event_date: str, formatted_date: Optional[datetime] = None) -> None:
        self.event_name = event_name
        self.event_date = event_date
        self.formatted_date = formatted_date

    def serialize_single(self) -> dict:
        return {
            "event_name": self.event_name,
            "event_date": self.event_date,
            "formatted_date": self.formatted_date.isoformat() if self.formatted_date else 'N/A'
        }

    def format_date(self, set_attr=True,  current_year: int = 2025) -> Optional[datetime]:
        date_part = self.event_date.split('-')[0].strip()
        date_part = re.sub(r'^[A-Za-z]{3,4}\.\s*', '', date_part)
        date_part = date_part.replace('.', '')
        for fmt in ["%b %d %Y", "%B %d %Y"]:
            try:
                resolve_dt = datetime.strptime(
                    f"{date_part} {current_year}", fmt)
                if set_attr:
                    self.formatted_date = resolve_dt
                return resolve_dt
            except ValueError:
                pass
        return None

    def __str__(self) -> str:
        return f"Name={self.event_name}\nRaw:{self.event_date}\nFormatted:{self.formatted_date}"


class CalendarParser:
    def __init__(self, url: str = None) -> None:
        self.url = url
        self.event_table = None

    def get_context(self, url: str = None) -> bool:
        self.url = self.url if self.url else self.url
        if not self.url:
            raise Exception('no url provided')
        res = requests.get(Config.WEBSITE_URL)
        if res.status_code != 200:
            print('the website did not like this request, cannot parse')
            return False
        bs = BeautifulSoup(res.text, "html.parser")
        self.event_table = bs.select_one(
            '#introduction > div > div:nth-child(1) > div > div > table > tbody'
        )
        return True

    def try_parse(self, verbose=False, resolve_dates=True) -> list[dict]:
        if not self.event_table and not self.get_context():
            raise Exception(
                'cannot parse without context, likely due to a failed request to the calendar'
            )
        serialized_events = []
        for tags in self.event_table.find_all('tr')[2:]:
            event_data = tags.find_all('td')
            if len(event_data) < 2:
                continue
            event = Event(event_data[1].text, event_data[0].text)
            if resolve_dates:
                event.format_date(set_attr=True)
            serialized_events.append(
                event.serialize_single()
            )
            if verbose:
                print(event)
        return serialized_events

    def export_data(self, events: list[dict]) -> None:
        os.makedirs('data', exist_ok=True)
        time_stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_json = Path('data', f"events_{time_stamp}.json")
        with output_json.open(mode='w') as f:
            json.dump(events, f, indent=4)

    def import_data(self, file_path: Path) -> list[Event]:
        event_dump = None
        if not file_path.exists():
            raise Exception('file does not exist, silly')
        with file_path.open(mode='r') as f:
            event_dump = json.load(f)
        if not event_dump:
            raise Exception('could not load data from file')
        event_objs = []
        for event in event_dump:
            if event.get('formatted_date'):
                event['formatted_date'] = datetime.fromisoformat(
                    event['formatted_date']
                )
            event_objs.append(Event(**event))
        return event_objs

    def count_dud_dates(self, events: list[Event]) -> int:
        dud_dates = 0
        for event in events:
            if not event.formatted_date:
                dud_dates += 1
        return dud_dates


def get_events(verbose=False) -> None:
    parser = CalendarParser(Config.WEBSITE_URL)
    events = parser.try_parse(verbose=verbose, resolve_dates=True)
    parser.export_data(events)
    print(f"Exported {len(events)} events")


def main() -> None:
    get_events(verbose=True)


if __name__ == '__main__':
    main()
