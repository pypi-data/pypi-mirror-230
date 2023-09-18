try:
    import pandas as pd
    from ninetydf import couples_df, seasons_df
    from ninetydf.data import _load_data

    def _validate_dataframe(df, expected_columns):
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        for column in expected_columns:
            assert column in df.columns

    def test_load_couples():
        _validate_dataframe(
            couples_df,
            [
                "show_id",
                "show_name",
                "season",
                "season_id",
                "couple_name",
                "couple_id",
                "appearance_id",
            ],
        )

    def test_load_seasons():
        _validate_dataframe(
            seasons_df, ["show_id", "season", "season_id", "start_date", "end_date"]
        )

    def test_load_data_function():
        df = _load_data("seasons.csv")
        _validate_dataframe(
            df, ["show_id", "season", "season_id", "start_date", "end_date"]
        )

except ImportError:
    pass
