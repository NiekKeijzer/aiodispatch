import enum


class Route(enum.Enum):
    TASKS = "TASKS"

    def __str__(self) -> str:
        return str(self.value)
