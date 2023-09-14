from dataclasses import dataclass


@dataclass
class Schedule:
    name: str = ""
    link: str = ""

    def to_json(self) -> str:
        return f"({self.name},{self.link})"

    def from_json(self, data: str):
        self.name: str = data[1:data.find(",")]
        self.link: str = data[data.find(",") + 1:-1]
        
        return self

