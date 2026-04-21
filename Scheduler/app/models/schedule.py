from dataclasses import dataclass

@dataclass
class Lesson:
    time: str
    subject: str

@dataclass
class Schedule:
    date: str
    lessons: list[Lesson]