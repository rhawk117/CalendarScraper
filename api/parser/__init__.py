
import requests
from bs4 import BeautifulSoup, Tag
from api.parser.event_data import Event
from typing import Optional


class CalendarParser:
    def __init__(self, url: str) -> None:
        self.url: str = url
        self.event_table: Optional[Tag] = None
        self.duds: int = 0

    def set_context(self) -> bool:
        '''sets the calendar table to be parsed'''
        res = requests.get(self.url)

        if res.status_code != 200:
            print(
                'Failed to fetch the calendar, website returned status code:', res.status_code)
            return False

        if not res.text:
            print('Failed to fetch the calendar, website returned no content')
            return False

        bs = BeautifulSoup(res.text, "html.parser")
        self.event_table = bs.select_one(
            '#introduction > div > div:nth-child(1) > div > div > table > tbody'
        )

        return True

    def try_parse(self, verbose=False, on_dud=None) -> tuple[bool, Optional[list[Event]]]:
        if not self.event_table and not self.set_context():
            return False, None

        event_rows = self.event_table.find_all('tr')[2:]
        events: list[Event] = []
        for tags in event_rows:
            event_data = tags.find_all('td')

            if len(event_data) < 2:
                continue

            event = Event(event_data[1].text, event_data[0].text)

            if not event.format_date():
                self.duds += 1
                if on_dud:
                    on_dud(event)

            events.append(event)

            if verbose:
                print(event)

        print(events)
        self._display_parser_infos()
        return True, events

    def _display_parser_infos(self) -> None:
        print(f'[*] Parser Complete - parser_infos')
        print(f'[*] Unprocessable Dates: {self.duds}')
