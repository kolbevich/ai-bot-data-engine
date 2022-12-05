import enum
import pandas as pd
from src import Season
from datetime import datetime


def enum_to_dict(enum):
    return {name: member.value for name, member in enum.__members__.items()}


class AliasesOfstatToUnderstat(enum.Enum):
    epl = {'Leeds United': 'Leeds', 'West Ham United': 'West Ham', 'Leicester City': 'Leicester',
           "Norwich City": "Norwich", "Wolverhampton": "Wolverhampton Wanderers", "Tottenham Hotspur": "Tottenham",
           'Atlético Madrid': 'Atletico Madrid', "Bayern München": "Bayern Munchen", "Malmö FF": "Malmo FF",
           "Beşiktaş": "Besiktas", "Brøndby": "Brondby", "Ferencváros": "Ferencvaros",
           "West Bromwich": "West Bromwich Albion", "Wolverhampton Wanderers Wanderers": "Wolverhampton Wanderers"}

    bundesliga = {"Hertha BSC": "Hertha Berlin", "Bayern Munchen": "Bayern Munich",
                  "Borussia Mgladbach": "Borussia M.Gladbach",
                  "Koln": "FC Cologne", "Stuttgart": "VfB Stuttgart", "Greuther Furth": "Greuther Fuerth",
                  "RB Leipzig": "RasenBallsport Leipzig"}
    serie = {"Milan": "AC Milan", "Hellas Verona": "Verona", "Parma": "Parma Calcio 1913"}

    laliga = {"Deportivo Alavés": "Alaves", "Celta de Vigo": "Celta Vigo", "Cádiz": "Cadiz",
              "Atlético Madrid": "Atletico Madrid", "Huesca": "SD Huesca", "SD Eibar": "Eibar",
              }

    liga1 = {"Angers SCO": "Angers", "Olympique Marseille": "Marseille", "Olympique Lyonnais": "Lyon",
             "Saint Etienne": "Saint-Etienne", "Clermont": "Clermont Foot"}


class Ligas(enum.Enum):
    epl = 'EPL'
    laliga = 'La_liga'
    bundesliga = 'Bundesliga'
    liga1 = 'Ligue_1'
    serie = 'Serie_A'


def get_liga(liga):
    for name, member in Ligas.__members__.items():
        if name == liga:
            return member.value
    raise ValueError('Liga not found')


def trim_async_table(table):
    table = pd.DataFrame(table)
    cols = table.loc[0]
    table.columns = cols
    league_table = table[1:]
    return league_table


def table_team_filter(league_table, team):
    return league_table[league_table['Team'] == team]


def get_goals_average(prematch_stats):
    # prepmatch_stats : filtered pandas dataframe

    try:
        for index, match in prematch_stats.iterrows():
            side = match['side']
        goals_sum = sum([int(match['goals'][match['side']]) for index, match in prematch_stats.iterrows()])
        if len(prematch_stats) == 0:
            return 0
        else:
            return goals_sum / len(prematch_stats)
    except IndexError:
        print('No info on match')


def get_goals_against_average(prematch_stats):
    # prepmatch_stats : filtered pandas dataframe

    ga_sum = 0
    try:
        if len(prematch_stats) == 0:
            return 0
        else:
            for index, match in prematch_stats.iterrows():
                if match['side'] == 'h':
                    ga_sum += float(match['goals']['a'])
                else:
                    ga_sum += float(match['goals']['h'])
            return ga_sum / len(prematch_stats)
    except IndexError:
        print('No info on match')


def get_matches_played(prematch_stats):
    # prepmatch_stats : filtered pandas dataframe
    return len(prematch_stats)


