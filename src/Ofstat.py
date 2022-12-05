from selenium.webdriver.common.by import By
from selenium.webdriver import Keys, ActionChains
import pandas as pd
import time
import datetime
import enum

base_url ='https://ofstats.com/'
matches_url = 'https://ofstats.com/matches/view/'
seasons_url = 'https://ofstats.com/season/'

league_mapping = {
    "serie" : "france-ligue-1-",
    "liga1" : "france-ligue-1-",
    "bundesliga" : "germany-bundesliga-",
    "epl" : "england-premier-league-",
    "laliga" : "spain-la-liga-"
}

season_mapping = {
    0: "2019-2020",
    1: "2020-2021",
    2: "2021-2022",
    3: "2022-2023"
}


def enum_to_dict(enum):
    return {name: member.value for name, member in enum.__members__.items()}


class AliasesUnderstatToOfstat(enum.Enum):
    epl = {'Leeds': 'Leeds United', 'West Ham': 'West Ham United', 'Leicester': 'Leicester City', 'Norwich': 'Norwich City', 'Wolverhampton': 'Wolverhampton Wanderers', 'Tottenham': 'Tottenham Hotspur', 'Atletico Madrid': 'Atlético Madrid', 'Bayern Munchen': 'Bayern München', 'Malmo FF': 'Malmö FF', 'Besiktas': 'Beşiktaş', 'Brondby': 'Brøndby', 'Ferencvaros': 'Ferencváros', 'West Bromwich Albion': 'West Bromwich'}
    bundesliga = {'Hertha Berlin': 'Hertha BSC', 'Bayern Munich': 'Bayern Munchen', 'Borussia M.Gladbach': 'Borussia Mgladbach', 'FC Cologne': 'Koln', 'VfB Stuttgart': 'Stuttgart', 'Greuther Fuerth': 'Greuther Furth', 'RasenBallsport Leipzig': 'RB Leipzig'}
    serie = {'AC Milan': 'Milan', 'Verona': 'Hellas Verona', 'Parma Calcio 1913': 'Parma'}
    laliga = {'Alaves': 'Deportivo Alavés', 'Celta Vigo': 'Celta de Vigo', 'Cadiz': 'Cádiz', 'Atletico Madrid': 'Atlético Madrid', 'SD Huesca': 'Huesca', 'Eibar': 'SD Eibar'}
    liga1 = {'Angers': 'Angers SCO', 'Marseille': 'Olympique Marseille', 'Lyon': 'Olympique Lyonnais', 'Saint-Etienne': 'Saint Etienne', 'Clermont Foot': 'Clermont'}


def get_season(league, season):
    # ligue : String : "serie", "liga1", "bundesliga", "epl", 'laliga"
    # season: Season object
    return league_mapping[league] + season_mapping[season.value]


def get_ball_control(driver, team1, team2, date):
    # driver : selenium Webdriver Firefox
    # team1 : String
    # team2: string
    # date : String dd.mm.YYYY (16.05.2021)
    # returns  Dict(str, float)

    table = driver.find_element(By.CLASS_NAME, "row.text-center.team-stat-section")

    first_row = table.find_elements(By.CLASS_NAME, "col-lg-4")[0].find_elements(By.CLASS_NAME, "team-stat-item")[0]

    goals_team1 = float(first_row.find_element(By.CLASS_NAME, "progress-bar.progress-bar-home").text)
    goals_team2 = float(first_row.find_element(By.CLASS_NAME, "progress-bar.progress-bar-visitor").text)

    return {'team1': goals_team1,
            'team2': goals_team2
            }


def get_shots_stvor(driver, team1, team2, date):
    # driver : selenium Webdriver Firefox
    # team1 : String
    # team2: string
    # date : String dd.mm.YYYY (16.05.2021)
    # returns  Dict(str, float)

    table = driver.find_element(By.CLASS_NAME, "row.text-center.team-stat-section")

    row = table.find_elements(By.CLASS_NAME, "col-lg-4")[2].find_elements(By.CLASS_NAME, "team-stat-item")[1]

    shots_team1 = float(row.find_element(By.CLASS_NAME, "progress-bar.progress-bar-home").text)
    shots_team2 = float(row.find_element(By.CLASS_NAME, "progress-bar.progress-bar-visitor").text)

    return {'team1': shots_team1,
            'team2': shots_team2
            }


def get_shots_corner(driver, team1, team2, date):
    # driver : selenium Webdriver Firefox
    # team1 : String
    # team2: string
    # date : String dd.mm.YYYY (16.05.2021)
    # returns  Dict(str, float)

    table = driver.find_element(By.CLASS_NAME, "row.text-center.team-stat-section")

    row = table.find_elements(By.CLASS_NAME, "col-lg-4")[0].find_elements(By.CLASS_NAME, "team-stat-item")[2]

    shots_team1 = float(row.find_element(By.CLASS_NAME, "progress-bar.progress-bar-home").text)
    shots_team2 = float(row.find_element(By.CLASS_NAME, "progress-bar.progress-bar-visitor").text)

    return {'team1': shots_team1,
            'team2': shots_team2
            }


