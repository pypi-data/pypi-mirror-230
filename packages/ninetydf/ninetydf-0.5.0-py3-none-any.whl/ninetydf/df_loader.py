from io import StringIO
import pandas as pd

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files


def _load_data(filename: str) -> pd.DataFrame:
    resource_path = files("ninetydf") / filename
    with resource_path.open(encoding="utf-8") as f:
        content = f.read()
    return pd.read_csv(StringIO(content))


def load_couples_df() -> pd.DataFrame:
    return _load_data("couples.csv")


def load_seasons_df() -> pd.DataFrame:
    return _load_data("seasons.csv")
