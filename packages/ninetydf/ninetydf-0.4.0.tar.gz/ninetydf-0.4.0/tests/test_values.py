from ninetydf import couples, seasons

SHOW_IDS = {
    "90 Day Fiancé": "90DF",
    "90 Day Fiancé: Before the 90 Days": "B90",
    "90 Day Fiancé: The Other Way": "TOW",
    "90 Day Fiancé: Happily Ever After?": "HEA",
}


def test_couple_values():
    assert couples.shape[0] == 172
    assert couples.isna().sum().sum() == 0
    assert (
        len(couples["appearance_id"]) - len(couples["appearance_id"].drop_duplicates())
        == 0
    )

    for _, couple in couples.iterrows():
        assert (
            couple["appearance_id"] == couple["couple_id"] + "_" + couple["season_id"]
        )
        assert couple["show_id"] == SHOW_IDS[couple["show_name"]]

        for column in couple.index:
            if isinstance(couple[column], str):
                assert couple[column].strip() == couple[column]


def test_season_values():
    assert seasons.shape[0] == 27
    assert seasons.isna().sum().sum() == 2
    assert len(seasons["season_id"]) - len(seasons["season_id"].drop_duplicates()) == 0

    for _, season in seasons.iterrows():
        assert season["show_id"] == SHOW_IDS[season["show_name"]]
        assert season["season_id"] == season["show_id"] + "_" + str(season["season"])

        for column in season.index:
            if isinstance(season[column], str):
                assert season[column].strip() == season[column]
