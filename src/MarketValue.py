import time
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
import enum
from src import Ofstat
import pandas as pd
from src.Season import Season

market_value_url = 'https://www.transfermarkt.com/'


class AliasesOfstatToMarket(enum.Enum):
    serie = {"Sampdoria": "UC Sampdoria", "Juventus": "Juventus FC", "Milan": "AC Milan", "Lazio": "SS Lazio",
             "Atalanta": "Atalanta BC", "Salernitana": "US Salernitana 1919", "Torino": "Torino FC",
             "Spezia": "Spezia Calcio", "Venezia": "Venezia FC", "Sassuolo": "US Sassuolo",
             "Inter": "Inter Milan", "Genoa": "Genoa CFC", "Udinese": "Udinese Calcio",
             "Bologna": "Bologna FC 1909", "Cagliari": "Cagliari Calcio", "Empoli": "FC Empoli",
             "Napoli": "SSC Napoli", "Roma": "AS Roma", "Fiorentina": "ACF Fiorentina", "Parma": "Parma Calcio 1913",
             "Crotone": "FC Crotone", "Benevento": "Benevento Calcio", "Brescia": "Brescia Calcio", "Lecce": "US Lecce"}

    laliga = {"Athletic Club": "Athletic Bilbao", "Espanyol": "RCD Espanyol Barcelona",
              "Deportivo Alavés": "Deportivo Alaves", "Cádiz": "Cadiz", "Atlético Madrid": "Atletico Madrid"}

    liga1 = {"Lille": "LOSC Lille", "Lorient": "FC Lorient", "Nice": "OGC Nice",
             "Paris Saint Germain": "Paris Saint-Germain", "Metz": "FC Metz", "Clermont": "Clermont Foot 63",
             "Nantes": "FC Nantes", "Olympique Lyonnais": "Olympique Lyon", "Bordeaux": "FC Girondins Bordeaux",
             "Rennes": "Stade Rennais FC", "Brest": "Stade Brestois 29", "Reims": "Stade Reims",
             "Monaco": "AS Monaco", "Montpellier": "Montpellier HSC", "Troyes": "ESTAC Troyes",
             "Strasbourg": "RC Strasbourg Alsace", "Lens": "RC Lens", "Saint Etienne": "AS Saint-Étienne",
             "Dijon": "Dijon FCO", "Nimes": "Nîmes Olympique"
             }

    bundesliga = {'Sevilla': 'Sevilla FC', "Barcelona": "FC Barcelona", "Getafe": "Getafe CF",
                  "Villarreal": "Villarreal CF",
                  "Real Betis": "Real Betis Balompié", "Levante": "Levante UD", "Granada": "Granada CF",
                  "Osasuna": "CA Osasuna", "Valencia": "Valencia CF", "Elche": "Elche CF",
                  "Atlético Madrid": "Atlético de Madrid", "Sevilla FC FC": "Sevilla FC",
                  "Mallorca": "RCD Mallorca", "Cádiz": "Cádiz CF",
                  "Brest": "Stade Brestois 29", "Clermont": "Clermont Foot 63", "Lille": "LOSC Lille",
                  "Lorient": "FC Lorient", "Nantes": "FC Nantes", "Reims": "Stade Reims",
                  "Strasbourg": "RC Strasbourg Alsace",
                  "Rennes": "Stade Rennais FC", "Lens": "RC Lens", "Monaco": "AS Monaco",
                  "Troyes": "ESTAC Troyes", "Nice": "OGC Nice", "Olympique Lyonnais": "Olympique Lyon",
                  "Montpellier": "Montpellier HSC", "Paris Saint Germain": "Paris Saint-Germain",
                  "Saint-Étienne": "AS Saint-Étienne", "Metz": "FC Metz",
                  "Greuther Furth": "SpVgg Greuther Fürth",
                  "Stuttgart": "VfB Stuttgart", "Freiburg": "SC Freiburg", "Hoffenheim": "TSG 1899 Hoffenheim",
                  "Union Berlin": "1.FC Union Berlin", "Borussia Mgladbach": "Borussia Mönchengladbach",
                  "Bayer Leverkusen": "Bayer 04 Leverkusen", "Mainz 05": "1.FSV Mainz 05",
                  "Bochum": "VfL Bochum", "Wolfsburg": "VfL Wolfsburg",
                  "Koln": "1. FC Köln", "Bayern Munchen": "Bayern Munich", "Augsburg": "FC Augsburg",
                  "Real Valladolid": "Real Valladolid CF", "Athletic Club": "Atlético de Madrid", "Huesca": "SD Huesca",
                  "Schalke 04": "FC Schalke 04", "Werder Bremen": "SV Werder Bremen"}

    epl = {"Arsenal": "Arsenal FC", "Burnley": "Burnley FC",
           "Chelsea": "Chelsea FC", "Brighton": "Brighton & Hove Albion", "Brentford": "Brentford FC",
           "Watford": "Watford FC", "Bournemouth" : "AFC Bournemouth",
           "Southampton": "Southampton FC", "Liverpool": "Liverpool FC", "Everton": "Everton FC", "Fulham": "Fulham FC",
           "West Bromwich": "West Bromwich Albion"}


