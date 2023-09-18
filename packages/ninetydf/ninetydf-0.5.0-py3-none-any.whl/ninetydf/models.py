from dataclasses import dataclass


@dataclass
class Couple:
    show_id: str
    show_name: str
    season: int
    season_id: str
    couple_name: str
    couple_id: str
    appearance_id: str


@dataclass
class Season:
    show_id: str
    show_name: str
    season: int
    season_id: str
    start_date: str
    end_date: str = ""
