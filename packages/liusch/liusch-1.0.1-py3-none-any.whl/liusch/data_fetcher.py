import requests
import re
import calendar
import time
from re import Match
from typing import List
from requests import Response
from .schedule import Schedule
from datetime import date, datetime, timezone
from dataclasses import dataclass, field


@dataclass
class ScheduleData:
    start_date: str = ""
    start_time: str = ""
    start_unix: float = 0
    end_date: str = ""
    end_time: str = ""
    end_unix: float = 0
    course_codes: List[str] = field(default_factory=lambda: [])
    course_type: str = ""
    locations: List[str] = field(default_factory=lambda: [])


class DataFetcher:
    ENTRY_SEPARATOR: str = "BEGIN:VEVENT"
    COURSE_CODE_SEPARATOR: str = r"\, "
    DATA_ENCODING: str = "utf-8"

    DATETIME_FORMAT: str = "%Y%m%dT%H%M%SZ"
    WEEK_IN_SECONDS: int = 604800
    
    START_TIME_RE: str = "(?<=DTSTART:).*"
    END_TIME_RE: str = "(?<=DTEND:).*"
    COURSE_CODE_RE: str = r"(?<=SUMMARY:).*(?=U)" 
    TYPE_RE: str = r"(?<=Undervisningstyp: ).*?(?=\\)" 
    LOCATION_RE: str = r"(?<=Lokal: ).*?(?=\\n|\n|\r)"


    def get_data(self, schedules: List[Schedule]) -> List[ScheduleData]:
        """Get the sorted schedule data"""
        data: List[ScheduleData] = []

        for schedule in schedules:
            content: str = self._fetch_from_web(schedule.link)

            if content:
                data += self._parse_data(content)

        # Sort the entries
        data.sort(key=lambda o: o.start_unix)

        return data

    def _parse_data(self, content: str) -> List[ScheduleData]:
        """Parse the raw data into ScheduleData"""
        data: List[ScheduleData] = []

        for entry in content.split(self.ENTRY_SEPARATOR):
            schedule: ScheduleData = ScheduleData()

            start_datetime_text: str = self._match_regex(entry, self.START_TIME_RE).strip()
            end_datetime_text: str = self._match_regex(entry, self.END_TIME_RE).strip()

            # Skip if the times couldn't be parsed
            if not start_datetime_text or not end_datetime_text:
                continue

            # Convert the dates to local datetimes
            start_datetime: datetime = self._get_datetime_from_text(start_datetime_text)
            end_datetime: datetime = self._get_datetime_from_text(end_datetime_text)

            # Get the local dates
            schedule.start_date = self._get_date_from_datetime(start_datetime)
            schedule.end_date = self._get_date_from_datetime(end_datetime)

            # Get the local time
            schedule.start_time = self._get_time_from_datetime(start_datetime)
            schedule.end_time = self._get_time_from_datetime(end_datetime)

            # Save unix time to be able to sort the schedule
            schedule.start_unix = start_datetime.timestamp()
            schedule.end_unix = end_datetime.timestamp()
            
            # Get the course code, type and location
            course_codes_text = self._match_regex(entry, self.COURSE_CODE_RE)
            schedule.course_codes = self._get_courses_from_text(course_codes_text)
            schedule.course_type = self._match_regex(entry, self.TYPE_RE)
            schedule.locations = self._match_all_regex(entry, self.LOCATION_RE)

            data.append(schedule)

        return data

    def _match_regex(self, text: str, regex: str) -> str:
        match: Match[str] | None = re.search(regex, text)

        return match.group() if match is not None else ""

    def _match_all_regex(self, text: str, regex: str) -> List[str]:
        return [entry.strip() for entry in re.findall(regex, text)]
    
    def _utc_to_local_time(self, utc_time: datetime) -> datetime:
        """Convert UTC time to local time"""
        return utc_time.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def _get_datetime_from_text(self, text: str) -> datetime:
        date_time: datetime = datetime.strptime(text, self.DATETIME_FORMAT)
        return self._utc_to_local_time(date_time)
    
    def _get_date_from_datetime(self, date_time: datetime) -> str:
        """Get the formatted date from a datetime object"""
        # Return weekday if less than a week is left
        if date_time.timestamp() - time.time() < self.WEEK_IN_SECONDS:
            return calendar.day_name[date_time.weekday()]

        return date_time.strftime("%Y-%m-%d")

    def _get_time_from_datetime(self, date_time: datetime) -> str:
        """Get the formatted time from a datetime object"""
        return date_time.strftime("%H:%M")
    
    def _get_courses_from_text(self, text: str) -> List[str]:
        """Get the course types from a string"""
        return text.split(self.COURSE_CODE_SEPARATOR)[:-1] # Remove last empty element

    
    def _fetch_from_web(self, link: str):
        """Fetch schedule data from the web"""
        try:
            return requests.get(link).content.decode(self.DATA_ENCODING)
        except Exception:
            return ""

