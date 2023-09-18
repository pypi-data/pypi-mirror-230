from dataclasses import asdict

from ninetydf.models import Couple, Season

try:
    from ninetydf import couples_df, seasons_df

    couples = [Couple(*row) for row in couples_df.values]

    seasons_df["end_date"] = seasons_df["end_date"].fillna("")
    seasons = [Season(*row) for row in seasons_df.values]

except ImportError:
    from ninetydf import couples_list, seasons_list

    couples = couples_list
    seasons = seasons_list

SHOW_IDS = {
    "90 Day Fiancé": "90DF",
    "90 Day Fiancé: Before the 90 Days": "B90",
    "90 Day Fiancé: The Other Way": "TOW",
    "90 Day Fiancé: Happily Ever After?": "HEA",
}


def test_couple_values():
    assert len(couples) == 172

    missing_values = sum(
        1
        for couple in couples
        if any(value is None for value in asdict(couple).values())
    )
    assert missing_values == 0, "should be no missing values"

    appearance_ids = [couple.appearance_id for couple in couples]
    assert len(appearance_ids) == len(
        set(appearance_ids)
    ), "`appearance_id` should be unique"

    for couple in couples:
        assert couple.appearance_id == f"{couple.couple_id}_{couple.season_id}"
        assert couple.show_id == SHOW_IDS[couple.show_name]
        assert (
            len(couple.couple_name.split(" & ")) == 2
        ), "couple name should have `&` separator"

        for value in asdict(couple).values():
            if isinstance(value, str):
                assert (
                    value.strip() == value
                ), "values should not have trailing white space"


def test_season_values():
    assert len(seasons) == 27

    for season in seasons:
        print(season.end_date)

    missing_values = sum(
        1 for season in seasons if any(not value for value in asdict(season).values())
    )

    assert missing_values == 2, "current seasons do not have end dates"

    season_ids = [season.season_id for season in seasons]
    assert len(season_ids) == len(set(season_ids)), "`season_id` should be unique"

    for season in seasons:
        assert season.show_id == SHOW_IDS[season.show_name]
        assert season.season_id == f"{season.show_id}_{season.season}"

        for value in asdict(season).values():
            if isinstance(value, str):
                assert (
                    value.strip() == value
                ), "values should not have trailing white space"