# aliases_mapping = league_mapping = {
#     "serie": aliases_market_seria_a,
#     "liga1": aliases_market_ligue_1,
#     "bundesliga": aliases_market_bundesliga,
#     "epl": aliases_market_epl,
#     "laliga": aliases_market_la_liga
# }


def enum_to_dict(enum):
    return {name: member.value for name, member in enum.__members__.items()}


class Ligas(enum.Enum):
    epl = {'string': 'premier-league', 'tag': 'GB1'}
    laliga = {'string': 'laliga', 'tag': 'ES1'}
    bundesliga = {'string': 'bundesliga', 'tag': 'L1'}
    liga1 = {'string': 'ligue-1', 'tag': 'FR1'}
    serie = {'string': 'serie-a', 'tag': 'IT1'}


def get_liga(liga):
    for name, member in Ligas.__members__.items():
        if name == liga:
            return member.value
    raise ValueError('Liga not found')


def get_market_teams_value(driver, liga, team, season):
    # driver : selenium webdriver
    # liga : Dict(String liga_name, String liga_code), example: {'string' : 'premier-league', 'tag' : 'GB1'}
    # team : String
    # season : String
    # returns String

    driver.get(market_value_url + liga['string'] + f'/startseite/wettbewerb/{liga["tag"]}/plus/?saison_id={season}')
    time.sleep(1)
    element = driver.find_element(By.XPATH, f'//*/table/tbody/tr/td[@class="rechts"]/a[@title="{team}"]')
    return element.text


def get_season_market_value(driver, temp_table, liga, season):
    # driver : selenium webdriver
    # temp_table : pandas dataframe
    # liga : Dict(String liga_name, String liga_code), example: {'string' : 'premier-league', 'tag' : 'GB1'}
    # season : String
    # returns pandas dataframe

    liga = get_liga(liga)
    market_value = {}
    unique_teams_hosts = list(temp_table['Host'].value_counts().index)
    unique_teams_guests = list(temp_table['Guest'].value_counts().index)
    overall_teams = pd.Series(list(set(unique_teams_hosts + unique_teams_guests)))

    for team in overall_teams:
        try:
            team_market_value = get_market_teams_value(driver, liga, team, season)
            market_value[team] = team_market_value
        except:
            print('Error:', team)

    return market_value


def get_market_value_with_alias(temp_table, driver, liga, season, aliases={}):
    # создаем копию, чтобы сохранить исходные названия команд
    # season_value : int, value of Season enum objecy
    temp_table_market = temp_table.copy()

    if isinstance(aliases, enum.EnumMeta):
        aliases = enum_to_dict(aliases)[liga]

    season = int(Ofstat.season_mapping[season.value].split('-')[0])

    temp_table_market['Host'] = temp_table_market["Host"].replace(aliases, regex=True)
    temp_table_market['Guest'] = temp_table_market['Guest'].replace(aliases, regex=True)

    market_value = get_season_market_value(driver, temp_table_market, liga, season)

    for index, row in temp_table_market.iterrows():
        try:
            temp_table.loc[index, 'Host: current season market value'] = market_value[row['Host']]
            temp_table.loc[index, 'Guest: current season market value'] = market_value[row['Guest']]
        except:
            pass

    return temp_table
