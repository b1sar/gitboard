from typing import TypedDict

class Navigation(TypedDict):
    prev: str
    next: str
    last: str
    first: str
    last_page: int