def days_since_last_match(match_date, prematch_stats):
    # prepmatch_stats : filtered pandas dataframe
    # match_date : string, %d.%m.%Y
    try:
        last_match_datetime = prematch_stats[-1:]['datetime'].values[0]  # 2022-05-22 15:00:00
        last_match_datetime = datetime.strptime(last_match_datetime, "%Y-%m-%d %H:%M:%S").date()
        print(f'Last match played {prematch_stats[-1:]["a"].values[0]["title"]} against {prematch_stats[-1:]["h"].values[0]["title"]} on {prematch_stats[-1:]["datetime"].values[0]}')
        timeDif = (match_date.date() - last_match_datetime)
        return timeDif.days
    except IndexError:
        print('No info on match')


def get_g_ga_delta(prematch_stats):
    # prepmatch_stats : filtered pandas dataframe

    try:
        g = sum([int(match['goals'][match['side']]) for index, match in prematch_stats.iterrows()])
        ga = 0
        for index, match in prematch_stats.iterrows():
            side_against = 'h' if match['side'] == 'a' else 'a'
            ga += int(match["goals"][side_against])
        return g - ga
    except IndexError:
        print('No info on match')


def get_xg_average(prematch_stats):
    # prepmatch_stats : filtered pandas dataframe

    ga_sum = 0
    try:
        if len(prematch_stats) == 0:
            return 0
        else:
            for index, match in prematch_stats.iterrows():
                if match['side'] == 'h':
                    ga_sum += float(match['xG']['a'])
                else:
                    ga_sum += float(match['xG']['h'])
            return ga_sum / len(prematch_stats)
    except IndexError:
        print('No info on match')


def get_team_prematch_stats(team, team_stats, team_upcoming, match_date, is_future=False):  # format '2021-11-06'
    # team : string
    # team_stats : pandas dataframe, all team's matches

    match_date_formatted = datetime.strptime(match_date, '%d.%m.%Y')

    prematch_stats = team_stats[
        pd.Series(datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in team_stats['datetime']) < match_date_formatted]

    if is_future:
        prematch_from_future = team_upcoming[
            pd.Series(datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in team_upcoming['datetime']) < match_date_formatted]
        prematch_stats_with_upcoming = prematch_stats.append(prematch_from_future).sort_values('datetime')

    final_prematch_stats = {'Team: G average this season': get_goals_average(prematch_stats),
                            'Team: GA average this season': get_goals_against_average(prematch_stats),
                            'Team: matches played this season': get_matches_played(prematch_stats),
                            'Team: days since last match': days_since_last_match(match_date_formatted, prematch_stats_with_upcoming),
                            'Team: G/GA delta this season': get_g_ga_delta(prematch_stats),
                            'Team: xG average this season': get_xg_average(prematch_stats)
                            }

    return final_prematch_stats


def get_team_stats_ondate(league_stats, team):
    team_stats = league_stats[league_stats['Team'] == team]
    result = {}
    for c in team_stats.columns:
        result[c] = team_stats[c].values[0]
    return result


def get_season_h2h(host_stats_season, guest_team):
    h2h = []
    for index, row in host_stats_season.iterrows():
        side = row['side']
        if side == 'a':
            opposite_side = 'h'
        else:
            opposite_side = 'a'
        if row[opposite_side]['title'] == guest_team:
            h2h.append({'target team': row[side]['title'],
                        'opposite team': row[opposite_side]['title'],
                        'date': row['datetime'],
                        'target team goals': float(row['goals'][side]),
                        'target team xG': float(row['xG'][side]),
                        'opposite team goals': float(row['goals'][opposite_side]),
                        'opposite team xG': float(row['xG'][opposite_side])})
    return h2h


def get_h2h_table(host_stats_20_21, host_stats_19_20, host_stats_18_19):
    h2h = []
    h2h_20_21 = get_season_h2h(host_stats_20_21, 'Everton')
    h2h_19_20 = get_season_h2h(host_stats_19_20, 'Everton')
    h2h_18_19 = get_season_h2h(host_stats_18_19, 'Everton')

    h2h = h2h_20_21 + h2h_19_20 + h2h_18_19

    return h2h

def reformat(date):
    return '-'.join(date.split('.')[::-1])


