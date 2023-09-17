from .racing_code import RacingCode


class RaceGrade:
    def __init__(
        self, grade: str | int | None, racing_code: RacingCode = RacingCode.FLAT
    ):
        if grade and str(grade).isdigit() and not 1 <= int(grade) < 4:
            raise ValueError(f"Grade must be between 1 and 3, not {grade}")

        if grade and not str(grade).isdigit() and grade != "Listed":
            raise ValueError(f"Grade must be a number or 'Listed', not {grade}")

        self.value = str(grade) if grade else None
        self.racing_code = racing_code

    def __repr__(self):
        return f"<RaceGrade: {self.value}>"

    def __str__(self):
        if not self.value:
            return ""

        title = "Grade" if self.racing_code == RacingCode.NATIONAL_HUNT else "Group"
        return "Listed" if not self.value.isdigit() else f"{title} {self.value}"

    def __bool__(self):
        return bool(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        if not self.value:
            return other.value

        if not self.value.isdigit():
            return other.value.isdigit()

        return other.value.isdigit() and self.value > other.value

    def __gt__(self, other):
        if not self.value:
            return False

        return self.value.isdigit() and (
            not other.value or not other.value.isdigit() or self.value < other.value
        )
