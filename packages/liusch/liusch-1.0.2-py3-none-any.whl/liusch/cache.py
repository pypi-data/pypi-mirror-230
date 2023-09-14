from __future__ import annotations
import os
import json
from typing import List
from .schedule import Schedule

    
class Cache:
    DIR_NAME: str = "python-liu-schedule"
    SCHEDULES_FILE: str = "schedules.json"
    COURSES_FILE: str = "course_whitelist.json"


    def __init__(self) -> None:
        self._dir: str = self._init_cache_dir()
        self._schedules: str = os.path.join(self._dir, self.SCHEDULES_FILE)
        self._courses: str = os.path.join(self._dir, self.COURSES_FILE)


    def add_schedule(self, name: str, link: str) -> None:
        data: List[Schedule] = self._read_schedules()
        data.append(Schedule(name, link))
        self._write_schedules(data)

    def add_course(self, course: str) -> None:
        """Add a course to the whitelist"""
        data: List[str] = self._read_courses()

        if course not in data:
            data.append(course)

        self._write_courses(data)

    def remove_schedule(self, name: str) -> None:
        schedules: List[Schedule] = [s for s in self._read_schedules() if not s.name == name]
        self._write_schedules(schedules)

    def remove_course(self, name: str) -> None:
        courses: List[str] = [c for c in self._read_courses() if not c == name]
        self._write_courses(courses)

    def get_schedules(self) -> List[Schedule]:
        return self._read_schedules()

    def get_courses(self) -> List[str]:
        return self._read_courses()

    def _read_schedules(self) -> List[Schedule]:
        return [Schedule().from_json(schedule) for schedule in self._read_json(self._schedules)]

    def _read_courses(self) -> List[str]:
        return self._read_json(self._courses)

    def _read_json(self, file_path: str) -> List[str]:
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_schedules(self, schedule_links: List[Schedule]) -> None:
        with open(self._schedules, "w") as file:
            json.dump(schedule_links, file, default=lambda o: o.to_json())

    def _write_courses(self, courses: List[str]) -> None:
        with open(self._courses, "w") as file:
            json.dump(courses, file)

    def _init_cache_dir(self) -> str:
        # Get the home catalogue path
        home: str | None = os.getenv("HOME", os.getenv("USERPROFILE"))

        if home is None:
            raise FileNotFoundError("Home catalogue could not be found.")

        # Get the cache directory path
        cache_dir: str = os.getenv("XDG_CACHE_HOME", os.path.join(home, ".cache"))

        if cache_dir is None:
            raise FileNotFoundError("Cache directory could not be found.")

        cache_dir: str = os.path.join(cache_dir, self.DIR_NAME)
        
        # Create the directory if it does not exist
        os.makedirs(cache_dir, exist_ok=True)

        return cache_dir

