from ninetydf.csv_loader import load_couples, load_seasons
from ninetydf.models import Couple, Season


def test_load_couples():
    couples = load_couples()
    assert isinstance(couples, list)
    assert len(couples) > 0
    assert isinstance(couples[0], Couple)
    assert hasattr(couples[0], "show_id")
    assert hasattr(couples[0], "show_name")
    assert hasattr(couples[0], "season")
    assert hasattr(couples[0], "season_id")
    assert hasattr(couples[0], "couple_name")
    assert hasattr(couples[0], "couple_id")
    assert hasattr(couples[0], "appearance_id")


def test_load_seasons():
    seasons = load_seasons()
    assert isinstance(seasons, list)
    assert len(seasons) > 0
    assert isinstance(seasons[0], Season)
    assert hasattr(seasons[0], "show_id")
    assert hasattr(seasons[0], "season")
    assert hasattr(seasons[0], "season_id")
    assert hasattr(seasons[0], "start_date")
    assert hasattr(seasons[0], "end_date")
