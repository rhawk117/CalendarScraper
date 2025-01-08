from datetime import datetime
import re
from typing import Optional
from datetime import date


class Event:
    INVALID_DATE = 'N/A'

    def __init__(self, event_name: str, event_date: str, formatted_date: Optional[datetime] = None) -> None:
        self.event_name: str = event_name
        self.event_date: str = event_date
        self.formatted_date = formatted_date

    def serialize(self) -> dict:
        return {
            "event_name": self.event_name,
            "event_date": self.event_date,
            "formatted_date": self.formatted_date.isoformat() if self.formatted_date else Event.INVALID_DATE
        }

    def is_tomorrow(self) -> bool:
        if not self.formatted_date:
            return False
        tomorrow = date.today().replace(day=date.today().day + 1)
        return self.formatted_date.date() == tomorrow

    def is_this_week(self) -> bool:
        if not self.formatted_date:
            return False
        today = date.today()
        return today <= self.formatted_date.date() <= today.replace(day=today.day + 7)

    def is_today(self) -> bool:
        if not self.formatted_date:
            return False
        return self.formatted_date.date() == date.today()

    def set_hour(self, hour: int) -> None:
        if not self.formatted_date:
            return
        self.formatted_date = self.formatted_date.replace(hour=hour)

    def is_unformatted(self) -> bool:
        return not self.formatted_date or self.formatted_date == 'N/A'

    def format_date(self, current_year: int = 2025) -> bool:

        date_part = self.event_date.split('-')[0].strip()
        date_part = re.sub(r'^[A-Za-z]{3,4}\.\s*', '', date_part)
        date_part = date_part.replace('.', '')

        formats = ["%b %d %Y", "%B %d %Y"]

        for fmt in formats:
            try:
                resolve_dt = datetime.strptime(
                    f"{date_part} {current_year}",
                    fmt
                )
                self.formatted_date = resolve_dt
                return True
            except ValueError:
                pass
        return False

    def __str__(self) -> str:
        return f"Name={self.event_name}\nRaw:{self.event_date}\nFormatted:{self.formatted_date}"