def get_scr(driver, team1, team2, date):
    # driver : selenium Webdriver Firefox
    # team1 : String
    # team2: string
    # date : String dd.mm.YYYY (16.05.2021)
    # returns  Dict(str, float)

    table = driver.find_element(By.CLASS_NAME, "row.text-center.team-stat-section")

    bad_shots = table.find_elements(By.CLASS_NAME, "col-lg-4")[1].find_elements(By.CLASS_NAME, "team-stat-item")[1]
    goals = table.find_elements(By.CLASS_NAME, "col-lg-4")[0].find_elements(By.CLASS_NAME, "team-stat-item")[3]

    shots_team1 = float(bad_shots.find_element(By.CLASS_NAME, "progress-bar.progress-bar-home").text)
    shots_team2 = float(bad_shots.find_element(By.CLASS_NAME, "progress-bar.progress-bar-visitor").text)

    goals_team1 = float(goals.find_element(By.CLASS_NAME, "progress-bar.progress-bar-home").text)
    goals_team2 = float(goals.find_element(By.CLASS_NAME, "progress-bar.progress-bar-visitor").text)

    try:
        scr_team1 = goals_team1 / (shots_team1 + goals_team1)
    except ZeroDivisionError:
        scr_team1 = 0

    try:
        scr_team2 = goals_team2 / (shots_team2 + goals_team2)
    except ZeroDivisionError:
        scr_team2 = 0

    return {'team1': scr_team1,
            'team2': scr_team2
            }


def get_season_matches(driver, ligue, season):
    # driver : selenium webdriver
    # season : Season object enum, name _YY_YY_, value int 0-3
    # returns pandas dataframe

    season = get_season(ligue, season)

    columns = ["Date", "Host", "Result", "Guest", "Status", "Season"]
    temp_table = pd.DataFrame(columns=columns)
    driver.get(seasons_url + season)
    time.sleep(3)
    clickable = driver.find_element(By.XPATH, '//*[@href="#nav-matches"]')
    ActionChains(driver).click(clickable).perform()

    time.sleep(3)
    matches_table = driver.find_element(By.ID, "nav-matches").find_element(By.TAG_NAME, 'table')
    time.sleep(3)
    table_bodies = matches_table.find_elements(By.TAG_NAME, 'tbody')
    for tbody in table_bodies:
        trs = tbody.find_elements(By.TAG_NAME, 'tr')
        for tr in trs:
            match = dict(zip(columns,
                             tr.text.split('\n')))
            match['Season'] = season
            temp_table = temp_table.append(match, ignore_index=True)
    return temp_table


def get_matches_statistics(driver, temp_table, matches_url):
    # driver : selenium webdriver
    # temp_table : pandas dataframe
    # returns pandas dataframe

    for index, row in temp_table[:].iterrows():
        team1 = '-'.join(row['Host'].lower().split())
        team2 = '-'.join(row['Guest'].lower().split())
        date_formatted = f"{datetime.datetime.strptime(row['Date'], '%d.%m.%Y'):%Y-%m-%d}"
        driver.get(f'{matches_url}{team1.lower()}-{team2.lower()}-{date_formatted}')

        time.sleep(3)
        clickable = driver.find_element(By.XPATH, f'//*[@href="/matches/statistics/{team1}-{team2}-{date_formatted}"]')
        ActionChains(driver).click(clickable).perform()
        time.sleep(3)

        stvor = get_shots_stvor(driver, row['Host'], row['Guest'], row['Date'])
        print(index, 'Stvor:', stvor['team1'], stvor['team2'], row['Host'], row['Guest'])
        temp_table.loc[index, 'Host: Average shots stvor'] = stvor['team1']
        temp_table.loc[index, 'Guest: Average shots stvor'] = stvor['team2']

        corner = get_shots_corner(driver, row['Host'], row['Guest'], row['Date'])
        print(index, 'Corner:', corner['team1'], corner['team2'], row['Host'], row['Guest'])
        temp_table.loc[index, 'Host: Average corner situation'] = corner['team1']
        temp_table.loc[index, 'Guest: Average corner situation'] = corner['team2']

        scr = get_scr(driver, row['Host'], row['Guest'], row['Date'])
        print(index, 'Scr:', scr['team1'], scr['team2'], row['Host'], row['Guest'])
        temp_table.loc[index, 'Host: SCR'] = scr['team1']
        temp_table.loc[index, 'Guest: SCR'] = scr['team2']

        ball_control = get_ball_control(driver, row['Host'], row['Guest'], row['Date'])
        print(index, 'Ball control:', ball_control['team1'], ball_control['team2'], row['Host'], row['Guest'])
        temp_table.loc[index, 'Host: Ball control'] = ball_control['team1']
        temp_table.loc[index, 'Guest: Ball control'] = ball_control['team2']

    return temp_table
