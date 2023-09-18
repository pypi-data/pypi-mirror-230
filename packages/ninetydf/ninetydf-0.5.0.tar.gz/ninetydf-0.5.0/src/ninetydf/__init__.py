from .csv_loader import load_couples, load_seasons

couples_list = load_couples()
seasons_list = load_seasons()

try:
    from .df_loader import load_couples_df, load_seasons_df

    couples_df = load_couples_df()
    seasons_df = load_seasons_df()
except ImportError:
    pass
