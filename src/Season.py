import enum


class Season(enum.Enum):
    _19_20 = 0
    _20_21 = 1
    _21_22 = 2
    _22_23 = 3


season_mapping = {
    "2022-2023": 3,
    "2021-2022": 2,
    "2020-2021": 1,
    "2019-2020": 0,
    "2018-2019": -1,
    "2017-2019": -2,
    "2016-2017": -3
}


def get_season(season):
    # season : String : "2020-2021"
    # returns Season object

    season_num = season_mapping[season]
    for name, member in Season.__members__.items():
        if member.value == season_num:
            return member
    raise ValueError("Season not found")
