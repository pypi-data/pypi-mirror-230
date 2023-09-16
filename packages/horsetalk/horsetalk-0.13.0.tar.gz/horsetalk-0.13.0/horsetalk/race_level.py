from .race_class import RaceClass
from .race_grade import RaceGrade


class RaceLevel:
    def __init__(self, value: RaceGrade | RaceClass):
        if isinstance(value, RaceClass) and value.value == 1:
            raise ValueError("Class 1 race needs a specified grade")

        self.grade = value if isinstance(value, RaceGrade) else RaceGrade(None)
        self.class_ = value if isinstance(value, RaceClass) else RaceClass(1)

    def __str__(self):
        return f"({self.class_.value}) {self.grade if self.grade.value else ''}".strip()

    def __eq__(self, other):
        return self.grade == other.grade and self.class_ == other.class_

    def __gt__(self, other):
        return self.grade > other.grade or self.class_ > other.class_

    def __lt__(self, other):
        return self.grade < other.grade or self.class_ < other.class_
