from typing import List, Type, Union

from .models import Couple, Season


def _load_data(
    filename: str, dataclass: Type[Union[Couple, Season]]
) -> List[Union[Couple, Season]]:
    data_list = []

    try:
        from importlib.resources import files  # Standard Python 3.9+
    except ImportError:
        from importlib_resources import files

    resource_path = files("ninetydf") / filename
    with resource_path.open(encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        for line in f:
            row = line.strip().split(",")
            instance = dataclass(*row)
            data_list.append(instance)

    return data_list


def load_couples() -> List[Couple]:
    return _load_data("couples.csv", Couple)


def load_seasons() -> List[Season]:
    return _load_data("seasons.csv", Season)
