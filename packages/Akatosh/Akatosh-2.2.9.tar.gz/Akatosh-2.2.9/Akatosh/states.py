import enum


class State(str, enum.Enum):
    ENDED = "ENDED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    CANCELED = "CANCELED"
    CREATED = "CREATED"
    TERMINATED = "TERMINATED"
