import sys
import time
from typing import List
from .cache import Cache
from .schedule import Schedule
from .data_fetcher import DataFetcher, ScheduleData


class Scheduler:
    USE_WHITELIST: bool = False 
    COMMAND_NAME: str = "liusch"


    def __init__(self) -> None:
        self.cache: Cache = Cache()
        self.data_fetcher: DataFetcher = DataFetcher()
            
    def get_next_entry(self) -> str:
        """Get the next calendar entry"""
        data: List[ScheduleData] = self.data_fetcher.get_data(self.cache.get_schedules())

        entry: ScheduleData | None = self._get_next_entry(data)

        if entry is None:
            return ""

        course_code: str = entry.course_codes[0]

        if self.USE_WHITELIST:
            course_code: str = self._get_whitelisted_course(entry.course_codes)

        if not course_code:
            return ""

        return f"{entry.start_date} | {entry.start_time}-{entry.end_time} | {course_code} | {entry.course_type} | {entry.locations[0] if entry.locations else ''}"

    def parse_args(self, argv: List[str]) -> None:
        # Exit if there are no arguments
        if len(argv) <= 1:
            print(self.get_next_entry())
            return

        match argv[1]:
            case "--add-schedule" | "-a":
                self._add_schedule(argv[2:])
            case "--add-course" | "-aw":
                self._add_courses(argv[2:])
            case "--remove-schedule" | "-rm":
                self._remove_schedule(argv[2:])
            case "--remove-course" | "-rmw":
                self._remove_courses(argv[2:])
            case "--list-schedules" | "-ls":
                self._list_schedules()
            case "--list-courses" | "-lsw":
                print(self.cache.get_courses())
            case "--help" | "-h":
                self._display_help()
            case _:
                print(f"{argv[1]} is not a valid argument. Try -h for help.")

    def _add_schedule(self, schedules: List[str]) -> None:
        if not len(schedules) % 2 == 0:
            print("Names and links do not match.")
            return

        for i in range(0, len(schedules), 2):
            name: str = schedules[i]
            link: str = schedules[i + 1]

            self.cache.add_schedule(name, link)

    def _add_courses(self, courses: List[str]) -> None:
        for course in courses:
            self.cache.add_course(course)

    def _remove_schedule(self, schedules: List[str]) -> None:
        for schedule in schedules:
            name: str = schedule

            self.cache.remove_schedule(name)

    def _remove_courses(self, courses: List[str]) -> None:
        for course in courses:
            self.cache.remove_course(course)

    def _list_schedules(self) -> None:
        for schedule in self.cache.get_schedules():
            print("{:<24} {}".format(schedule.name, schedule.link))

    def _get_whitelisted_course(self, courses: List[str]) -> str:
        """Get the course that's in the whitelist from a list of courses"""
        whitelist: List[str] = self.cache.get_courses()

        for course in courses:
            print(f"{course} in {whitelist}")
            if course in whitelist:
                return course

        return ""

    def _get_next_entry(self, data: List[ScheduleData]) -> ScheduleData | None:
        """Get the next relevant entry"""
        for schedule in data:
            if schedule.end_unix >= time.time():
                return schedule

        return None
    
    def _display_help(self) -> None:
        self._print_bold("USAGE")
        print(f"    {self.COMMAND_NAME} [-a 'name' 'link' ...] [-aw 'course' ...] [-rm 'name' ...] [-rmw 'course' ...] [-ls] [-lsw] [-h]")

        self._print_bold("\nOPTIONS")

        self._print_bold("   -a, --add-schedule 'name' 'link'")
        print("        Add a new schedule with a name and a TimeEdit link.\n")

        self._print_bold("   -aw, --add-course 'course'")
        print("        Add a course code to the whitelist. If a schedule entry has several codes \n        the whitelisted one will be displayed.\n")

        self._print_bold("   -rm, --remove-schedule 'name'")
        print("        Remove a schedule entry given it's name.\n")

        self._print_bold("   -rmw, --remove-course 'course'")
        print("        Remove a whitelisted course given it's course code.\n")

        self._print_bold("   -ls, --list-schedules")
        print("        Display all loaded shedules.\n")

        self._print_bold("   -lsw, --list-courses")
        print("        Display all whitelisted course codes.\n")

        self._print_bold("   -h, --help")
        print("        Display this help message.")

    def _print_bold(self, text: str) -> None:
        print(f"\033[1m{text}\033[0m")


def main() -> None:
    scheduler: Scheduler = Scheduler()
    scheduler.parse_args(sys.argv)


if __name__ == "__main__":
    main()

